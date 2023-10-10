#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os
from pytz import timezone
from datetime import datetime

"""
Evaluating BART agents on light-dialog-wild (dialogue response) and summaryQA
on TEST and with self_say_once.

The metrics, we're interested in are:
    - PPL
    - Token Accuracy
    - F1
    - RF1
"""

HOURS = 2
GPUS = 1

NOW = datetime.now(timezone("Europe/Zurich")).strftime("%a_%b_%d_%H%M")

here_path = os.path.realpath(__file__).replace(".py", "")
projects = here_path[here_path.find("/projects") :].strip("/")
projects_dir = "/".join(projects.split("/")[:-1])

SWEEP_NAME = projects.split("/")[-1] + "_" + NOW
SAVEROOT = os.path.join("/checkpoint/ladolphs", projects_dir)
name_keys = {}

MODELS = [
    # BART trained on light-dialog-wild (no knowledge).
    # '/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_11_Thu_Sep_16_1320/a52/model',
    "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_baseline_bart_light/model",
    # BART trained on summaryQA.
    # '/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_11_Thu_Sep_16_1320/2a8/model',
    "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_baseline_bart_summaryqa/model",
    # BART trained on light-dialog-wild (no knowledge) and summaryQA.
    # '/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_11_Thu_Sep_16_1320/166/model',
    "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_baseline_bart_light_and_summaryqa/model",
]

grid = {
    "-t": [
        # Same as light_dialog_wild but with rare_word_f1 metric.
        "parlai_internal.projects.light.lightqa.lightqa.task.agents:LightTeacherPlus",
        "parlai_internal.projects.light.lightqa.lightqa.task.agents:SummaryQATeacher",
    ],
    "--mutators": ["flatten,self_say_once"],
    "-dt": ["test", "valid"],
    # generation args
    "--log-every-n-secs": [60],
    "--skip-generation": [False],
    "--inference": ["beam"],
    "--beam-min-length": [10],
    "--beam-block-ngram": [3],
    "--beam-context-block-ngram": [-1],
    "--beam-size": [3],
    "--beam-block-full-context": [True],
    "--model-file": MODELS,
    "--batchsize": [16],
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
        partition="learnfair",
        jobtime="{}:00:00".format(HOURS),
        hashname=True,
        requeue=True,
        mem_gb=400,
    )
