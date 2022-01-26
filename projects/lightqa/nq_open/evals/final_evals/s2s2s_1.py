#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os
from pytz import timezone
from datetime import datetime

"""
Evaluating StackedAgent on NQ.
"""

HOURS = 4
GPUS = 2

NOW = datetime.now(timezone("Europe/Zurich")).strftime("%a_%b_%d_%H%M")

here_path = os.path.realpath(__file__).replace(".py", "")
projects = here_path[here_path.find("/projects") :].strip("/")
projects_dir = "/".join(projects.split("/")[:-1])

SWEEP_NAME = projects.split("/")[-1] + "_" + NOW
SAVEROOT = os.path.join("/checkpoint/ladolphs", projects_dir)
name_keys = {}

MODELS = {
    "knowledge_response": [
        # T5 fid trained on NQ
        # '/checkpoint/mpchen/projects/chatty_tasks/qa/t5fid/t9b_nq_singleValSweep_notCompressedMon_May_24/b09/model',
        "/checkpoint/light/projects/lightqa/nq_open/models/nq_krm_t5/model",
        # Oracle
        "oracle",
    ],
    "dialogue_response": [
        # '/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_sweep_3_Wed_Aug_18_2130/ad6/model',
        "/checkpoint/light/projects/lightqa/nq_open/models/nq_drm_bart/model",
    ],
}

grid = {
    "-t": ["parlai_internal.projects.light.lightqa.nq_open.task.agents:NQOpenTeacher"],
    "-m": [
        "parlai_internal.projects.light.lightqa.seq2seq2seq.task.agents:StackedKnowledgeDialogueAgent"
    ],
    "--knowledge-response-model-path": MODELS["knowledge_response"],
    "--dialogue-response-model-path": MODELS["dialogue_response"],
    "--dialogue-response-no-knowledge-model-path": ["None"],
    "--dialogue-response-rag-wiki-model-path": ["None"],
    "-dt": ["test", "valid"],
    # generation args
    "--krm-beam-min-length": [1],
    "--drm-beam-min-length": [1],
    "--drm-beam-size": [3, 30],
    "--beam-filter-for-knowledge-response": [True, False],
    "--log-every-n-secs": [120],
    "--batchsize": [16],
    "--metrics": ["all"],
    "--drm-skip-generation": [False],
    "--krm-skip-generation": [False],
    "--krm-path-to-index": [
        "/private/home/ladolphs/code/ParlAI/data/models/hallucination/wiki_index_exact/exact"
    ],
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
