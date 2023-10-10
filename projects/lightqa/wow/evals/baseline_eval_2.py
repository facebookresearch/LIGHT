#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os
from pytz import timezone
from datetime import datetime

"""
Evaluating StackedAgent on WoW.
"""

HOURS = 20
GPUS = 1

NOW = datetime.now(timezone("Europe/Zurich")).strftime("%a_%b_%d_%H%M")

here_path = os.path.realpath(__file__).replace(".py", "")
projects = here_path[here_path.find("/projects") :].strip("/")
projects_dir = "/".join(projects.split("/")[:-1])

SWEEP_NAME = projects.split("/")[-1] + "_" + NOW
SAVEROOT = os.path.join("/checkpoint/ladolphs", projects_dir)
name_keys = {}


MODELS = [
    # BARt
    "/checkpoint/kshuster/projects/wizard_2.0/parlai_sweeps/take2_bart_sweep44_Sat_Mar_27/cb8/model",
    "/checkpoint/kshuster/projects/wizard_2.0/parlai_sweeps/take2_bart_sweep6_Mon_Feb_22/d22/model",
]


grid = {
    "-t": [
        "wizard_of_wikipedia:WizardDialogKnowledge:random_split",
        "wizard_of_wikipedia:WizardDialogKnowledge:topic_split",
    ],
    "--datatype": ["test"],
    "--include-knowledge-separator": [True],
    # blender args
    "--fp16": [False, True],
    "--log-every-n-secs": [30],
    "--model-parallel": [True],
    "--skip-generation": [False],
    "--inference": ["beam"],
    "--beam-min-length": [20],
    "--beam-block-ngram": [3],
    "--beam-context-block-ngram": [-1],
    "--beam-size": [3],
    "--beam-block-full-context": [True],
    "--model-file": MODELS,
    "--metrics": ["all"],
    "--n-docs": ["5 --batchsize 2", "25 --batchsize 1"],
}

if __name__ == "__main__":
    run_grid(
        grid,
        {},
        SWEEP_NAME,
        saveroot=os.path.join(SAVEROOT, SWEEP_NAME),
        prefix="python -m parlai.scripts.eval_model",
        create_model_file=False,
        include_job_id=False,
        gpus=GPUS,
        data_parallel=True,
        copy_env=True,
        nodes=1,
        cpus=10,
        volta=True,
        volta32=True,
        partition="devlab",
        jobtime="{}:00:00".format(HOURS),
        hashname=True,
        requeue=True,
        mem_gb=400,
    )
