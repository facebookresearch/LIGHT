##!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import random
import shutil
import subprocess
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import load_db_and_process_config
from mephisto.abstractions.blueprint import BlueprintArgs
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

import hydra
import json
import random
from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import List, Any

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LIGHT_DB_PATH = "~/ParlAI/data/light/environment/db/d3/database3.db"
# INPUT_FILE_TASK = "objects-interaction-task-pilot-sandbox"
# INPUT_FILE_TASK = "objects-interaction-task-pilot-3"
INPUT_FILE_TASKS = [
    "objects-interaction-task-pilot-4",
    "objects-interaction-task-pilot-5",
]
# PREVIOUSLY_DONE_TASKS = ["ground-stage-1-pilot-2", "ground-stage-1-pilot-3"]
PREVIOUSLY_DONE_TASKS = ["ground-stage-1-pilot-3", "ground-stage-1-pilot-4"]

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


@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY
    # input_file_task: str = INPUT_FILE_TASK
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


def match_object_to_list(object_name, object_list):
    # TODO: handle non-found case, which shouldn't theoretically happen
    # currently returns the first matching object with the information we have, technically multiple could apply
    return [obj for obj in object_list if obj["name"] == object_name][0]


def find_light_object(light_objects, cur_obj):
    # search through light objects for object whose name and physical description match the input
    matching_objects = [
        o
        for o in light_objects
        if o["name"] == cur_obj["name"] and o["physical_description"] == cur_obj["desc"]
    ]
    if len(matching_objects) == 0:
        # no matching object found
        return None
    # should be only one matching object, but regardless return the first one
    return matching_objects[0]


def get_attributes_from_light_obj(obj):
    # all attributes start with is_, ignore is_plural because it's not the kind of thing that changes
    return [
        {"name": k.replace("is_", ""), "val": v > 0.5}
        for k, v in obj.items()
        if k.startswith("is_") and k != "is_plural"
    ]


def get_attributes_from_obj(light_objects, obj):
    light_obj = find_light_object(light_objects, obj)
    if light_obj is None:
        return []
    return get_attributes_from_light_obj(light_obj)


def get_previously_completed_unit_data():
    existing_units = []
    for task_name in PREVIOUSLY_DONE_TASKS:
        task_units = mephisto_data_browser.get_units_for_task_name(task_name)
        for unit in task_units:
            inputs = mephisto_data_browser.get_data_from_unit(unit)["data"]["inputs"]
            obj1 = inputs["object1"]["name"]
            obj2 = inputs["object2"]["name"]
            rawAction = inputs["rawAction"]
            interaction = inputs["interaction"]
            existing_units.append((obj1, obj2, rawAction, interaction))
    return set(existing_units)


def new_unit_in_completed(new_unit_data, existing_units):
    obj1 = new_unit_data["object1"]["name"]
    obj2 = new_unit_data["object2"]["name"]
    rawAction = new_unit_data["rawAction"]
    interaction = new_unit_data["interaction"]
    return (obj1, obj2, rawAction, interaction) in existing_units


def create_task_data(input_file_tasks, num_tasks):
    # get data from collect-narration submissions
    units = []
    for t in input_file_tasks:
        new_units = mephisto_data_browser.get_units_for_task_name(t)
        units.extend(new_units)
        print(f"{t}: {len(new_units)} -> {len(units)}")
    units = [u for u in units if u.get_db_status() == "accepted"]
    print(f"len(accepted units): {len(units)}")
    all_light_objects = get_light_objects()
    random.shuffle(units)
    data = []
    existing_units = get_previously_completed_unit_data()
    print(f"len(existing) {len(existing_units)}")
    for unit in units:
        # iterate over narration units and resolve names with their corresponding objects (which have descriptions)
        unit_data = mephisto_data_browser.get_data_from_unit(unit)["data"]
        primary_objects, secondary_objects = (
            unit_data["inputs"]["primary_object_list"],
            unit_data["inputs"]["secondary_object_list"],
        )
        # output_data = unit_data['outputs']['final_data']
        output_data = unit_data["outputs"]
        # get primary and secondary objects from their corresponding lists
        primary_object = match_object_to_list(
            output_data["primaryObject"], primary_objects
        )
        primary_object["attributes"] = get_attributes_from_obj(
            all_light_objects, primary_object
        )

        secondary_object = match_object_to_list(
            output_data["secondaryObject"], secondary_objects
        )
        secondary_object["attributes"] = get_attributes_from_obj(
            all_light_objects, secondary_object
        )
        # input to this grounding task has both objects and their interaction text
        data_for_unit = {
            "object1": primary_object,
            "object2": secondary_object,
            "interaction": output_data["actionDescription"],
            "rawAction": output_data["rawAction"],
        }
        if not new_unit_in_completed(data_for_unit, existing_units):
            data.append(data_for_unit)

    print(f"len(data): {len(data)}")
    print(data[0])

    return data[:num_tasks]
    # return [{}]  # data[:num_tasks]


def validate_unit(unit):
    if unit.get_assigned_agent() is None:
        return

    print("Task Directory: ", TASK_DIRECTORY)
    unit_data = mephisto_data_browser.get_data_from_unit(unit)
    unit_data = unit_data.get("data")

    if unit_data is None:
        return

    data = unit_data.get("outputs")
    print("Data: ", data)

    # front-end already handles basic validation (e.g. all answers exist, aren't inherently invalid)
    validated = True

    # TODO: extra heuristic-based validation

    if not validated:
        print("Unit not validated!")
        unit.get_assigned_agent().soft_reject_work()
        worker = unit.get_assigned_agent().get_worker()
        worker.grant_qualification("ground_events_1_task_block", 1)

    return


@hydra.main(config_path="hydra_configs", config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    task_dir = cfg.task_dir

    def onboarding_always_valid(onboarding_data):
        return True

    if not cfg.qualify_new_workers:
        validator = lambda u: True
    else:
        validator = validate_unit

    shared_state = SharedStaticTaskState(
        static_task_data=create_task_data(cfg.input_file_tasks, cfg.num_tasks),
        validate_onboarding=onboarding_always_valid,
        on_unit_submitted=validator,
    )

    # shared_state.mturk_specific_qualifications = [
    #     {
    #         "QualificationTypeId": "00000000000000000040",
    #         "Comparator": "GreaterThanOrEqualTo",
    #         "IntegerValues": [3000],
    #         "ActionsGuarded": "DiscoverPreviewAndAccept",
    #     },
    #     {
    #         "QualificationTypeId": "000000000000000000L0",
    #         "Comparator": "GreaterThanOrEqualTo",
    #         "IntegerValues": [97],
    #         "ActionsGuarded": "DiscoverPreviewAndAccept",
    #     },
    # ]

    # build_task(task_dir)
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

    built_file = os.path.join(task_dir, "webapp", "build", "bundle.js")
    if cfg.force_rebuild or not os.path.exists(built_file):
        build_task(task_dir)

    db, cfg = load_db_and_process_config(cfg)
    operator = Operator(db)

    operator.validate_and_run_config(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
