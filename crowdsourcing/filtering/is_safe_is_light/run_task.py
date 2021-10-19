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
from mephisto.abstractions.blueprints.mixins.use_gold_unit import get_gold_factory
from light.data_model.light_database import LIGHTDatabase
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.data_model.worker import Worker
from mephisto.data_model.unit import Unit

import hydra
import json
import random
import pandas as pd
import numpy as np
from omegaconf import DictConfig, MISSING
from dataclasses import dataclass, field
from typing import List, Any, Tuple, Dict

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
GOLD_FOLDER = os.path.join(TASK_DIRECTORY, "data", "golds")
TARGET_FOLDER = os.path.join(TASK_DIRECTORY, "data", "targets")
DEFAULT_UNITS_PER_RUN = 10
DEFAULT_ANNOTATIONS_PER_UNIT = 5

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
    gold_path: str = MISSING
    target_file: str = MISSING
    units_per_run: int = DEFAULT_UNITS_PER_RUN
    annotations_per_unit: int = DEFAULT_ANNOTATIONS_PER_UNIT


def create_task_data(
    num_tasks,
    annotations_per_unit,
    annotation_source,
):
    df = pd.read_csv(annotation_source)

    # TODO sort based on least confident of safe or LIGHT

    df_dict_list = df.to_dict("records")

    remaining_annotations = len(df["annotations"]) - df["annotations"].sum()
    if remaining_annotations < num_tasks * annotations_per_unit:
        print(
            f"Not enough data for the tasks present, only launching  "
            f"{remaining_annotations // num_tasks + 1} rather than {num_tasks}"
        )
        num_tasks = remaining_annotations // num_tasks + 1

    tasks = []
    curr_idx = 0
    while len(tasks) < num_tasks:
        subtasks = []
        while len(subtasks) < annotations_per_unit:
            entry = df_dict_list[curr_idx]
            curr_idx = (curr_idx + 1) % len(df_dict_list)
            if entry["annotations"]:
                continue
            subtasks.append(
                {
                    "text": entry["text"],
                }
            )
            df["launched"] = df.apply(
                lambda x: x["launched"] + 1
                if x["text"] == entry["text"]
                else x["launched"],
                axis=1,
            )
        tasks.append(
            {
                "texts": subtasks,
            }
        )

    return tasks


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


SafeLightAnnotation = Dict[str, bool]
FrontendSubUnit = Dict[str, str]
GoldTask = Dict[str, List[FrontendSubUnit]]


def make_golds(
    gold_path: str,
    annotations_per_unit: int,
) -> Tuple[Dict[str, SafeLightAnnotation], List[GoldTask]]:
    """
    Given a gold folder, returns an id->gold label dict as well as a
    list of gold annotations
    """
    goldframe = pd.read_csv(gold_path)
    gold_dict_list = goldframe.to_dict("records")
    golds = []
    gold_map = {}
    random.shuffle(gold_dict_list)
    idx = 0
    while len(gold_dict_list) >= annotations_per_unit:
        sub_golds = gold_dict_list[-annotations_per_unit:]
        gold_dict_list = gold_dict_list[:-annotations_per_unit]
        task_texts = []
        for gold in sub_golds:
            task_texts.append({"id": idx, "text": gold["text"]})
            gold_map[idx] = {
                "is_safe": gold["is_safe"],
                "is_light": gold["is_light"],
            }
            idx += 1
        task = {"texts": task_texts}
        golds.append(task)
    return gold_map, golds


@hydra.main(config_path="hydra_configs", config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    task_dir = cfg.task_dir
    target_path = os.path.join(task_dir, cfg.target_file)
    gold_path = os.path.join(task_dir, cfg.gold_path)

    def onboarding_always_valid(onboarding_data):
        return True

    gold_answers, gold_questions = make_golds(gold_path, cfg.annotations_per_unit)

    def unit_matches_gold(unit) -> bool:
        """
        Check against the answer list for the given ID to return
        if the given unit's data matches
        """
        if unit.get_assigned_agent() is None:
            return False

        data = unit.get_assigned_agent().state.get_data()
        print(data, gold_answers)
        return False

    validate_unit = StaticGoldBlueprint.create_validation_function(
        cfg.mephisto, unit_matches_gold
    )

    shared_state = StaticGoldSharedState(
        static_task_data=create_task_data(
            cfg.units_per_run,
            cfg.annotations_per_unit,
            target_path,
        ),
        on_unit_submitted=validate_unit,
        get_gold_for_worker=get_gold_factory(gold_questions),
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
