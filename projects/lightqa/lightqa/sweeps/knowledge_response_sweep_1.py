#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Train BART model on knowledge response (overlap).
"""

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os

from pytz import timezone
from datetime import datetime

HOURS = 4
GPUS = 4
NOW = datetime.now(timezone("Europe/Zurich")).strftime("%a_%b__%w_%H%M")

here_path = os.path.realpath(__file__).replace(".py", "")
projects = here_path[here_path.find("/projects") :].strip("/")
projects_dir = "/".join(projects.split("/")[:-1])

SWEEP_NAME = projects.split("/")[-1] + "_" + NOW
SAVEROOT = os.path.join("/checkpoint/ladolphs", projects_dir)
PARLAI_HOME_DIR = "/private/home/ladolphs/code/ParlAI"
name_keys = {}

grid = {
    "-t": ["parlai_internal.projects.light.lightqa.lightqa.task.agents:LightQATeacher"],
    ## LIGHT-QA Flags ---------------------------------------
    "--lightqa_dataname": ["overlap"],
    "--lightqa_labeltype": ["knowledge_response_answer", "knowledge_response_sentence"],
    "--lightqa_knowledge_provided": [
        "None",
    ],
    ## -------------------------------------------------------
    "--max-train-time": [(60 * 60) * HOURS * 0.96],
    "--max-train-steps": [10000],
    "--model": ["bart"],
    "--tensorboard-log": [True],
    ## -------------------------------------------------------
    "--validation-every-n-steps": [500],
    "--batchsize": [4],
    "--fp16": [True],
    "--label-truncate": [512],
    "-lr": [1e-4, 1e-5, 1e-3],
    "--lr-scheduler": ["reduceonplateau"],
    "--save-after-valid": [True],
    "--text-truncate": [512],
    "--warmup-updates": [100],
    "--update-freq": [2],
    "--gradient-clip": [1.0],
    # "--skip-generation": [True],
    "--validation-patience": [20],
    "--validation-metric": ["token_acc"],  # should be token_em for QA task
    "--validation-metric-mode": ["max"],
    "--dynamic-batching": ["full"],
    "-tblog": ["true"],
    "--load-from-checkpoint": ["true"],
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
        include_job_id=True,
        create_model_file=True,
        hashname=True,
        requeue=True,
        mem_gb=400,
        data_parallel=True,
        one_job_per_node=True,
        copy_env=False,
        wandb=True,
    )
