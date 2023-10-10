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


MODELS = [
    # BART RAG DPR -> BART
    # '/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_knowledge_response_generation_sweep_4_Tue_Aug_31_1155/577/model'
    # ' --dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_sweep_3_Wed_Aug_18_2130/ad6/model',
    "/checkpoint/light/projects/lightqa/wow/models/wow_krm_bart_rag_dpr/model"
    " --dialogue-response-model-path /checkpoint/light/projects/lightqa/wow/models/wow_drm_bart/model",
    # Shared Model
    # '/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_shared_model_sweep_1_Wed_Oct_06_1745/40f/model'
    # ' --dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_shared_model_sweep_1_Wed_Oct_06_1745/40f/model',
    "/checkpoint/light/projects/lightqa/wow/models/wow_krm_drm_shared_bart_rag_dpr/model"
    " --dialogue-response-model-path /checkpoint/light/projects/lightqa/wow/models/wow_krm_drm_shared_bart_rag_dpr/model",
    # Confidence-Score Conditioned Models
    # '/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_knowledge_response_generation_sweep_4_Tue_Aug_31_1155/577/model'
    # ' --dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_knowledge_sweep_1_Mon_Oct_11_1120/956/model --add-fixed-confidence 0',
    "/checkpoint/light/projects/lightqa/wow/models/wow_krm_bart_rag_dpr/model"
    " --dialogue-response-model-path /checkpoint/light/projects/lightqa/wow/models/wow_drm_conf_score_bart/model --add-fixed-confidence 0",
    # '/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_knowledge_response_generation_sweep_4_Tue_Aug_31_1155/577/model'
    # ' --dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_knowledge_sweep_1_Mon_Oct_11_1120/956/model --add-fixed-confidence 2',
    "/checkpoint/light/projects/lightqa/wow/models/wow_krm_bart_rag_dpr/model"
    " --dialogue-response-model-path /checkpoint/light/projects/lightqa/wow/models/wow_drm_conf_score_bart/model --add-fixed-confidence 2",
    # '/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_knowledge_response_generation_sweep_4_Tue_Aug_31_1155/577/model'
    # ' --dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_knowledge_sweep_1_Mon_Oct_11_1120/956/model --add-fixed-confidence 6',
    "/checkpoint/light/projects/lightqa/wow/models/wow_krm_bart_rag_dpr/model"
    " --dialogue-response-model-path /checkpoint/light/projects/lightqa/wow/models/wow_drm_conf_score_bart/model --add-fixed-confidence 6",
    # '/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_knowledge_response_generation_sweep_4_Tue_Aug_31_1155/577/model'
    # ' --dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_knowledge_sweep_1_Mon_Oct_11_1120/956/model --add-fixed-confidence 10',
    "/checkpoint/light/projects/lightqa/wow/models/wow_krm_bart_rag_dpr/model"
    " --dialogue-response-model-path /checkpoint/light/projects/lightqa/wow/models/wow_drm_conf_score_bart/model --add-fixed-confidence 10",
    # Oracle Knowledge Models
    # 'oracle'
    # ' --dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_sweep_3_Wed_Aug_18_2130/ad6/model',
    "oracle"
    " --dialogue-response-model-path /checkpoint/light/projects/lightqa/wow/models/wow_drm_bart/model",
    # 'oracle'
    # ' --dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_knowledge_sweep_1_Mon_Oct_11_1120/956/model --add-fixed-confidence 0',
    "oracle"
    " --dialogue-response-model-path /checkpoint/light/projects/lightqa/wow/models/wow_drm_conf_score_bart/model --add-fixed-confidence 0",
    # 'oracle'
    # ' --dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_knowledge_sweep_1_Mon_Oct_11_1120/956/model --add-fixed-confidence 2',
    "oracle"
    " --dialogue-response-model-path /checkpoint/light/projects/lightqa/wow/models/wow_drm_conf_score_bart/model --add-fixed-confidence 2",
    # 'oracle'
    # ' --dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_knowledge_sweep_1_Mon_Oct_11_1120/956/model --add-fixed-confidence 6',
    "oracle"
    " --dialogue-response-model-path /checkpoint/light/projects/lightqa/wow/models/wow_drm_conf_score_bart/model --add-fixed-confidence 6",
    # 'oracle'
    # ' --dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_knowledge_sweep_1_Mon_Oct_11_1120/956/model --add-fixed-confidence 10',
    "oracle"
    " --dialogue-response-model-path /checkpoint/light/projects/lightqa/wow/models/wow_drm_conf_score_bart/model --add-fixed-confidence 10",
]


grid = {
    "-t": [
        "parlai_internal.projects.light.lightqa.wow.task.agents:WizardOfWikipediaGeneratorTeacher:topic_split",
        "parlai_internal.projects.light.lightqa.wow.task.agents:WizardOfWikipediaGeneratorTeacher:random_split",
    ],
    "-m": [
        "parlai_internal.projects.light.lightqa.seq2seq2seq.task.agents:StackedKnowledgeDialogueAgent"
    ],
    "--knowledge-response-model-path": MODELS,
    "--dialogue-response-no-knowledge-model-path": ["None"],
    "--dialogue-response-rag-wiki-model-path": ["None"],
    "--mutators": ["flatten"],
    "-dt": ["test", "valid"],
    # generation args
    "--krm-fp16": [False],
    "--krm-model-parallel": [False],
    "--drm-model-parallel": [False],
    "--krm-beam-min-length": [10, 15, 20],
    "--krm-beam-size": [3],
    "--krm-indexer-type": ["exact"],
    "--krm-n-docs": [5],
    "--drm-beam-size": [3],
    "--drm-beam-min-length": [20],
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
