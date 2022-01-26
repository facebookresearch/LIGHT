#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os
from pytz import timezone
from datetime import datetime

"""
Evaluating BART agents on light-dialog-wild (dialogue response).

The metrics, we're interested in are:
    - PPL
    - Token Accuracy
    - F1
    - RF1
"""

HOURS = 2
GPUS = 2

NOW = datetime.now(timezone("Europe/Zurich")).strftime("%a_%b_%d_%H%M")

here_path = os.path.realpath(__file__).replace(".py", "")
projects = here_path[here_path.find("/projects") :].strip("/")
projects_dir = "/".join(projects.split("/")[:-1])

SWEEP_NAME = projects.split("/")[-1] + "_" + NOW
SAVEROOT = os.path.join("/checkpoint/ladolphs", projects_dir)
PARLAI_HOME_DIR = "/private/home/ladolphs/code/ParlAI"
name_keys = {}

MODELS = [
    # BART trained on light-dialog-wild (no knowledge).
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_11_Thu_Sep_16_1320/a52/model",
    # BART trained on summaryQA.
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_11_Thu_Sep_16_1320/2a8/model",
    # BART trained on light-dialog-wild (no knowledge) and summaryQA.
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_11_Thu_Sep_16_1320/166/model",
]

grid = {
    "-t": [
        # Same as light_dialog_wild but with rare_word_f1 metric.
        "parlai_internal.projects.light.lightqa.lightqa.task.agents:LightTeacherPlus"
    ],
    "--mutators": ["flatten,self_say_once"],
    "-dt": ["valid"],
    # generation args
    "--fp16": [True],
    "--log-every-n-secs": [60],
    "--skip-generation": [False],
    "--inference": ["beam"],
    "--beam-min-length": [1, 10],
    "--beam-block-ngram": [3],
    "--beam-context-block-ngram": [-1],
    "--beam-size": [3, 10],
    "--beam-block-full-context": [True],
    "--model-file": MODELS,
    "--batchsize": [8],
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
