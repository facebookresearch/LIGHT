#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import random
import shutil
import subprocess
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import load_db_and_process_config
from mephisto.abstractions.blueprints.static_react_task.static_react_blueprint import (
    BLUEPRINT_TYPE_STATIC_REACT as BLUEPRINT_TYPE,
)
from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    SharedStaticTaskState,
)
from light.data_model.db.environment import EnvDB
from light.data_model.db.base import LightLocalDBConfig
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.data_model.worker import Worker
from mephisto.data_model.unit import Unit
from mephisto.utils.qualifications import make_qualification_dict
from mephisto.data_model.qualification import QUAL_EXISTS
from parlai_internal.crowdsourcing.projects.reverse_persona.utils.dataloading_utils import (
    get_block_list,
)
from mephisto.abstractions.providers.mturk.utils.script_utils import (
    direct_soft_block_mturk_workers,
)

import hydra
import json
import random
from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import List, Any

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LIGHT_DB_PATH = "/checkpoint/light/db/prod"
# LIGHT_DB_PATH = "/Users/jju/LIGHT/prod_db"
SECONDARY_OBJECT_LIST_SIZE = 6
DEFAULT_NUM_TASKS = 20

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

defaults = [
    "_self_",
    {"mephisto/blueprint": BLUEPRINT_TYPE},
    {"mephisto/architect": "local"},
    {"mephisto/provider": "mock"},
    {"conf": "collect_narrations"},
]

from mephisto.operations.hydra_config import RunScriptConfig, register_script_config


ALLOWLIST_QUAL_NAME = "OBJINTERACTION_NARRATION_DATA_ANNOTATION_TASK_ALLOWLIST"
BLOCKLIST_QUAL_NAME = "OBJINTERACTION_NARRATION_DATA_ANNOTATION_TASK_BLOCKLIST"

ALL_GOOD_USER_FILES = ["/checkpoint/light/common_sense/jing_worker_allow_list.txt"]
ALL_BAD_USER_FILES = ["/checkpoint/light/common_sense/all_bad_users.txt"]


@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY
    light_db_path: str = LIGHT_DB_PATH
    secondary_object_list_size: int = SECONDARY_OBJECT_LIST_SIZE
    num_tasks: int = DEFAULT_NUM_TASKS
    force_rebuild: bool = False
    qualify_new_workers: bool = False
    use_allowlist: bool = False


def get_object_lists(db_path):
    ldb = EnvDB(LightLocalDBConfig(file_root=LIGHT_DB_PATH))
    all_objects = ldb.find_objects()

    secondary_objects = [
        {"name": obj.name, "desc": obj.physical_description} for obj in all_objects
    ]

    return secondary_objects


def create_task_data(
    secondary_objects,
    secondary_object_list_size,
    num_tasks,
):
    random.shuffle(secondary_objects)
    task_data_array = []

    for _ in range(num_tasks):
        secondary_object_list = random.sample(
            secondary_objects, secondary_object_list_size
        )
        task_data_array.append(
            {
                "secondary_object_list": secondary_object_list,
            }
        )

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
    if unit.get_assigned_agent() is None:
        return

    unit_data = mephisto_data_browser.get_data_from_unit(unit)
    unit_data = unit_data.get("data")

    if unit_data is None:
        return

    data = unit_data.get("outputs")

    if data is None or "actionDescription" not in data:
        return
    action_description = data["actionDescription"]
    if type(action_description) is not str:
        return
    action_description = action_description.strip()

    object_name = data["primaryObject"]
    object_description = data["primaryDescription"]

    # some basic filtering
    if (
        len(action_description) <= 20
        or action_description.lower().find("you") == -1
        or (
            action_description.lower()[-1] != "."
            and action_description.lower()[-1] != "?"
            and action_description.lower()[-1] != "!"
        )
        or len(object_description) <= 20
    ):
        # Not in second person or invalid punctuation
        print("Action " + action_description + " was not validated!")
        print("Or Object " + object_description + " was not validated!")
        # unit.get_assigned_agent().soft_reject_work() => must wait for async version
        worker = unit.get_assigned_agent().get_worker()
        worker.grant_qualification("collect_narrations_task_block", 1)
    return


@hydra.main(config_path="hydra_configs", config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    print(cfg)
    task_dir = cfg.task_dir

    def onboarding_always_valid(onboarding_data):
        return True

    secondary_objects = get_object_lists(
        cfg.light_db_path,
    )

    if not cfg.qualify_new_workers:
        validator = lambda u: True
    else:
        validator = validate_unit

    db, cfg = load_db_and_process_config(cfg)

    using_allowlist = cfg.use_allowlist
    if using_allowlist:
        # # Kind of hacky, but add qualifications to good+bad users
        # for fname in ALL_GOOD_USER_FILES:
        #     direct_soft_block_mturk_workers(
        #         db,
        #         get_block_list(fname),
        #         ALLOWLIST_QUAL_NAME,
        #         cfg.mephisto.provider.requester_name,
        #     )

        # for fname in ALL_BAD_USER_FILES:
        #     direct_soft_block_mturk_workers(
        #         db,
        #         get_block_list(fname),
        #         BLOCKLIST_QUAL_NAME,
        #         cfg.mephisto.provider.requester_name,
        #     )
        # add allowlist qualification
        existing_qualifications = [
            make_qualification_dict("collect_narrations_task_allow_09_19", QUAL_EXISTS, None),
        ]

    shared_state = SharedStaticTaskState(
        static_task_data=create_task_data(
            secondary_objects,
            cfg.secondary_object_list_size,
            cfg.num_tasks,
        ),
        validate_onboarding=onboarding_always_valid,
        on_unit_submitted=validator,
    )

    if using_allowlist:
        # add qualifications
        shared_state.qualifications = existing_qualifications

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
                "IntegerValues": [97],
                "ActionsGuarded": "DiscoverPreviewAndAccept",
            },
        ]

    built_file = os.path.join(task_dir, "webapp", "build", "bundle.js")
    if cfg.force_rebuild or not os.path.exists(built_file):
        build_task(task_dir)

    db, cfg = load_db_and_process_config(cfg)
    operator = Operator(db)
    operator.validate_and_run_config(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=300)


if __name__ == "__main__":
    main()
