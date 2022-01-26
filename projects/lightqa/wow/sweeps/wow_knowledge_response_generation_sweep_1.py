#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os

from pytz import timezone
from datetime import datetime

"""
RAG on WoW to generate knowledge response, with Wiki index
"""

HOURS = 48
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
    "-t": ["wizard_of_wikipedia:Generator"],
    "--mutators": ["flatten,checked_sentence_as_label"],
    # blender args
    "--activation": ["gelu"],
    "--attention-dropout": [0.0],
    "--batchsize": [16],
    "--dropout": [0.1],
    "--fp16": [True],
    "--gradient-clip": [0.1],
    "--label-truncate": [128],
    "--text-truncate": [512],
    "--log-every-n-secs": [30],
    "--lr-scheduler": ["reduceonplateau"],
    "--lr-scheduler-patience": [1],
    "--max-train-time": [0.98 * HOURS * 60 * 60],
    "--model-parallel": [True],
    "--model": ["rag -o arch/bart_large"],
    "--init-model": [
        "zoo:bart/bart_large/model --dict-file zoo:bart/bart_large/model.dict",
    ],
    "--warmup-updates": [0],
    "--multitask-weights": ["stochastic"],
    "--relu-dropout": [0.0],
    "--save-after-valid": [True],
    "--skip-generation": [True],
    "-lr": [1e-5, 5e-5],
    "-vmm": ["min"],
    "-veps": [0.25],
    "-vme": [1000],
    "-vmt": ["ppl"],
    "-vp": [5],
    ## Rag params
    "--n-docs": [5],
    "-tblog": [True],
    "--compressed-indexer-nprobe": [128],
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
        copy_env=True,
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
    )
