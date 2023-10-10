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
GPUS = 2

NOW = datetime.now(timezone("Europe/Zurich")).strftime("%a_%b_%d_%H%M")

here_path = os.path.realpath(__file__).replace(".py", "")
projects = here_path[here_path.find("/projects") :].strip("/")
projects_dir = "/".join(projects.split("/")[:-1])

SWEEP_NAME = projects.split("/")[-1] + "_" + NOW
SAVEROOT = os.path.join("/checkpoint/ladolphs", projects_dir)
name_keys = {}

MODELS = [
    # No knowledge WoW baseline
    "/checkpoint/kshuster/projects/wizard_2.0/parlai_sweeps/bart_sweep1_Fri_Oct__2/395/model",
    # BART RAG DPR
    "/checkpoint/kshuster/projects/wizard_2.0/parlai_sweeps/take2_bart_sweep44_Sat_Mar_27/cb8/model --n-docs 5",
]

grid = {
    "-t": [
        "parlai_internal.projects.light.lightqa.wow.task.agents:WizardOfWikipediaGeneratorTeacher:topic_split",
        "parlai_internal.projects.light.lightqa.wow.task.agents:WizardOfWikipediaGeneratorTeacher:random_split",
    ],
    "-mf": MODELS,
    "--mutators": ["flatten"],
    "-dt": ["test"],
    "--include-knowledge-separator": [True],
    # generation args
    "--fp16": [False],
    "--inference": ["beam"],
    "--beam-min-length": [20],
    "--beam-block-ngram": [3],
    "--beam-context-block-ngram": [-1],
    "--beam-size": [3],
    "--beam-block-full-context": [True],
    "--skip-generation": [False],
    # ------------------------
    "--log-every-n-secs": [120],
    "--batchsize": [4],
    "--metrics": ["all"],
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
        copy_env=False,
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
