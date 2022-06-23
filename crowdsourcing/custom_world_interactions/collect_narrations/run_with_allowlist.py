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
    BLUEPRINT_TYPE_STATIC_REACT as BLUEPRINT_TYPE
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

from mephisto.utils.qualifications import make_qualification_dict

from mephisto.data_model.qualification import QUAL_EXISTS

from mephisto.abstractions.providers.mturk.utils.script_utils import (
    # direct_allow_mturk_workers,
    direct_soft_block_mturk_workers,
)
from parlai_internal.crowdsourcing.projects.reverse_persona.utils.dataloading_utils import (
    get_block_list,
)
from parlai_internal.crowdsourcing.projects.reverse_persona.parlai_chat_task_demo.constants import (
    ALLOWLIST_QUAL_NAME,
)
from parlai.crowdsourcing.tasks.model_chat.model_chat_blueprint import (
    SharedModelChatTaskState,
)
import parlai_internal.crowdsourcing.projects.continual_learning.model_chat.worlds as world_module

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
# LIGHT_DB_PATH = "~/ParlAI/data/LIGHT/merged.db"
LIGHT_DB_PATH = "~/ParlAI/data/light/environment/db/d3/database3.db"
PRIMARY_OBJECT_LIST_SIZE = 8
SECONDARY_OBJECT_LIST_SIZE = 8
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


@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY
    light_db_path: str = LIGHT_DB_PATH
    primary_object_list_size: int = PRIMARY_OBJECT_LIST_SIZE
    secondary_object_list_size: int = SECONDARY_OBJECT_LIST_SIZE
    num_tasks: int = DEFAULT_NUM_TASKS
    force_rebuild: bool = False
    qualify_new_workers: bool = False


def get_object_lists(db_path):
    db = LIGHTDatabase(db_path)
    with db as ldb:
        all_objects = [dict(obj) for obj in ldb.get_object()]

    primary_objects = [
        {"name": obj["name"], "desc": obj["physical_description"]}
        for obj in all_objects
        if obj["is_gettable"] > 0.5
    ]

    secondary_objects = [
        {"name": obj["name"], "desc": obj["physical_description"]}
        for obj in all_objects
    ]

    return primary_objects, secondary_objects


def create_task_data(
    primary_objects,
    secondary_objects,
    primary_object_list_size,
    secondary_object_list_size,
    num_tasks,
):
    random.shuffle(primary_objects)
    random.shuffle(secondary_objects)
    task_data_array = []

    for idx in range(num_tasks):
        primary_object_list = random.sample(primary_objects, primary_object_list_size)
        secondary_object_list = random.sample(
            secondary_objects, secondary_object_list_size
        )

        task_data_array.append(
            {
                "primary_object_list": primary_object_list,
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

    if (
        len(action_description) <= 20
        or action_description.lower().find("you") == -1
        or (
            action_description.lower()[-1] != "."
            and action_description.lower()[-1] != "?"
            and action_description.lower()[-1] != "!"
        )
    ):
        # Not in second person or invalid punctuation
        print("Action " + action_description + " was not validated!")
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

    primary_objects, secondary_objects = get_object_lists(
        cfg.light_db_path,
    )

    if not cfg.qualify_new_workers:
        validator = lambda u: True
    else:
        validator = validate_unit

    existing_qualifications = [
            make_qualification_dict(ALLOWLIST_QUAL_NAME, QUAL_EXISTS, None)
        ]

    shared_state = SharedStaticTaskState(
    # shared_state = SharedModelChatTaskState(
        static_task_data=create_task_data(
            primary_objects,
            secondary_objects,
            cfg.primary_object_list_size,
            cfg.secondary_object_list_size,
            cfg.num_tasks,
        ),
        # world_module=world_module,
        # validate_onboarding=onboarding_always_valid,
        on_unit_submitted=validator,
        qualifications=existing_qualifications
    )

    
    architect_type = cfg.mephisto.architect._architect_type
    db, cfg = load_db_and_process_config(cfg)
    if architect_type != 'local':
        direct_soft_block_mturk_workers(
            db,
            get_block_list(
                f"/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/jing_allow_workers.txt"
            ),
            ALLOWLIST_QUAL_NAME,
            cfg.mephisto.provider.requester_name,
        )
        direct_soft_block_mturk_workers(
            db,
            get_block_list(
                f"/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/collect_narrations/found_workers.txt"
            ),
            ALLOWLIST_QUAL_NAME,
            cfg.mephisto.provider.requester_name,
        )

    # shared_state = SharedModelChatTaskState(
    #     world_module=world_module, qualifications=existing_qualifications
    # )

    # shared_state.world_opt.update(
    #     {
    #         'requester_name': 'alexgurung',
    #         'allowlist_only': True,
    #         'architect_type': architect_type,
    #     }
    # )
    # shared_state.onboarding_world_opt.update(
    #     {
    #         'requester_name': 'alexgurung',
    #         'allowlist_only': True,
    #         'architect_type': architect_type,
    #     }
    # )

    built_file = os.path.join(task_dir, "webapp", "build", "bundle.js")
    if cfg.force_rebuild or not os.path.exists(built_file):
        build_task(task_dir)

    db, cfg = load_db_and_process_config(cfg)
    operator = Operator(db)
    operator.validate_and_run_config(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
