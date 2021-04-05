#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import random
import shutil
import subprocess
from mephisto.operations.operator import Operator
from mephisto.operations.utils import get_root_dir
from mephisto.tools.scripts import load_db_and_process_config
from mephisto.abstractions.blueprints.static_react_task.static_react_blueprint import (
    BLUEPRINT_TYPE,
)
from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    SharedStaticTaskState,
)
from light.data_model.light_database import LIGHTDatabase

import hydra
import json
from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import List, Any

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LIGHT_DB_PATH = "/checkpoint/light/data/database3.db"
PRIMARY_OBJECT_LIST_SIZE = 5
SECONDARY_OBJECT_LIST_SIZE = 5
DEFAULT_NUM_TASKS = 20
BLOCK_QUALIFICATION = "The answer should be a full phrase starting with 'You...'"

defaults = [
    {"mephisto/blueprint": BLUEPRINT_TYPE},
    {"mephisto/architect": "local"},
    {"mephisto/provider": "mock"},
    {"conf": "objects_interaction_task"},
]

from mephisto.operations.hydra_config import RunScriptConfig, register_script_config

@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY
    light_db_path: str = LIGHT_DB_PATH
    primary_object_list_size: int = PRIMARY_OBJECT_LIST_SIZE
    secondary_object_list_size: int = SECONDARY_OBJECT_LIST_SIZE
    num_tasks: int = DEFAULT_NUM_TASKS
    block_qualification: str = BLOCK_QUALIFICATION

def get_object_list(db_path):
    db = LIGHTDatabase(db_path)
    with db as ldb:
        object_list = [dict(obj)["name"] for obj in ldb.get_object()]

    return object_list

def create_task_data(object_list, primary_object_list_size, secondary_object_list_size, num_tasks):
    random.shuffle(object_list)
    task_data_array = []

    for idx in range(num_tasks):
        obj_name = object_list[idx % len(object_list)]

        random_object_list = random.sample(object_list, primary_object_list_size + secondary_object_list_size)
        primary_object_list = random_object_list[:primary_object_list_size]
        secondary_object_list = random_object_list[primary_object_list_size:]

        task_data_array.append({ "primary_object_list": primary_object_list, "secondary_object_list": secondary_object_list })

    return task_data_array


register_script_config(name="scriptconfig", module=TestScriptConfig)

def build_task(task_dir):
    """Rebuild the frontend for this task"""

    frontend_source_dir = os.path.join(task_dir, "webapp")
    frontend_build_dir = os.path.join(frontend_source_dir, "build")

    return_dir = os.getcwd()
    os.chdir(frontend_source_dir)
    if os.path.exists(frontend_build_dir):
        shutil.rmtree(frontend_build_dir)
    packages_installed = subprocess.call(["npm", "install"])
    if packages_installed != 0:
        raise Exception(
            "please make sure npm is installed, otherwise view "
            "the above error for more info."
        )

    webpack_complete = subprocess.call(["npm", "run", "dev"])
    if webpack_complete != 0:
        raise Exception(
            "Webpack appears to have failed to build your "
            "frontend. See the above error for more information."
        )
    os.chdir(return_dir)

def validate_unit(unit):
    print("Inside validation function")

    if unit.get_assigned_agent() is None:
        return

    data = unit.get_assigned_agent().get_data()

    if len(data) <= 20 or data.lower().find("you") == -1:
        # Not in second person
        print("Not validated unit!")
        unit.get_assigned_agent().soft_reject_work()
        worker = unit.get_assigned_agent().get_worker()
        worker.grant_qualification(cfg.block_qualification, 1)
    return

@hydra.main(config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    task_dir = cfg.task_dir

    def onboarding_always_valid(onboarding_data):
        return True

    shared_state = SharedStaticTaskState(
        static_task_data=create_task_data(get_object_list(cfg.light_db_path), cfg.primary_object_list_size, cfg.secondary_object_list_size, cfg.num_tasks),
        validate_onboarding=onboarding_always_valid
    )
    shared_state.on_unit_submitted = validate_unit

    shared_state.mturk_specific_qualifications = [
        {
            "QualificationTypeId": "00000000000000000040",
            "Comparator": "GreaterThanOrEqualTo",
            "IntegerValues": [3000],
            "ActionsGuarded": "DiscoverPreviewAndAccept",
        },
        {
            "QualificationTypeId": "000000000000000000L0",
            "Comparator": "GreaterThanOrEqualTo",
            "IntegerValues": [97],
            "ActionsGuarded": "DiscoverPreviewAndAccept",
        },
    ]

    build_task(task_dir)

    db, cfg = load_db_and_process_config(cfg)
    operator = Operator(db)

    operator.validate_and_run_config(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
