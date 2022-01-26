#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os

from pytz import timezone
from datetime import datetime

"""
RAG on WoW to generate dialogue response, with Wiki index
"""

HOURS = 24
GPUS = 4
NOW = datetime.now(timezone("Europe/Zurich")).strftime("%a_%b_%d_%H%M")

here_path = os.path.realpath(__file__).replace(".py", "")
projects = here_path[here_path.find("/projects") :].strip("/")
projects_dir = "/".join(projects.split("/")[:-1])

SWEEP_NAME = projects.split("/")[-1] + "_" + NOW
SAVEROOT = os.path.join("/checkpoint/ladolphs", projects_dir)
PARLAI_HOME_DIR = "/private/home/ladolphs/code/ParlAI"
name_keys = {}

grid = {
    "-t": [
        "wizard_of_wikipedia:Generator --mutators flatten,add_checked_sentence_to_input"
    ],
    # blender args
    "--activation": ["gelu"],
    "--attention-dropout": [0.1],
    "--batchsize": [64, 16],
    "--dropout": [0.1],
    "--fp16": [True],
    "--gradient-clip": [0.1],
    "--label-truncate": [256],
    "--text-truncate": [1024],
    "--log-every-n-secs": [30],
    "--lr-scheduler": ["reduceonplateau"],
    "--max-train-time": [0.98 * HOURS * 60 * 60],
    "--model-parallel": [True],
    "--model": ["bart"],
    "--relu-dropout": [0.0],
    "--save-after-valid": [True],
    "--skip-generation": [True],
    "--optimizer": ["adam"],
    "-lr": [7e-6, 5e-6, 1e-5, 3e-5],
    "-vtim": [60 * 60],
    "-vmm": ["min"],
    "-vmt": ["ppl"],
    "-vp": [10],
    "-tblog": [True],
    # BART Training params
    "--warmup-updates": [500],
}

if __name__ == "__main__":
    run_grid(
        grid,
        name_keys,
        SWEEP_NAME,
        saveroot=os.path.join(SAVEROOT, SWEEP_NAME),
        PARLAI_PATH=PARLAI_HOME_DIR,
        create_model_file=True,
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
        email_updates=True,
        wandb=True,
        one_job_per_node=True,
    )
