#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os
from pytz import timezone
from datetime import datetime

"""
Evaluating RAG on WoW checked sentence prediction.
"""

HOURS = 20
GPUS = 8

NOW = datetime.now(timezone("Europe/Zurich")).strftime("%a_%b_%d_%H%M")

here_path = os.path.realpath(__file__).replace(".py", "")
projects = here_path[here_path.find("/projects") :].strip("/")
projects_dir = "/".join(projects.split("/")[:-1])

SWEEP_NAME = projects.split("/")[-1] + "_" + NOW
SAVEROOT = os.path.join("/checkpoint/ladolphs", projects_dir)
PARLAI_HOME_DIR = "/private/home/ladolphs/code/ParlAI"
name_keys = {}

MODELS = [
    # trained on --indexer-type compressed
    "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_knowledge_response_generation_sweep_1_Tue_Aug_17_1822/9aa/model",
    # trained on --indexer-type exact
    "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_knowledge_response_generation_sweep_3_Sat_Aug_28_0811/35e/model",
]

grid = {
    "-t": ["wizard_of_wikipedia:Generator"],
    "--mutators": ["flatten,checked_sentence_as_label"],
    "-dt": ["valid:stream"],
    # generation args
    "--fp16": [True],
    "--log-every-n-secs": [60],
    "--model-parallel": [True],
    "--skip-generation": [False],
    "--inference": ["beam"],
    "--beam-min-length": [1, 10, 20],
    "--beam-block-ngram": [3],
    "--beam-context-block-ngram": [-1],
    "--beam-size": [3],
    "--beam-block-full-context": [True],
    "--model-file": MODELS,
    "--batchsize": [8],
    "--metrics": ["all"],
    "--indexer-type": ["exact"],
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
    )
