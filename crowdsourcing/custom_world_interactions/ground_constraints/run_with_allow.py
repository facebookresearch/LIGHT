##!/usr/bin/env python3

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
from light.data_model.light_database import LIGHTDatabase
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
LIGHT_DB_PATH = "~/ParlAI/data/light/environment/db/d3/database3.db"
# INPUT_FILE_TASK = "objects-interaction-task-pilot-sandbox"
# INPUT_FILE_TASK = "ground-stage-2-task-1"
INPUT_FILE_TASKS = ["objects-interaction-task-allowlist-attributes-1"]

# PREVIOUSLY_DONE_TASKS = ["objects-interaction-task-allowlist-contraints-1", "objects-interaction-task-allowlist-constraints-2"]
PREVIOUSLY_DONE_TASKS = ["objects-interaction-task-allowlist-constraints-3"]

ALLOWLIST_QUAL_NAME = "OBJINTERACTION_ATTRIBUTES_DATA_ANNOTATION_TASK_ALLOWLIST"
BLOCKLIST_QUAL_NAME = "OBJINTERACTION_ATTRIBUTES_DATA_ANNOTATION_TASK_BLOCKLIST"

ALL_GOOD_USER_FILES = [
    "/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/jing_allow_workers.txt", 
    "/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/collect_narrations/found_workers.txt"]
ALL_BAD_USER_FILES = [
    "/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/ground_events/users_who_didnt_get_it.txt",
    "/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/collect_narrations/users_who_didnt_get_it.txt",
    "/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/ground_attributes/users_who_didnt_get_it.txt",
    "/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/ground_constraints/users_who_didnt_get_it.txt"
    ]

DEFAULT_NUM_TASKS = 20

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

defaults = [
    "_self_",
    {"mephisto/blueprint": BLUEPRINT_TYPE},
    {"mephisto/architect": "local"},
    {"mephisto/provider": "mock"},
    {"conf": "constraints_events_task"},
]

from mephisto.operations.hydra_config import RunScriptConfig, register_script_config

def get_previously_completed_unit_data():
    existing_units = []
    for task_name in PREVIOUSLY_DONE_TASKS:
        task_units = mephisto_data_browser.get_units_for_task_name(task_name)
        accepted_units = [u for u in task_units if u.get_status() == "accepted"]
        for unit in accepted_units:
            inputs = mephisto_data_browser.get_data_from_unit(unit)["data"]['inputs']
            o1 = inputs['object1']['name']
            o2 = inputs['object2']['name']
            existing_units.append((o1, o2))
            # existing_units.append(inputs['interaction'])
            # inputs = mephisto_data_browser.get_data_from_unit(unit)["data"]['inputs']
            # existing_units.append(inputs['interaction'])
    return set(existing_units)

@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY
    input_file_tasks: List[str] = field(default_factory=lambda: INPUT_FILE_TASKS)
    num_tasks: int = DEFAULT_NUM_TASKS
    force_rebuild: bool = False
    qualify_new_workers: bool = False


register_script_config(name="scriptconfig", module=TestScriptConfig)


def get_light_objects():
    db = LIGHTDatabase(LIGHT_DB_PATH)
    all_objects = []
    with db as ldb:
        all_objects = [dict(obj) for obj in ldb.get_object()]
    return all_objects

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


def create_task_data(input_file_tasks, num_tasks):
    # get data from collect-narration submissions
    units = []
    for input_file_task in input_file_tasks:
        cur_units = mephisto_data_browser.get_units_for_task_name(input_file_task)
        print(f"{input_file_task}: {len(cur_units)}")
        units.extend(cur_units)
    units = [u for u in units if u.get_db_status() == "accepted"]
    previous_messages = get_previously_completed_unit_data()
    print(f"len(previously done units): {len(previous_messages)}")
    print(f"len(accepted units from previous tasks): {len(units)}")
    random.shuffle(units)
    data = []
    for unit in units:
        unit_data = mephisto_data_browser.get_data_from_unit(unit)["data"]
        new_data = unit_data['inputs']
        for key, val in unit_data['outputs'].items():
            new_data[key] = val
        if "this_task_state" in new_data:
            if 'isCreatingEntity' in new_data['this_task_state'] or 'createdModifiedAttributes' in new_data['this_task_state']:
                # if 'ranges' in new_data['this_task_state']:
                o1 = new_data['this_task_state']['object1']['name']
                o2 = new_data['this_task_state']['object2']['name']
                if (o1, o2) in previous_messages:
                    continue
                broadcastMessage = new_data['this_task_state']['interaction']
                # if broadcastMessage in previous_messages:
                #     continue
                if any(broadcastMessage.count(key) > 3 for key in ["OBJECT2", "OBJECT1", "ACTOR", "LOCATION"]):
                    continue
                data.append(new_data)
                previous_messages.add((o1, o2))
                # else:
                #     print("no ranges")
            # else:
            #     print(new_data)
                # print("subset")
        # else:
        #     print("no task state")

       

    print(f"len(data): {len(data)}")
    print(data[0])

    return data[:num_tasks]
    # return [{}]  # data[:num_tasks]


def validate_unit(unit):
    if unit.get_assigned_agent() is None:
        return

    print("Task Directory: ", TASK_DIRECTORY)

    data = mephisto_data_browser.get_data_from_unit(unit)["data"]["outputs"]
    print("Data: ", data)

    constraints = data["constraints"]
    events = data["events"]

    # front-end already handles basic validation (e.g. all answers exist, aren't inherently invalid)
    validated = True

    # TODO: extra heuristic-based validation

    if not validated:
        print("Unit not validated!")
        unit.get_assigned_agent().soft_reject_work()
        worker = unit.get_assigned_agent().get_worker()

    return


# @hydra.main(config_name="scriptconfig")
@hydra.main(config_path="hydra_configs", config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    task_dir = cfg.task_dir

    def onboarding_always_valid(onboarding_data):
        return True

    db, cfg = load_db_and_process_config(cfg)
    
    if not cfg.qualify_new_workers:
        validator = lambda u: True
    else:
        validator = validate_unit

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

    existing_qualifications = [
        make_qualification_dict(ALLOWLIST_QUAL_NAME, QUAL_EXISTS, None),
        # make_qualification_dict(BLOCKLIST_QUAL_NAME, QUAL_EXISTS, None),
    ]

    shared_state = SharedStaticTaskState(
        static_task_data=create_task_data(cfg.input_file_tasks, cfg.num_tasks),
        validate_onboarding=onboarding_always_valid,
        on_unit_submitted=validator,
    )
    shared_state.qualifications = existing_qualifications

    build_task(task_dir)

    db, cfg = load_db_and_process_config(cfg)
    operator = Operator(db)

    # operator.validate_and_run_config(cfg.mephisto, shared_state)
    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
