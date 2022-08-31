# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

##!/usr/bin/env python3

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
from mephisto.abstractions.blueprint import BlueprintArgs
from mephisto.abstractions.blueprints.static_react_task.static_react_blueprint import (
    BLUEPRINT_TYPE,
)
from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    SharedStaticTaskState,
)
from light.data_model.light_database import LIGHTDatabase
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.data_model.worker import Worker
from mephisto.data_model.unit import Unit

import hydra
import json
import random
from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import List, Any

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE_TASK = "fantasy-object-attribute-annotation-task-14"
DEFAULT_NUM_TASKS = 20

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

defaults = [
    {"mephisto/blueprint": BLUEPRINT_TYPE},
    {"mephisto/architect": "local"},
    {"mephisto/provider": "mock"},
    {"conf": "fantasy_object_attribute_annotation_task"},
]

from mephisto.operations.hydra_config import RunScriptConfig, register_script_config


@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY
    input_file_task: str = INPUT_FILE_TASK
    num_tasks: int = DEFAULT_NUM_TASKS


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


def create_task_data(input_file_task, num_tasks):
    # units = mephisto_data_browser.get_units_for_task_name(input_file_task)
    # random.shuffle(units)
    # data = []
    # for unit in units:
    #    data.append(
    #        mephisto_data_browser.get_data_from_unit(unit)["data"]["outputs"][
    #            "final_data"
    #        ]
    #    )

    return [{}]  # data[:num_tasks]


def validate_unit(unit):
    if unit.get_assigned_agent() is None:
        return

    print("Task Directory: ", TASK_DIRECTORY)

    data = mephisto_data_browser.get_data_from_unit(unit)["data"]["outputs"][
        "final_data"
    ]
    print("Data: ", data)

    constraints = data["constraints"]
    events = data["events"]

    has_active = False

    for constraint in constraints:
        if constraint["active"] == "1":
            has_active = True
            break

    for event in events:
        if event["active"] == "1":
            has_active = True
            break

    if not has_active:
        print("Unit not validated!")
        unit.get_assigned_agent().soft_reject_work()
        worker = unit.get_assigned_agent().get_worker()
        worker.grant_qualification("fantasy_object_attribute_annotation_task_block", 1)

    return


@hydra.main(config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    task_dir = cfg.task_dir

    def onboarding_always_valid(onboarding_data):
        return True

    shared_state = SharedStaticTaskState(
        static_task_data=create_task_data(cfg.input_file_task, cfg.num_tasks),
        validate_onboarding=onboarding_always_valid,
        on_unit_submitted=validate_unit,
    )

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
