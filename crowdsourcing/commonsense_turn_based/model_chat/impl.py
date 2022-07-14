#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import random

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

ALLOWLIST_QUAL_NAME = "COMMONSENSE_MODELCHAT_ANNOTATION_TASK_ALLOWLIST"
BLOCKLIST_QUAL_NAME = "COMMONSENSE_MODELCHAT_ANNOTATION_TASK_BLOCKLIST"

ALL_GOOD_USER_FILES = [
    "/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/jing_allow_workers.txt", ]
ALL_BAD_USER_FILES = [
    ]

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
    with open('/private/home/alexgurung/LIGHT/crowdsourcing/commonsense_turn_based/model_chat/test_data.pkl', 'rb') as f:
        task_data = pickle.load(f)

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
