#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import shutil
import subprocess
from mephisto.operations.operator import Operator
from mephisto.operations.utils import get_root_dir
from mephisto.tools.scripts import load_db_and_process_config
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.abstractions.blueprints.static_react_task.static_react_blueprint import (
    BLUEPRINT_TYPE,
)
from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    SharedStaticTaskState,
)
from mephisto.data_model.qualification import QUAL_NOT_EXIST, make_qualification_dict

import hydra
from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import List, Any

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

defaults = [
    {"mephisto/blueprint": BLUEPRINT_TYPE},
    {"mephisto/architect": "local"},
    {"mephisto/provider": "mock"},
    {"conf": "example"},
]

from mephisto.operations.hydra_config import RunScriptConfig, register_script_config


@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY


register_script_config(name="scriptconfig", module=TestScriptConfig)


# TODO it would be nice if this was automated in the way that it
# is for ParlAI custom frontend tasks
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


CURRENT_START = 50000
CURRENT_END = 94000


@hydra.main(config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    task_dir = cfg.task_dir
    db, cfg = load_db_and_process_config(cfg)

    def onboarding_always_valid(onboarding_data):
        return True


    with open('/private/home/jju/LIGHT/scripts/safety/out/turns_to_eval.txt', 'r') as eval_file:
        lines = eval_file.readlines()

    lines_to_work_on = lines[CURRENT_START:CURRENT_END]

    split_lines = [lines_to_work_on[i:i + 10] for i in range(0, len(lines_to_work_on), 10)]

    task_data = [{"text_lines": l} for l in split_lines]


    mephisto_data_browser = MephistoDataBrowser(db=db)

    def validate_final_unit(unit):
        try:
            u_data = mephisto_data_browser.get_data_from_unit(unit)
        except AssertionError:
            return  # unit was not final...
        ratings = u_data['data']['outputs']['final_data']['ratings']
        false_count = 20 - sum([sum([int(t) for t in turn_ratings]) for turn_ratings in ratings])
        if (false_count > 8):
            worker = unit.get_assigned_agent().get_worker()
            worker.grant_qualification('can-write-light-quests-live-failed', 1)

    shared_state = SharedStaticTaskState(
        static_task_data=task_data,
        validate_onboarding=onboarding_always_valid,
        validate_final_unit=validate_final_unit,
    )

    shared_state.qualifications = [
        make_qualification_dict(
            'can-write-light-quests-live-failed',
            QUAL_NOT_EXIST,
            None,
        )
    ]

    # build_task(task_dir)

    operator = Operator(db)

    operator.validate_and_run_config(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
