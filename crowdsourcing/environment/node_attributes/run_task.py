##!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import random
import shutil
import subprocess
import pandas as pd
import numpy as np
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
REMAINING_TASKS_DIRECTORY = os.path.join(TASK_DIRECTORY, 'tasks')
ANNOTATIONS_PER_ENTITY = 2
ENTITIES_PER_TASK = 4
DEFAULT_NUM_TASKS = 50
LIGHT_DB_PATH = "~/ParlAI/data/LIGHT/merged.db"

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

defaults = [
    {"mephisto/blueprint": BLUEPRINT_TYPE},
    {"mephisto/architect": "local"},
    {"mephisto/provider": "mock"},
    {"conf": "find_workers"},
]

from mephisto.operations.hydra_config import RunScriptConfig, register_script_config


@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY
    num_tasks: int = DEFAULT_NUM_TASKS
    force_rebuild: bool = False
    qualify_new_workers: bool = False


register_script_config(name="scriptconfig", module=TestScriptConfig)


def construct_complete_task_list():
    """
    If it doesn't already exist, construct a local list of tasks that have
    been completed for this.

    All things should be annotated at least as part of two batches, with 
    additional batches for each "special" attribute they have.

    As such, we construct a set of stacks that get popped from when tasks
    are launched. When the tasks are shut down we need to write any
    expired content back to the unfinished queue. 
    """
    if os.path.exists(REMAINING_TASKS_DIRECTORY):
        return # this directory has already been constructed

    os.makedirs(REMAINING_TASKS_DIRECTORY, exist_ok=True)
    
    db = LIGHTDatabase(LIGHT_DB_PATH)
    with db as ldb:
        all_objects = [dict(obj) for obj in ldb.get_object()]
        all_characters = [dict(char) for char in ldb.get_character()]
        all_rooms = [dict(room) for room in ldb.get_room()]

    parsed_objects = [
        {
            'id': o['id'],
            'name': o['name'],
            'description': o['physical_description'],
            'wieldable': o['is_weapon'] > 0.5,
            'wearable': o['is_wearable'] > 0.5,
            'food': o['is_food'] > 0.5,
            'drink': o['is_drink'] > 0.5,
            'container': o['is_container'] > 0.5,
            'surface': o['is_surface'] > 0.5,
            'carryable': o['is_gettable'] > 0.5,
            'assigned': 0,
            'annotated': 0,
        } for o in all_objects
    ]

    parsed_characters = [
        {
            'id': o['id'],
            'name': o['name'] + " (a member of)" if o['is_plural'] > 0.5 else o['name'],
            'description': f"PERSONA: {o['persona']}. DESCRIPTION: {o['physical_description']}",
            'is_human': o['char_type'] == 'person',
            'assigned': 0,
            'annotated': 0,
        } for o in all_characters
    ]

    parsed_rooms = [
        {
            'id': o['id'],
            'name': o['name'],
            'description': o['description'] + " " + o['backstory'],
            'assigned': 0,
            'annotated': 0,
        } for o in all_rooms
    ]

    containers = [o for o in parsed_objects if o['container'] or o['surface']]
    weapons = [o for o in parsed_objects if o['wieldable']]
    wearable = [o for o in parsed_objects if o['wearable']]
    consumable = [o for o in parsed_objects if o['food'] or o['drink']]
    
    dfs = {
        'objs': pd.DataFrame(parsed_objects),
        'chars': pd.DataFrame(parsed_characters),
        'rooms': pd.DataFrame(parsed_rooms),
        'containers': pd.DataFrame(containers),
        'weapons': pd.DataFrame(weapons),
        'wearable': pd.DataFrame(wearable),
        'consumable': pd.DataFrame(consumable),
    }
   
    for csv_name, df in dfs.items():
        df.to_csv(os.path.join(REMAINING_TASKS_DIRECTORY, f"{csv_name}.csv"), index=False)
    

