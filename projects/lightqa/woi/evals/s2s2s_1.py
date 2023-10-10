#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os
from pytz import timezone
from datetime import datetime

"""
Evaluating StackedAgent on WoI.
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
    "knowledge_model": [
        "/checkpoint/light/projects/lightqa/woi/models/woi_fidgold",
        # Oracle
        "oracle",
    ],
    "dialogue_model": [
        # BB2.7B
        "/checkpoint/kshuster/projects/wizard_internet/woi_sweep7_Wed_Jun__2/967/model",
        # BB400m
        "/checkpoint/kshuster/projects/wizard_internet/woi_sweep4_Wed_Jun__2/cb2/model",
        # BART
        "/checkpoint/kshuster/projects/wizard_internet/woi_sweep5_Wed_Jun__2/58b/model",
        # T5-Large
        "/checkpoint/kshuster/projects/wizard_internet/woi_sweep6_Wed_Jun__2/99a/model",
    ],
}


grid = {
    "-t": [
        "internal:wizard_of_internet:WizardDialogTeacher --speaker-tags false --include-checked-sentence false",
    ],
    "-m": [
        "parlai_internal.projects.light.lightqa.seq2seq2seq.task.agents:StackedKnowledgeDialogueAgent"
    ],
    "--knowledge-response-model-path": MODELS["knowledge_model"],
    "--dialogue-response-model-path": MODELS["dialogue_model"],
    "--dialogue-response-no-knowledge-model-path": ["None"],
    "--dialogue-response-rag-wiki-model-path": ["None"],
    "--mutators": ["flatten"],
    "-dt": ["test", "valid"],
    # generation args
    "--krm-fp16": [False],
    "--drm-fp16": [False],
    "--krm-model-parallel": [False],
    "--drm-model-parallel": [False],
    "--krm-skip-generation": [False],
    "--krm-inference": ["beam"],
    "--krm-beam-size": [3],
    "--krm-beam-min-length": [10, 15, 20],
    "--krm-beam-block-ngram": [3],
    "--krm-beam-context-block-ngram": [-1],
    "--drm-skip-generation": [False],
    "--drm-inference": ["beam"],
    "--drm-beam-size": [3],
    "--drm-beam-min-length": [20],
    "--drm-beam-block-ngram": [3],
    "--drm-beam-context-block-ngram": [-1],
    "--batchsize": [4],
    "--log-every-n-secs": [30],
    "--metrics": ["all"],
    # fid args
    "--krm-retriever-debug-index": ["compressed"],
    "--krm-gold-knowledge-fpath": [
        "/checkpoint/komeili/projects/wizard-internet/fid_gold_docs/knowledge_doc_full-hist.jsonl"
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
