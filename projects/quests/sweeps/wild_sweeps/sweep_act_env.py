# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import time

"""
    Finetune on all12 tasks after train  multitask on all 12 parlall tasks
"""

SWEEP_NAME = "swp7_light_neg"
HOURS = 24

grid = {
    "--image-mode": ["none"],
    # model args
    # internal:light_agent_neg_hist:control_task=light_dialog
    "-t": [
        '"light_dialog:simple_multi:light_label_type=action:light_use_speech=all,light_dialog:simple_multi:light_label_type=emote:light_use_speech=all"'
    ],
    # internal:light_agent_neg_hist:control_task=light_dialog:neg_hist_cands=20:neg_hist_negs=0:neg_speaker_negs=0,
    "-et": [
        '"light_dialog:simple_multi:light_label_type=action:light_use_speech=all,light_dialog:simple_multi:light_label_type=emote:light_use_speech=all"'
    ],
    "--multitask_weights": ["1.0,1.0"],
    # "--neg-hist-cands": [100],
    # "--neg-hist-negs": [1],
    # "--neg-speaker-negs": [2],
    # "--neg-speaker-negs-type": [0.5],
    "-veps": [0.5],
    "-vme": [8000],
    "--activation": ["gelu"],
    "--attention-dropout": [0.20],
    "--batchsize": ["16 --eval-batchsize 16"],
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
    "--init-model": ["zoo:pretrained_transformers/poly_model_huge_reddit/model"],
    "--label-truncate": [100],
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
    "--poly-n-codes": [4],
    "--polyencoder-type": ["n_first"],
    "--reduction-type": ["first"],
    "--relu-dropout": [0.2],
    "--save-after-valid": [True],
    "--share-encoders": [False],
    #    "--shuffle": [True],
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
        # saveroot="/checkpoint/rajammanabrolu/projects/light/beatthehobbot/" + SWEEP_NAME,
        prefix="python -u examples/train_model.py",
        PARLAI_PATH="/private/home/rajammanabrolu/src/ParlAI/",
        create_model_file=True,
        include_job_id=True,
        data_parallel=True,
        gpus=8,
        volta=True,
        volta32=True,
        partition="learnfair",
        # partition='dev',
        jobtime="{}:00:00".format(HOURS),
        hashname=False,
        requeue=True,
        copy_env=False,
    )
