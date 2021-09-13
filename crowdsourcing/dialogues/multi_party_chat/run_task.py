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
        default=300,
        metadata={
            "help": "Maximum response time before kicking "
            "a worker out, default 300 seconds"
        },
    )
    qualify_new_workers: bool = False


register_script_config(name="scriptconfig", module=ScriptConfig)


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
        world_opt=world_opt, onboarding_world_opt=world_opt
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