def select_one_task(df):
    df.sort_values(by=['assigned'])
    search_cap = len(df.index[df.assigned < ANNOTATIONS_PER_ENTITY])
    if search_cap == 0:
        return None
    accessible = range(search_cap)
    if search_cap < ENTITIES_PER_TASK:
        extra = np.random.choice(
            range(search_cap, df.shape[0]), 
            size=(ENTITIES_PER_TASK-search_cap,), 
            replace=False,
        )
        idxs = accessible + extra.tolist()
    else:
        idxs = np.random.choice(
            accessible, 
            size=(ENTITIES_PER_TASK,), 
            replace=False,
        ).tolist()
    entries = []
    ATTRIBUTES = [
        'wieldable', 'wearable', 'food', 'drink', 'container', 'surface', 'carryable'
    ]
    for idx in idxs:
        df.at[idx, 'assigned'] += 1
        e = df.iloc[idx]
        entry =  {
            'id': int(e['id']),
            'name': e['name'],
            'description': e['description'],
        }
        entry['attributes'] = [
            {"name": name, 'value': bool(e[name])} for name in df.columns 
            if name in ATTRIBUTES
        ]
        
        entries.append(entry)

    return entries


def construct_tasks(num_tasks, task_types=None):
    """
    Construct tasks from the remaining complete task list, up to the amount desired

    If a task type is provided, only selects from that task type
    """
    csv_names = ['objs', 'chars', 'rooms', 'containers', 'weapons', 'wearable', 'consumable']
    if task_types is None: 
        task_types = csv_names
    csv_dfs = {name: pd.read_csv(os.path.join(REMAINING_TASKS_DIRECTORY, f"{name}.csv")) for name in csv_names}
    
    tasks = []
    while len(tasks) < num_tasks:
        task_type = random.choice(task_types)
        df = csv_dfs[task_type]
        item_category = "objects"
        if task_type == 'chars':
            item_category = "characters"
        elif task_type == 'rooms':
            item_category = 'locations'
        
        selections = select_one_task(df)
        if selections is None:
            task_types.remove(task_type)
            if len(task_types) == 0:
                break
            continue
        tasks.append(
            {
                "itemCategory": item_category,
                "selection": selections,
            }
        )

    # Write out the newly selected annotations
    entities_left = 0
    for csv_name, df in csv_dfs.items():
        entities_left += len(df['assigned'])*2 - df['assigned'].sum()
        df.to_csv(os.path.join(REMAINING_TASKS_DIRECTORY, f"{csv_name}.csv"), index=False)

    print(
        f"At the rate of {ENTITIES_PER_TASK} entities per task, "
        f"there are still {entities_left/ENTITIES_PER_TASK} more tasks to launch "
        "after this batch."
    )
    return tasks


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

    print("Task Directory: ", TASK_DIRECTORY)

    data = mephisto_data_browser.get_data_from_unit(unit)["data"]["outputs"][
        "final_data"
    ]
    print("Data: ", data)

    # constraints = data["constraints"]
    # events = data["events"]

    # has_active = False

    # for constraint in constraints:
    #     if constraint["active"] == "1":
    #         has_active = True
    #         break

    # for event in events:
    #     if event["active"] == "1":
    #         has_active = True
    #         break

    # if not has_active:
    #     print("Unit not validated!")
    #     unit.get_assigned_agent().soft_reject_work()
    #     worker = unit.get_assigned_agent().get_worker()
    #     worker.grant_qualification("fantasy_object_attribute_annotation_task_block", 1)

    return


@hydra.main(config_path="hydra_configs", config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    task_dir = cfg.task_dir

    construct_complete_task_list()

    def onboarding_always_valid(onboarding_data):
        return True

    shared_state = SharedStaticTaskState(
        static_task_data=construct_tasks(cfg.num_tasks),
        validate_onboarding=onboarding_always_valid,
        on_unit_submitted=validate_unit,
    )

    if cfg.qualify_new_workers:
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

    built_file = os.path.join(task_dir, "webapp", "build", "bundle.js")
    if cfg.force_rebuild or not os.path.exists(built_file):
        build_task(task_dir)

    db, cfg = load_db_and_process_config(cfg)
    operator = Operator(db)

    operator.validate_and_run_config(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
