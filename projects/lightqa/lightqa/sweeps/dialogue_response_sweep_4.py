#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Train BART model on dialogueoverlap response (overlapdialogue).

Here, we try to train a dialogue model on light-wild chat data where we condition the
model with knowledge. The knowledge is a noun chunk from the target utterance. With
probability p choose wrong knowledge.
"""

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os

from pytz import timezone
from datetime import datetime

HOURS = 10
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
        "parlai_internal.projects.light.lightqa.lightqa.task.agents:LightQATeacher:"
        "lightqa_dataname=overlapdialogue:"
        "lightqa_labeltype=dialogue_response:"
        "lightqa_overlapdialogue_wrong_prob=0.1,"
        "parlai_internal.projects.light.lightqa.task.agents:LightQATeacher:"
        "lightqa_dataname=overlap:"
        "lightqa_labeltype=dialogue_response"
    ],
    "--lightqa_knowledge_provided": ["knowledge_response_answer"],
    ## -------------------------------------------------------
    "--max-train-time": [(60 * 60) * HOURS * 0.96],
    "--max-train-steps": [10000],
    "--model": ["bart"],
    "--tensorboard-log": [True],
    ## -------------------------------------------------------
    "--multitask_weights": ["1,1"],
    "--validation-every-n-steps": [500],
    "--batchsize": [8],
    "--fp16": [True],
    "--label-truncate": [512],
    "-lr": [1e-2, 5e-2, 1e-1],
    "--lr-scheduler": ["reduceonplateau"],
    "--save-after-valid": [True],
    "--text-truncate": [512],
    "--warmup-updates": [100],
    "--update-freq": [2],
    "--gradient-clip": [1.0],
    "--validation-patience": [20],
    "--validation-metric": ["ppl"],
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
