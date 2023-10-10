#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os

from pytz import timezone
from datetime import datetime

"""
FiD model that uses the gold document accompanying the original message
"""

HOURS = 48
GPUS = 4
NOW = datetime.now(timezone("Europe/Zurich")).strftime("%a_%b_%d_%H%M")

here_path = os.path.realpath(__file__).replace(".py", "")
projects = here_path[here_path.find("/projects") :].strip("/")
projects_dir = "/".join(projects.split("/")[:-1])

SWEEP_NAME = projects.split("/")[-1] + "_" + NOW
SAVEROOT = os.path.join("/checkpoint/ladolphs", projects_dir)
name_keys = {}
HOURS = 72
GPUS = 4

grid = {
    "-t": ["wizard_of_internet:GoldKnowledgeTeacher"],
    "--activation": ["gelu"],
    "--attention-dropout": [0.1],
    "--batchsize": [16],
    "--dropout": [0.1],
    "--optimizer": ["adam"],
    "--fp16": [True],
    "--gradient-clip": [0.1],
    "--label-truncate": [128],
    "--text-truncate": [512],
    "--log-every-n-secs": [30],
    "--lr-scheduler": ["reduceonplateau"],
    "--max-train-time": [0.98 * HOURS * 60 * 60],
    "--model-parallel": [True],
    "--save-after-valid": [True],
    "--skip-generation": [True],
    "-lr": [5e-5, 1e-5, 5e-6, 1e-6],
    "-vmm": ["min"],
    "-vmt": ["ppl"],
    "-vp": [3],
    "-veps": [0.5],
    "-tblog": [True],
    "--warmup-updates": [100],
    # RAG args
    "--retriever-debug-index": [
        "compressed"
    ],  # We are not using the regular RAG retrievers.
    "--model": ["parlai_internal.agents.fid.fid:FiDGoldAgent"],
    "--generation-model": ["bart"],
    "--init-opt": ["arch/bart_large"],
    "--gold-knowledge-fpath": [
        "/checkpoint/komeili/projects/wizard-internet/fid_gold_docs/knowledge_doc_full-hist.jsonl"
    ],
}
if __name__ == "__main__":
    run_grid(
        grid,
        name_keys,
        SWEEP_NAME,
        saveroot=os.path.join(SAVEROOT, SWEEP_NAME),
        create_model_file=True,
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
        email_updates=True,
        wandb=True,
    )
