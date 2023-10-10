#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os
from pytz import timezone
from datetime import datetime

"""
Evaluating DRM with knowledge on light-dialog-wild (with noun chunks provided).
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
    # Trained on lightNC (light-dialog-wild with a noun chunk of the target utterance as knowledge).
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_8_Thu_Sep_09_1026/d39/model",
]

grid = {
    "-t": [
        "parlai_internal.projects.light.lightqa.lightqa.task.agents:LightDialogueNounChunk:"
        "lightnc-labeltype=dialogue_response:"
        "lightnc-knowledge-provided=knowledge_response"
    ],
    "--mutators": ["flatten"],
    "-mf": MODELS,
    "-dt": ["valid"],
    # generation args
    "--skip-generation": [False],
    "--inference": ["beam"],
    "--beam-min-length": [1, 10, 20],
    "--beam-size": [3, 10],
    "--beam-context-block-ngram": [-1],
    "--beam-block-full-context": [True],
    "--log-every-n-secs": [60],
    "--batchsize": [16],
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
        partition="devlab",
        jobtime="{}:00:00".format(HOURS),
        hashname=True,
        requeue=True,
        mem_gb=400,
    )
