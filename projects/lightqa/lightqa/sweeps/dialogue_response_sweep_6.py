#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Train BART model for dialogue response on LIGHT-NC (includes knowledge).
"""

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os

from pytz import timezone
from datetime import datetime

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
        "parlai_internal.projects.light.lightqa.lightqa.task.agents:LightDialogueNounChunk:"
        "lightnc-labeltype=dialogue_response:"
        "lightnc-knowledge-provided=knowledge_response"
    ],
    "--activation": ["gelu"],
    "--attention-dropout": [0.1],
    "--batchsize": [8, 32],
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
        partition="learnfair",
        jobtime="{}:00:00".format(HOURS),
        PARLAI_PATH=PARLAI_HOME_DIR,
        gpus=GPUS,
        nodes=1,
        cpus=10,
        volta=True,
        volta32=True,
        saveroot=os.path.join(SAVEROOT, SWEEP_NAME),
        include_job_id=False,
        create_model_file=True,
        hashname=True,
        requeue=True,
        mem_gb=400,
        data_parallel=True,
        one_job_per_node=True,
        copy_env=False,
        wandb=True,
    )
