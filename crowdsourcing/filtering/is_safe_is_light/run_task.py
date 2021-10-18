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
from static_gold_blueprint import (
    BLUEPRINT_TYPE,
    StaticGoldBlueprint,
    StaticGoldBlueprintArgs,
    StaticGoldSharedState,
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
from typing import List, Any, Tuple, Dict

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
GOLD_FOLDER = os.path.join(TASK_DIRECTORY, "data", "golds")
TARGET_FOLDER = os.path.join(TASK_DIRECTORY, "data", "targets")
DEFAULT_UNITS_PER_RUN = 30
DEFAULT_ANNOTATIONS_PER_UNIT = 10

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

default_config = [
    "_self_",
    {"mephisto/blueprint": BLUEPRINT_TYPE},
    {"conf": "is_safe_is_light_task"},
]

from mephisto.operations.hydra_config import RunScriptConfig, register_script_config


@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: default_config)
    task_dir: str = TASK_DIRECTORY
    gold_path: str = GOLD_FOLDER
    target_folder: str = TARGET_FOLDER
    units_per_run: int = DEFAULT_UNITS_PER_RUN
    annotations_per_unit: int = DEFAULT_ANNOTATIONS_PER_UNIT


def create_task_data(
    num_tasks,
    annotations_per_unit,
    annotation_source,
):
    task_data_array = [{}]

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


def make_golds(
    gold_path: str,
) -> Tuple[Dict[str, Dict[str, bool]], Dict[str, Dict[str, str]]]:
    """
    Given a gold folder, returns an id->gold label dict as well as an id->annotation dict
    """
    pass


@hydra.main(config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    task_dir = cfg.task_dir

    def onboarding_always_valid(onboarding_data):
        return True

    gold_answers, gold_questions = make_golds(cfg.gold_path)

    def unit_matches_gold(unit) -> bool:
        """
        Check against the answer list for the given ID to return
        if the given unit's data matches
        """
        return False

    validate_unit = StaticGoldBlueprint.create_validation_function(
        cfg.mephisto, unit_matches_gold
    )

    shared_state = StaticGoldSharedState(
        static_task_data=create_task_data(
            cfg.units_per_run,
            cfg.annotations_per_unit,
            cfg.target_folder,
        ),
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
