#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os
from pytz import timezone
from datetime import datetime

"""
Evaluating Seq2Seq2Seq model on light-dialog-wild.

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

MODELS = {
    "knowledge_response": [
        # Trained on summaryQA.
        "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_7_Thu_Sep_09_1016/e73/model",
        # Trained on LIGHTNC.
        "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_7_Thu_Sep_09_1016/062/model",
        # Trained on summaryQA + LIGHTNC.
        "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_7_Thu_Sep_09_1016/e57/model",
    ],
    "dialogue_response": [
        # Trained on lightNC (light-dialog-wild with a noun chunk of the target utterance as knowledge).
        "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_8_Thu_Sep_09_1026/d39/model",
    ],
}

grid = {
    "-t": [
        # Same as light_dialog_wild but with rare_word_f1 metric.
        "parlai_internal.projects.light.lightqa.lightqa.task.agents:LightTeacherPlus"
    ],
    "-m": [
        "parlai_internal.projects.light.lightqa.seq2seq2seq.task.agents:StackedKnowledgeDialogueAgent"
    ],
    "--mutators": ["flatten"],
    "--knowledge-response-model-path": MODELS["knowledge_response"],
    "--dialogue-response-model-path": MODELS["dialogue_response"],
    "--dialogue-response-no-knowledge-model-path": ["None"],
    "--dialogue-response-rag-wiki-model-path": ["None"],
    "-dt": ["valid"],
    # generation args
    "--drm-skip-generation": [False],
    "--krm-skip-generation": [False],
    "--drm-inference": ["beam"],
    "--krm-inference": ["beam"],
    "--krm-beam-min-length": [1],
    "--drm-beam-min-length": [10],
    "--krm-beam-size": [3],
    "--drm-beam-size": [3, 10],
    "--beam-filter-for-knowledge-response": [True, False],
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
