#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os
from pytz import timezone
from datetime import datetime

"""
Evaluating StackedAgent on NQ.
"""

HOURS = 4
GPUS = 4

NOW = datetime.now(timezone("Europe/Zurich")).strftime("%a_%b_%d_%H%M")

here_path = os.path.realpath(__file__).replace(".py", "")
projects = here_path[here_path.find("/projects") :].strip("/")
projects_dir = "/".join(projects.split("/")[:-1])

SWEEP_NAME = projects.split("/")[-1] + "_" + NOW
SAVEROOT = os.path.join("/checkpoint/ladolphs", projects_dir)
PARLAI_HOME_DIR = "/private/home/ladolphs/code/ParlAI"
name_keys = {}

MODELS = [
    # rag-wiki model
    "/private/home/ladolphs/code/ParlAI/data/models/hallucination/bart_rag_token/model",
    # no-knowledge model trained on wow data
    "/checkpoint/kshuster/projects/wizard_2.0/parlai_sweeps/bart_sweep1_Fri_Oct__2/395/model",
]

grid = {
    "-t": ["parlai_internal.projects.light.lightqa.nq_open.task.agents:NQOpenTeacher"],
    "-mf": MODELS,
    "-dt": ["test"],
    # generation args
    "--inference": ["beam"],
    "--beam-min-length": [1, 10, 20, 30],
    "--skip-generation": [False],
    "--beam-size": [3, 10, 20, 30],
    "--log-every-n-secs": [120],
    "--batchsize": [2],
    "--metrics": ["all"],
}

if __name__ == "__main__":
    run_grid(
        grid,
        {},
        SWEEP_NAME,
        saveroot=os.path.join(SAVEROOT, SWEEP_NAME),
        PARLAI_PATH=PARLAI_HOME_DIR,
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
        partition="learnfair",
        jobtime="{}:00:00".format(HOURS),
        hashname=True,
        requeue=True,
        mem_gb=400,
    )
