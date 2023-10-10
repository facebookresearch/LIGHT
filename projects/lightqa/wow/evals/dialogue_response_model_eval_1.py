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
GPUS = 4

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
        # trained on --indexer-type compressed
        "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_knowledge_response_generation_sweep_1_Tue_Aug_17_1822/9aa/model",
        # trained on --indexer-type exact
        "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_knowledge_response_generation_sweep_3_Sat_Aug_28_0811/35e/model",
    ],
    "dialogue_response": [
        "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_sweep_3_Wed_Aug_18_2130/ad6/model",
    ],
}

DECODING_OPTIONS = {
    "knowledge_response": [
        "inference:beam,beam_block_ngram:3,beam_context_block_ngram:-1,beam_size:3,beam_min_length:1,indexer_type:exact,path_to_index:/private/home/ladolphs/code/ParlAI/data/models/hallucination/wiki_index_exact/exact,model_parallel:True",
    ],
    "dialogue_response": [
        "inference:beam,beam_block_ngram:3,beam_context_block_ngram:-1,beam_size:3,beam_min_length:20,model_parallel:True",
    ],
}

grid = {
    "-t": [
        "parlai_internal.projects.light.lightqa.wow.task.agents:WizardOfWikipediaGeneratorTeacher"
    ],
    "-m": [
        "parlai_internal.projects.light.lightqa.seq2seq2seq.task.agents:StackedKnowledgeDialogueAgent"
    ],
    "--knowledge-response-model-path": MODELS["knowledge_response"],
    "--dialogue-response-model-path": MODELS["dialogue_response"],
    "--knowledge-response-model-options": DECODING_OPTIONS["knowledge_response"],
    "--dialogue-response-model-options": DECODING_OPTIONS["dialogue_response"],
    "--dialogue-response-no-knowledge-model-path": ["None"],
    "--dialogue-response-rag-wiki-model-path": ["None"],
    "--mutators": ["flatten"],
    "-dt": ["valid:stream"],
    # generation args
    # '--fp16': [True],
    "--log-every-n-secs": [120],
    # '--model-parallel': [False],
    "--batchsize": [1],
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
        one_job_per_node=True,
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
