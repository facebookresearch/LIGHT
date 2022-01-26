#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os
from pytz import timezone
from datetime import datetime

"""
Evaluating Seq2Seq2Seq model on light-dialog-wild and summaryQA on TEST and
self_say_once.

The metrics, we're interested in are:
    - PPL
    - Token Accuracy
    - F1
    - RF1
"""

HOURS = 6
GPUS = 1

NOW = datetime.now(timezone("Europe/Zurich")).strftime("%a_%b_%d_%H%M")

here_path = os.path.realpath(__file__).replace(".py", "")
projects = here_path[here_path.find("/projects") :].strip("/")
projects_dir = "/".join(projects.split("/")[:-1])

SWEEP_NAME = projects.split("/")[-1] + "_" + NOW
SAVEROOT = os.path.join("/checkpoint/ladolphs", projects_dir)
name_keys = {}


KNOWLEDGE_RESPONSE_MODELS = [
    # Trained on summaryQA.
    # '/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_8_Thu_Sep_16_0953/3ed/model',
    "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_krm_bart_summaryqa/model",
    # Trained on LIGHTNC.
    # '/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_8_Thu_Sep_16_0953/974/model',
    "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_krm_bart_light/model",
    # Trained on summaryQA + LIGHTNC.
    # '/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_8_Thu_Sep_16_0953/375/model',
    "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_krm_bart_light_and_summaryqa/model",
    # Oracle
    "oracle",
]

DIALOGUE_RESPONSE_MODELS = [
    # Trained on lightNC (light-dialog-wild with a noun chunk of the target utterance as knowledge).
    # '/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_10_Thu_Sep_16_1306/1d8/model',
    "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_drm_bart",
    # Trained with 0-10 confidence int
    # '/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_9_Mon_Sep_13_1703/d13/model --add-confidence-as-str false --add-fixed-confidence 0',
    # '/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_9_Mon_Sep_13_1703/d13/model --add-confidence-as-str false --add-fixed-confidence 2',
    # '/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_9_Mon_Sep_13_1703/d13/model --add-confidence-as-str false --add-fixed-confidence 6',
    # '/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_9_Mon_Sep_13_1703/d13/model --add-confidence-as-str false --add-fixed-confidence 10',
    "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_drm_bart_confidence/model --add-confidence-as-str false --add-fixed-confidence 0",
    "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_drm_bart_confidence/model --add-confidence-as-str false --add-fixed-confidence 2",
    "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_drm_bart_confidence/model --add-confidence-as-str false --add-fixed-confidence 6",
    "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_drm_bart_confidence/model --add-confidence-as-str false --add-fixed-confidence 10",
]

SHARED_MODELS = [
    # Shared param model.
    # '/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_12_Thu_Sep_23_1335/27b/model',
    "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_krm_drm_shared_bart/model",
]

MODELS = [
    f"{krm} --dialogue-response-model-path {drm}"
    for krm in KNOWLEDGE_RESPONSE_MODELS
    for drm in DIALOGUE_RESPONSE_MODELS
] + [f"{sm} --dialogue-response-model-path {sm}" for sm in SHARED_MODELS]

grid = {
    "-t": [
        # Same as light_dialog_wild but with rare_word_f1 metric.
        "parlai_internal.projects.light.lightqa.lightqa.task.agents:LightTeacherPlus",
        "parlai_internal.projects.light.lightqa.lightqa.task.agents:SummaryQATeacher",
    ],
    "-m": [
        "parlai_internal.projects.light.lightqa.seq2seq2seq.task.agents:StackedKnowledgeDialogueAgent"
    ],
    "--mutators": ["flatten,self_say_once"],
    "--knowledge-response-model-path": MODELS,
    # '--dialogue-response-model-path': MODELS['dialogue_response'],
    "--dialogue-response-no-knowledge-model-path": ["None"],
    "--dialogue-response-rag-wiki-model-path": ["None"],
    "-dt": ["test", "valid"],
    # generation args
    "--krm-fp16": [False],
    "--drm-fp16": [False],
    "--drm-skip-generation": [False],
    "--krm-skip-generation": [False],
    "--drm-inference": ["beam"],
    "--krm-inference": ["beam"],
    "--krm-beam-min-length": [1],
    "--drm-beam-min-length": [10],
    "--krm-beam-size": [3],
    "--drm-beam-size": [3],
    "--beam-filter-for-knowledge-response": [False],
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
