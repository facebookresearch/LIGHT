#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os
from pytz import timezone
from datetime import datetime

"""
Evaluating StackedAgent on WoW.
"""

HOURS = 20
GPUS = 1

NOW = datetime.now(timezone("Europe/Zurich")).strftime("%a_%b_%d_%H%M")

here_path = os.path.realpath(__file__).replace(".py", "")
projects = here_path[here_path.find("/projects") :].strip("/")
projects_dir = "/".join(projects.split("/")[:-1])

SWEEP_NAME = projects.split("/")[-1] + "_" + NOW
SAVEROOT = os.path.join("/checkpoint/ladolphs", projects_dir)
PARLAI_HOME_DIR = "/private/home/ladolphs/code/ParlAI"
name_keys = {}

MODELS = {
    "knowledge_response": [
        # trained on --indexer-type exact
        "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_shared_model_sweep_1_Wed_Oct_06_1745/1df/model",
        "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_shared_model_sweep_1_Wed_Oct_06_1745/40f/model",
    ],
    "dialogue_response": [
        "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_shared_model_sweep_1_Wed_Oct_06_1745/1df/model",
        "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_shared_model_sweep_1_Wed_Oct_06_1745/40f/model",
    ],
}

grid = {
    "-t": [
        "parlai_internal.projects.light.lightqa.wow.task.agents:WizardOfWikipediaGeneratorTeacher:topic_split",
        "parlai_internal.projects.light.lightqa.wow.task.agents:WizardOfWikipediaGeneratorTeacher:random_split",
    ],
    "-m": [
        "parlai_internal.projects.light.lightqa.seq2seq2seq.task.agents:StackedKnowledgeDialogueAgent"
    ],
    "--knowledge-response-model-path": MODELS["knowledge_response"],
    "--dialogue-response-model-path": MODELS["dialogue_response"],
    "--dialogue-response-no-knowledge-model-path": ["None"],
    "--dialogue-response-rag-wiki-model-path": ["None"],
    "--mutators": ["flatten"],
    "-dt": ["test"],
    # generation args
    "--krm-indexer-type": ["exact"],
    "--drm-indexer-type": ["exact"],
    "--krm-fp16": [False],
    "--drm-fp16": [False],
    "--krm-model-parallel": [False],
    "--drm-model-parallel": [False],
    "--krm-beam-min-length": [5, 10],
    "--krm-beam-size": [3, 5],
    "--drm-beam-size": [3],
    "--drm-beam-min-length": [20],
    "--krm-n-docs": [5],
    "--drm-n-docs": [5],
    "--batchsize": [2],
    "--log-every-n-secs": [30],
    "--metrics": ["all"],
}

if __name__ == "__main__":
    run_grid(
        grid,
        {},
        SWEEP_NAME,
        saveroot=os.path.join(SAVEROOT, SWEEP_NAME),
        # PARLAI_PATH=PARLAI_HOME_DIR,
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
