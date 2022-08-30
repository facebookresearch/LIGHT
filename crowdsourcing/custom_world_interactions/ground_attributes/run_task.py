##!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import random
import shutil
import subprocess

from numpy import broadcast
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

import hydra
import json
import random
from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import List, Any

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LIGHT_DB_PATH = "~/ParlAI/data/light/environment/db/d3/database3.db"
# INPUT_FILE_TASK = "objects-interaction-task-pilot-sandbox"
# INPUT_FILE_TASK = "ground-stage-1-task-1"
# INPUT_FILE_TASK = "ground-stage-1-pilot-3"
# INPUT_FILE_TASKS = ["ground-stage-1-pilot-3", "ground-stage-1-pilot-4", "ground-stage-1-pilot-5"]
INPUT_FILE_TASKS = ["ground-stage-1-pilot-3", "ground-stage-1-pilot-4"]
# PREVIOUSLY_DONE_TASKS = ["ground-stage-2-pilot-1"]
PREVIOUSLY_DONE_TASKS = ["ground-stage-2-pilot-2", "ground-stage-2-pilot-3"]

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


# @dataclass
# class TestScriptConfig(RunScriptConfig):
#     defaults: List[Any] = field(default_factory=lambda: defaults)
#     task_dir: str = TASK_DIRECTORY
#     input_file_task: str = INPUT_FILE_TASK
#     num_tasks: int = DEFAULT_NUM_TASKS
@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY
    # input_file_tasks: str = INPUT_FILE_TASKS
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


def get_previously_completed_unit_data():
    existing_units = []
    for task_name in PREVIOUSLY_DONE_TASKS:
        task_units = mephisto_data_browser.get_units_for_task_name(task_name)
        for unit in task_units:
            inputs = mephisto_data_browser.get_data_from_unit(unit)["data"]["inputs"]
            existing_units.append(inputs["this_task_state"]["broadcastMessage"])
    return set(existing_units)


def create_task_data(input_file_tasks, num_tasks):
    # get data from collect-narration submissions
    units = []
    for input_file_task in input_file_tasks:
        cur_units = mephisto_data_browser.get_units_for_task_name(input_file_task)
        print(f"{input_file_task}: {len(cur_units)}")
        units.extend(cur_units)
    units = [u for u in units if u.get_db_status() == "accepted"]
    previous_messages = get_previously_completed_unit_data()
    print(f"len(previously units): {len(previous_messages)}")
    print(f"len(accepted units): {len(units)}")
    random.shuffle(units)
    data = []
    for unit in units:
        unit_data = mephisto_data_browser.get_data_from_unit(unit)["data"]
        new_data = unit_data["inputs"]
        for key, val in unit_data["outputs"].items():
            new_data[key] = val
        # filter for outputs created with new multi-stage tasks
        if "this_task_state" in new_data:
            # FIX RANGES
            ranges = new_data["this_task_state"]["ranges"]
            original_bm = new_data["this_task_state"]["broadcastMessage"]
            ranges = [
                r
                for r in ranges
                if r["start"] is not None
                and r["end"] is not None
                and r["text"] == original_bm
            ]
            ranges = [
                r
                for r in ranges
                if r["start"] >= 0
                and r["start"] < len(original_bm)
                and r["end"] >= r["start"]
                and r["end"] < len(original_bm)
            ]
            ranges = sorted(ranges, key=lambda r: r["start"])
            h_map = {}
            for i, r in enumerate(ranges):
                broadcastMessage = new_data["this_task_state"]["broadcastMessage"]
                start = r["start"]
                end = r["end"]
                # print(f"og overlap: {broadcastMessage[start:end+1]}")
                if broadcastMessage[end].isalnum():
                    next_index = end + 1
                    while (
                        next_index < len(broadcastMessage)
                        and broadcastMessage[next_index].isalnum()
                    ):
                        next_index += 1
                    end = next_index - 1
                else:
                    end = end - 1
                if broadcastMessage[start].isalnum():
                    prev_index = start - 1
                    while prev_index >= 0 and broadcastMessage[prev_index].isalnum():
                        prev_index -= 1
                    start = prev_index + 1
                else:
                    start = start + 1
                h_map[broadcastMessage[start : end + 1]] = r["highlighter"]
                # size_original_word = end - start
                # print(f"REPLACE: {broadcastMessage[start:end+1]} with {r['highlighter']}")
                # broadcastMessage = broadcastMessage[:start] + r['highlighter'] + broadcastMessage[end+1:]
                # size_difference = len(r['highlighter']) - size_original_word
                # for j, r2 in enumerate(ranges[i+1:]):
                #     r2['start'] = r2['start'] if r2['start'] < start else r2['start'] + size_difference
                #     r2['end'] = r2['end'] if r2['end'] < end else r2['end'] + size_difference

                # new_data['this_task_state']['broadcastMessage'] = broadcastMessage
            broadcastMessage = original_bm
            for word, highlighter in h_map.items():
                broadcastMessage = broadcastMessage.replace(word, highlighter)
            new_data["this_task_state"]["broadcastMessage"] = broadcastMessage
            if broadcastMessage in previous_messages:
                continue
            # print(f"OUTPUT: {broadcastMessage}")
            # print("-"*100)
            new_data["this_task_state"]["object1"]["attributes"] = []
            new_data["object1"]["attributes"] = [{"name": "", "val": False}]
            new_data["this_task_state"]["object2"]["attributes"] = []
            # new_data['object2']['attributes'] = []
            new_data["object2"]["attributes"] = [[{"name": "", "val": False}]]
            data.append(new_data)
    print(f"len(data): {len(data)}")
    print(data[0])
    # x = 1/0
    return data[:num_tasks]
    # return [{}]  # data[:num_tasks]


def validate_unit(unit):
    if unit.get_assigned_agent() is None:
        return

    print("Task Directory: ", TASK_DIRECTORY)

    data = mephisto_data_browser.get_data_from_unit(unit)["data"]["outputs"]
    print("Data: ", data)

    # constraints = data["constraints"]
    # events = data["events"]

    # front-end already handles basic validation (e.g. all answers exist, aren't inherently invalid)
    validated = True

    # TODO: extra heuristic-based validation

    if not validated:
        print("Unit not validated!")
        unit.get_assigned_agent().soft_reject_work()
        worker = unit.get_assigned_agent().get_worker()
        worker.grant_qualification("ground_events_2_task_block", 1)

    return


# @hydra.main(config_name="scriptconfig")
@hydra.main(config_path="hydra_configs", config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    task_dir = cfg.task_dir

    def onboarding_always_valid(onboarding_data):
        return True

    shared_state = SharedStaticTaskState(
        # static_task_data=create_task_data(cfg.input_file_task, cfg.num_tasks),
        static_task_data=create_task_data(cfg.input_file_tasks, cfg.num_tasks),
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
