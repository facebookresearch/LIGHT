#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import os
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import load_db_and_process_config
from mephisto.abstractions.blueprints.parlai_chat.parlai_chat_blueprint import (
    BLUEPRINT_TYPE,
    SharedParlAITaskState,
)

from light.graph.builders.one_room_builder import OneRoomChatBuilder
from light.data_model.light_database import LIGHTDatabase
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
import hydra
from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import List, Any

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LIGHT_DB_PATH = "~/ParlAI/data/LIGHT/merged.db"

hydra_defaults = [
    {"mephisto/blueprint": BLUEPRINT_TYPE},
    {"mephisto/architect": "local"},
    {"mephisto/provider": "mock"},
    {"conf": "multi_chat"},
]

from mephisto.operations.hydra_config import RunScriptConfig, register_script_config

@dataclass
class ScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: hydra_defaults)
    task_dir: str = TASK_DIRECTORY
    num_turns: int = field(
        default=8,
        metadata={
            "help": "Number of min turns per worker before a conversation is complete"
        },
    )
    turn_timeout: int = field(
        default=180,
        metadata={
            "help": "Maximum response time before kicking "
            "a worker out, default 180 seconds"
        },
    )
    qualify_new_workers: bool = False


register_script_config(name="scriptconfig", module=ScriptConfig)


def make_unit_validator(db, block_qual):
    MIN_AVG_MESSAGE_LENGTH = 7 # 7 words should be easily achievable
    SPAM_MESSAGE_TIMEOUT = 3 # Responding within 3 seconds of own message is likely spam
    SPAM_MESSAGE_FORGIVENESS = 0.25 # If less than a quarter are spam, we don't penalize
    TOO_LONG_TIME = 90 # Taking 2 minutes own messages is getting a bit long
    LONG_MESSAGE_FORGIVENESS = 0.40 # So long as less than 40% are too long, we forgive
    MAX_REPEAT_MESSAGE_PROPORTION = 0.30 # most messages should respond to others

     # Heuristic functions - return true if there's a possible red flag
    # for the given worker
    def too_long_between_messages(m_info):
        time_exceeds_cap = [m['d_last_self'] > TOO_LONG_TIME for m in m_info]
        exceed_cap_count = len([x for x in time_exceeds_cap if x])
        exceed_cap_prop = exceed_cap_count / len(m_info)
        return exceed_cap_prop > LONG_MESSAGE_FORGIVENESS
        
    def too_short_between_messages(m_info):
        time_below_min = [m['d_last_self'] < SPAM_MESSAGE_TIMEOUT for m in m_info]
        below_min_count = len([x for x in time_below_min if x])
        below_min_prop = below_min_count / len(m_info)
        return below_min_prop > SPAM_MESSAGE_FORGIVENESS

    def messages_too_short(m_info):
        """Check to find out the average message lengths"""
        message_lengths = [len(m['text'].strip().split()) for m in m_info]
        avg_len = sum(message_lengths) / len(message_lengths)
        return avg_len < MIN_AVG_MESSAGE_LENGTH

    def too_many_repeated(m_info):
        repeat_count = len([m for m in m_info if m['last_is_self']])
        repeat_prop = repeat_count / len(m_info)
        return repeat_prop > MAX_REPEAT_MESSAGE_PROPORTION


    mephisto_data_browser = MephistoDataBrowser(db=db)

    def validate_unit(unit):
        if unit.get_assigned_agent() is None:
            return

        output = mephisto_data_browser.get_data_from_unit(unit)["data"]

        if output is None:
            return

        messages = output['messages']
        agent_name = output['agent_name']

        message_info = []
        for idx in range(len(messages)):
            m = messages[idx]
            if m['id'] == agent_name:
                last_timestamp = messages[idx-1]['timestamp']
                last_self_timestamp = last_timestamp if len(message_info) == 0 else message_info[-1]['timestamp']
                last_is_self = messages[idx-1]['id'] == agent_name
                timestamp = m['timestamp']
                message_info.append({
                    'timestamp': timestamp,
                    'd_last_self': timestamp - last_self_timestamp,
                    'd_last_message': timestamp - last_timestamp,
                    'last_is_self': last_is_self,
                    'text': m['text'],
                })

        valids = [
            too_long_between_messages(message_info),
            too_short_between_messages(message_info),
            messages_too_short(message_info),
            too_many_repeated(message_info),
        ]
        if any(valids):
            print(f"VALID FAIL {message_info}\nMessages  was not validated: {valids}")
            # unit.get_assigned_agent().soft_reject_work() => must wait for async version
            worker = unit.get_assigned_agent().get_worker()
            worker.grant_qualification(block_qual, 1)
        return

    return validate_unit


@hydra.main(config_path="hydra_configs", config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    db, cfg = load_db_and_process_config(cfg)
    ldb = LIGHTDatabase(LIGHT_DB_PATH)

    world_opt = {
        "num_turns": cfg.num_turns,
        "turn_timeout": cfg.turn_timeout,
        "builder": OneRoomChatBuilder(
            ldb=ldb,
            opt={
                "db_path": LIGHT_DB_PATH,
                "model_path": "/checkpoint/light/models",
                "suggestion_type": "hybrid",
                "hybridity_prob": 0.2,
            },
        ),
    }

    custom_bundle_path = cfg.mephisto.blueprint.get("custom_source_bundle", None)
    if custom_bundle_path is not None:
        assert os.path.exists(custom_bundle_path), (
            "Must build the custom bundle with `npm install; npm run dev` from within "
            f"the {TASK_DIRECTORY}/webapp directory in order to demo a custom bundle "
        )
        world_opt["send_task_data"] = True

    shared_state = SharedParlAITaskState(
        world_opt=world_opt, onboarding_world_opt=world_opt, on_unit_submitted=make_unit_validator(db, cfg.mephisto.blueprint.block_qualification)
    )

    if cfg.qualify_new_workers:
        shared_state.mturk_specific_qualifications = [
            {
                "QualificationTypeId": "00000000000000000040",
                "Comparator": "GreaterThanOrEqualTo",
                "IntegerValues": [1500],
                "ActionsGuarded": "DiscoverPreviewAndAccept",
            },
            {
                "QualificationTypeId": "000000000000000000L0",
                "Comparator": "GreaterThanOrEqualTo",
                "IntegerValues": [95],
                "ActionsGuarded": "DiscoverPreviewAndAccept",
            },
        ]

    operator = Operator(db)

    operator.validate_and_run_config(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
