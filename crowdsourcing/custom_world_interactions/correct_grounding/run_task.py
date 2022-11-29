#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import random
import shutil
import subprocess
import time
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
from typing import List, Any, Optional

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LIGHT_DB_PATH = "/checkpoint/light/db/prod"
# LIGHT_DB_PATH = "/Users/jju/LIGHT/prod_db"
DATA_BASE_PATH = os.path.join(TASK_DIRECTORY, "../collect_narrations/out_data/results.json")

SECONDARY_OBJECT_LIST_SIZE = 6
DEFAULT_NUM_TASKS = 20

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

defaults = [
    "_self_",
    {"mephisto/blueprint": BLUEPRINT_TYPE},
    {"mephisto/architect": "local"},
    {"mephisto/provider": "mock"},
    {"conf": "base"},
]

from mephisto.operations.hydra_config import RunScriptConfig, register_script_config


@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY
    light_db_path: str = LIGHT_DB_PATH
    num_tasks: int = DEFAULT_NUM_TASKS
    force_rebuild: bool = False
    qualify_new_workers: bool = False
    allowlist_qualification: Optional[str] = None


def load_unannotated_entries():
    with open(DATA_BASE_PATH, 'r') as data_file:
        data = json.load(data_file)
    
    print(f"{len(data)} interactions logged")
    model_annotated_data = [e for e in data.values() if e['object_attributes']['after'] is not None]
    print(f"{len(model_annotated_data)} interactions currently model-annotated" )
    not_human_annotated_data = [e for e in model_annotated_data if e['edit_data'] is None]
    print(f"{len(not_human_annotated_data)} interactions needing human annotation")
    return not_human_annotated_data

def get_task_data(num_tasks):
    valid_entries = load_unannotated_entries()
    random.shuffle(valid_entries)
    return valid_entries[:num_tasks]

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
    start_time = unit_data.get("task_start")
    end_time = unit_data.get("task_end", time.time())
    data = unit_data.get("data")

    if data is None:
        return

    outputs = data.get("outputs")

    failure_reason = ""
    task_duration = end_time - start_time
    if (task_duration < 300):
        failure_reason += f"Too quick! {task_duration}\n"
    if (len(outputs['updatedNarration']) < 20):
        failure_reason += f"New narration too short! {outputs['updatedNarration']}\n"
    if (len(outputs['externalPerspective']) < 20):
        failure_reason += f"New external too short! {outputs['externalPerspective']}\n"
    if ("{actor}" not in outputs['externalPerspective']):
        failure_reason += f"New external missing actor! {outputs['externalPerspective']}\n"
    for desc in outputs['finalDescriptions'].values():
        if len(desc) < 10:
            failure_reason += f"Object description too short {desc}\n"
    for location in outputs['finalLocations'].values():
        start_found = False
        for valid_start in ["original location", "held by", "worn by", "wielded by", "in", "on"]:
            start_found = start_found or location.lower().startswith(valid_start)
        if not start_found:
            failure_reason += f"Object location doesn't follow pattern: {location}\n"
    for attMap in outputs['beforeAttributes'].values():
        for att, reason in attMap.items():
            if att == 'EXTRAS':
                continue
            if not (reason.lower().startswith('required') or reason.lower().startswith("not required")):
                failure_reason += f"Attribute {att} doesn't follow pattern: {reason}\n"
    for attMap in outputs['afterAttributes'].values():
        for att, reason in attMap.items():
            if att == 'EXTRAS':
                continue
            if not (reason.lower().startswith('required') or reason.lower().startswith("not required")):
                failure_reason += f"Attribute {att} doesn't follow pattern: {reason}\n"
    
    if failure_reason != "":
        # unit.get_assigned_agent().soft_reject_work() => must wait for async version
        worker = unit.get_assigned_agent().get_worker()
        worker.grant_qualification("collect_narrations_task_block", 1)
        print(f"Worker granted block because: \n{failure_reason}")
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

    db, cfg = load_db_and_process_config(cfg)

    using_allowlist = cfg.allowlist_qualification
    if cfg.allowlist_qualification != None:
        existing_qualifications = [
            make_qualification_dict(cfg.allowlist_qualification, QUAL_EXISTS, None),
        ]

    shared_state = SharedStaticTaskState(
        static_task_data=get_task_data(cfg.num_tasks),
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
                "IntegerValues": [98],
                "ActionsGuarded": "DiscoverPreviewAndAccept",
            },
        ]

    built_file = os.path.join(task_dir, "webapp", "build", "bundle.js")
    if cfg.force_rebuild or not os.path.exists(built_file):
        build_task(task_dir)

    db, cfg = load_db_and_process_config(cfg)
    operator = Operator(db)
    operator.validate_and_run_config(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=600)


if __name__ == "__main__":
    main()
