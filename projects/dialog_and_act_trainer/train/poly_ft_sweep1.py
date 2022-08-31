# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import time

"""
    LIGHT+WILD poly-encoder training fine-tuned on all interesting LIGHT retrieval/ranking tasks.
"""

SWEEP_NAME = "poly_ft"
HOURS = 24

act = "fromfile:fromfile_datapath=/checkpoint/light/projects/dialog_and_act_trainer/light_act_train.txt"
emote = "fromfile:fromfile_datapath=/checkpoint/light/projects/dialog_and_act_trainer/light_emote_train.txt"
quest_scorer = "fromfile:fromfile_datapath=/checkpoint/light/projects/dialog_and_act_trainer/light_questscorer_train.txt"
typepicker = "fromfile:fromfile_datapath=/checkpoint/light/projects/dialog_and_act_trainer/light_typepicker_train.txt"

grid = {
    "--image-mode": ["none"],
    # model args
    "-t": [
        '"fromfile:fromfile_datapath=/checkpoint/light/projects/dialog_and_act_trainer/light_train.txt,fromfile:fromfile_datapath=/checkpoint/light/projects/dialog_and_act_trainer/light_wild_train.txt,'
        + act
        + ","
        + emote
        + ","
        + quest_scorer
        + ","
        + typepicker
        + '"'
    ],
    "-et": [
        '"fromfile:fromfile_datapath=/checkpoint/light/projects/dialog_and_act_trainer/light_act_valid.txt,fromfile:fromfile_datapath=/checkpoint/light/projects/dialog_and_act_trainer/light_emote_valid.txt"',
    ],
    "-vme": [8000],
    "--activation": ["gelu"],
    "--attention-dropout": [0.20],
    "--batchsize": ["32 --eval-batchsize 16"],
    "--candidates": ["inline"],
    "--data-parallel": [True],
    "--dict-endtoken": ["__start__"],
    "--dict-file": ["./data/models/pretrained_transformers/model_bi.dict"],
    "--dict-lower": [True],
    "--dict-tokenizer": ["bpe"],
    "--dropout": [0.00],
    "--embedding-size": [768],
    "--embeddings-scale": [False],
    "--ffn-size": [3072],
    "--fp16": [True],
    "--history-size": [20],
    "--init-model": [
        "/checkpoint/light/projects/dialog_and_act_trainer/models/poly_pre/34c_jobid=1/model"
    ],
    "--label-truncate": [72],
    "--learn-embeddings": [True],
    "--learn-positional-embeddings": [True],
    "--log_every_n_secs": [20],
    # "-lr": [1e-7, 3e-7, 1e-6],
    "-lr": [5e-5],
    "--lr-scheduler-decay": [0.7],
    "--lr-scheduler-patience": [1],
    "--max_train_time": [200000],
    "--model": ["transformer/polyencoder"],
    "--n-heads": [12],
    "--n-layers": [12],
    "--n-positions": [1024],
    "--n-segments": [2],
    "--num-epochs": [50.0],
    "--optimizer": ["adamax"],
    "--output-scaling": [0.04],
    "--poly-attention-type": ["basic"],
    "--poly-n-codes": [20],
    "--polyencoder-type": ["n_first"],
    "--reduction-type": ["first"],
    "--relu-dropout": [0.2],
    "--save-after-valid": [True],
    "--share-encoders": [False],
    "--text-truncate": [360],
    "--validation-metric": ["accuracy"],
    "--validation-metric-mode": ["max"],
    "--variant": ["xlm"],
    "--warmup_updates": [100],
    # existing ones..
    "--validation-every-n-secs": [60 * 60],
    "--validation-patience": [10],
    "--log-every-n-secs": [10],
    "-ttim": [HOURS * 60 * 60 - 60 * 30],
    "--load-from-checkpoint": ["true"],
}

if __name__ == "__main__":
    run_grid(
        grid,
        {},
        SWEEP_NAME,
        saveroot="/checkpoint/light/projects/dialog_and_act_trainer/models/"
        + SWEEP_NAME,
        # prefix='python -u examples/train_model.py',
        PARLAI_PATH="/private/home/jase/src/ParlAI/",
        create_model_file=True,
        include_job_id=True,
        data_parallel=True,
        gpus=8,
        volta=True,
        volta32=True,
        # partition='learnfair',
        partition="dev",
        jobtime="{}:00:00".format(HOURS),
        hashname=True,
        requeue=True,
        copy_env=False,
        email_updates=False,
    )
