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

MODELS = [
    # rag-wiki model
    # '/private/home/ladolphs/code/ParlAI/data/models/hallucination/bart_rag_token/model',
    "/checkpoint/light/projects/lightqa/nq_open/models/nq_baseline_bart_rag_dpr/model",
    # no-knowledge model trained on wow data
    # '/checkpoint/kshuster/projects/wizard_2.0/parlai_sweeps/bart_sweep1_Fri_Oct__2/395/model',
    "/checkpoint/light/projects/lightqa/nq_open/models/nq_baseline_bart/model"
    # T5-FID QA model
    # '/checkpoint/mpchen/projects/chatty_tasks/qa/t5fid/t9b_nq_singleValSweep_notCompressedMon_May_24/b09/model --path-to-index /private/home/ladolphs/code/ParlAI/data/models/hallucination/wiki_index_exact/exact',
    "/checkpoint/light/projects/lightqa/nq_open/models/nq_krm_t5/model --path-to-index /private/home/ladolphs/code/ParlAI/data/models/hallucination/wiki_index_exact/exact",
]

grid = {
    "-t": ["parlai_internal.projects.light.lightqa.nq_open.task.agents:NQOpenTeacher"],
    "-mf": MODELS,
    "-dt": ["test", "valid"],
    # generation args
    "--inference": ["beam"],
    "--beam-min-length": [1],
    "--skip-generation": [False],
    "--beam-size": [3, 30],
    "--beam_block_ngram": [3],
    "--beam_context_block_ngram": [-1],
    "--log-every-n-secs": [120],
    "--batchsize": [2],
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
        partition="devlab",
        jobtime="{}:00:00".format(HOURS),
        hashname=True,
        requeue=True,
        mem_gb=400,
    )
