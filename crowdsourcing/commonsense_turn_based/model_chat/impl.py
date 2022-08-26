#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import random
import copy

import jsonlines

from mephisto.operations.operator import Operator
from mephisto.tools.scripts import load_db_and_process_config
from omegaconf import DictConfig, OmegaConf

from parlai.crowdsourcing.utils.mturk import soft_block_mturk_workers
# from parlai.crowdsourcing.tasks.model_chat.model_chat_blueprint import (
#     SharedModelChatTaskState,
# )
from model_chat_blueprint import (
    SharedModelChatTaskState,
)
from dataclasses import dataclass, field
from typing import ClassVar, List, Type, Any, Dict, Iterable, TYPE_CHECKING

from mephisto.utils.qualifications import make_qualification_dict
from mephisto.data_model.qualification import QUAL_EXISTS
from parlai_internal.crowdsourcing.projects.reverse_persona.utils.dataloading_utils import (
    get_block_list,
)
from mephisto.abstractions.providers.mturk.utils.script_utils import (
    direct_soft_block_mturk_workers,
)
from light.data_model.light_database import LIGHTDatabase
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser

ALLOWLIST_QUAL_NAME = "COMMONSENSE_MODELCHAT_ANNOTATION_TASK_ALLOWLIST"
BLOCKLIST_QUAL_NAME = "COMMONSENSE_MODELCHAT_ANNOTATION_TASK_BLOCKLIST"

ALL_GOOD_USER_FILES = [
    "/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/jing_allow_workers.txt", ]
ALL_BAD_USER_FILES = [
    ]

# PREVIOUSLY_DONE_TASKS = ["commonsense_model_chat_bart_grounded_1"]
# PREVIOUSLY_DONE_TASKS = ["commonsense_model_chat_bart_nongrounded_3"]
PREVIOUSLY_DONE_TASKS = []

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)
def get_previously_completed_unit_data():
    existing_units = []
    for task_name in PREVIOUSLY_DONE_TASKS:
        task_units = mephisto_data_browser.get_units_for_task_name(task_name)
        # accepted_units = [u for u in task_units if u.get_status() == "accepted"]
        for unit in task_units:
            # data = mephisto_data_browser.get_data_from_unit(unit)
            resp = mephisto_data_browser.get_data_from_unit(unit)['data']['initial_data']['game_text_dropoutless']
            existing_units.append(resp)
    return set(existing_units)

@dataclass
class SharedModelWithTaskData(SharedModelChatTaskState):
    static_task_data: Iterable[Any] = field(
        default_factory=list,
        metadata={
            "help": (
                "List or generator that returns dicts of task data. Generators can be "
                "used for tasks with lengths that aren't known at the start of a "
                "run, or are otherwise determined during the run. "
            ),
            "type": "Iterable[Dict[str, Any]]",
            "default": "[]",
        },
    )


def run_task(cfg: DictConfig, task_directory: str, world_module=None, only_allow=False):
    """
    Run task, given configuration.
    """

    frontend_source_dir = os.path.join(task_directory, "webapp")
    frontend_build_dir = os.path.join(frontend_source_dir, "build")
    _ = frontend_build_dir  # Unused at the moment

    db, cfg = load_db_and_process_config(cfg)
    print(f'\nHydra config:\n{OmegaConf.to_yaml(cfg)}')

    random.seed(42)

    if only_allow:
        for fname in ALL_GOOD_USER_FILES:
            direct_soft_block_mturk_workers(
                db,
                get_block_list(fname),
                ALLOWLIST_QUAL_NAME,
                cfg.mephisto.provider.requester_name,
            )

        for fname in ALL_BAD_USER_FILES:
            direct_soft_block_mturk_workers(
                db,
                get_block_list(fname),
                BLOCKLIST_QUAL_NAME,
                cfg.mephisto.provider.requester_name,
            )

    # Update task name when on sandbox or local to ensure data is split.
    task_name = cfg.mephisto.task.get('task_name', 'model_chat')
    architect_type = cfg.mephisto.architect._architect_type
    if architect_type == 'local':
        task_name = f"{task_name}_local"
    elif architect_type == 'mturk_sandbox':
        task_name = f"{task_name}_sandbox"
    cfg.mephisto.task.task_name = task_name

    # soft_block_qual_name = cfg.mephisto.blueprint.get(
    #     'block_qualification', f'{task_name}_block'
    # )
    # Default to a task-specific name to avoid soft-block collisions
    # soft_block_mturk_workers(cfg=cfg, db=db, soft_block_qual_name=soft_block_qual_name)
    
    #######################
    import pickle

    task_data = None
    
    # with open("/checkpoint/alexgurung/tmp/validating_test_data/output_bart_compare_largersweep_Sun_Aug_14_d4e_InvalidSelfPlayNarrationTeacher_test_data.pkl", "rb") as f:
    #     task_data = pickle.load(f)
    fname = "/checkpoint/alexgurung/light/common_sense/compare_grounding/world_logs/6ce/6ce_internal:light_common_sense:InvalidSelfPlayNarrationTeacher.jsonl"
    # fname = "/checkpoint/alexgurung/light/common_sense/compare_grounding/world_logs/341/341_internal:light_common_sense:InvalidSelfPlayNarrationTeacher.jsonl"
    dialogs = []
    with jsonlines.open(fname, "r") as f:
        for line in f:
            dialogs.append(line)

    task_data = []
    for item in dialogs:
        this_dialog = item['dialog']
        this_dialog = this_dialog[0]
        teacher_dialog = this_dialog[0]
        game_text = teacher_dialog['game_text_dropoutless']
        # this_game_texts.add(game_text)
        task_data.append(teacher_dialog)


    # with open("/private/home/alexgurung/LIGHT/crowdsourcing/commonsense_turn_based/nochat_modelchat/retrofit_good_observations.txt", 'r') as f:
    #     good_obs = f.read()

    # new_task_data = []
    # for t in task_data:
    #     if t['teacher']['agent_observation'] in good_obs:
    #         new_task_data.append(t)
            

    # task_data = [t['teacher'] for t in task_data]
    # print(task_data)
    # print(task_data[0])
    # x = 1/0
    seen_responses = get_previously_completed_unit_data()
    print(f"Pre previously tasks: {len(task_data)}")
    task_data = [t for t in task_data if t['game_text_dropoutless'] not in seen_responses]
    print(f"Post previously tasks: {len(task_data)}")
    new_task_data = []
    for t in task_data:
        if len(t['setting_context_text_dropoutless']) == 0:
            continue
        new_task_data.append(copy.deepcopy(t))
        new_task_data[-1]['saved_contextual_data'] = copy.deepcopy(t)
    task_data = new_task_data
    random.shuffle(task_data)
    #######################

    # Init
    # shared_state = SharedModelWithTaskData(world_module=world_module, static_task_data=[{'context': "some context text"} for i in range(100)])
    task_data = task_data[:cfg.num_tasks]
    shared_state = SharedModelWithTaskData(world_module=world_module, static_task_data=task_data)
    # shared_state = SharedModelChatTaskState(world_module=world_module)

    if only_allow:
        existing_qualifications = [
            make_qualification_dict(ALLOWLIST_QUAL_NAME, QUAL_EXISTS, None),
            # make_qualification_dict(BLOCKLIST_QUAL_NAME, QUAL_EXISTS, None),
        ]

        shared_state.qualifications = existing_qualifications



    operator = Operator(db)
    operator.validate_and_run_config(run_config=cfg.mephisto, shared_state=shared_state)
    operator.wait_for_runs_then_shutdown(
        skip_input=True, log_rate=cfg.monitoring_log_rate
    )
