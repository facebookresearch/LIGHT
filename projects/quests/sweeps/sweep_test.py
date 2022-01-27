#!/usr/bin/env python3
# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid

SWEEP_NAME = "sweep_test"
HOURS = 1

# grid must be a Dict[str, List[value]]. Nested options are not allowed.
# see below for an example of how to tie weights
grid = {
    "-t": [
        '"parlai_internal.projects.light.quests.tasks.quest_teacher:QuestTeacher:stask=seq_timeline_prediction"'
    ],
    "--model": [
        "transformer/generator",
        "parlai.agents.bert_ranker.bi_encoder_ranker:BiEncoderRankerAgent",
    ],
    "--dict-file": ["/checkpoint/rajammanabrolu/lighttest/all.dict"],
    "--dict-tokenizer": ["bpe"],
    "--dict-lower": [True],
    "-esz": [512],
    "--optimizer": ["adamax"],
    "-lr": [1e-6],  # , 2.5e-6, 5e-6, 7.5e-6, 1e-5, 5e-5, 1e-4],
    "--lr-scheduler": ["reduceonplateau"],
    "-bs": ["16"],
    "--dropout": [0.1],
    "--attention-dropout": [
        #'0.0 --relu-dropout 0.0',  # notice how i tied two weights together
        "0.1 --relu-dropout 0.1"
    ],
    "--n-heads": [16],
    "--n-layers": [8],
    "--n-positions": [512],
    "--text-truncate": [512],
    "--label-truncate": [128],
    "--ffn-size": [2048],
    "--gradient-clip": [0.1],
    "--validation-metric": ["ppl"],
    "--validation-metric-mode": ["min"],
    "--validation-patience": [10],
    "--log-every-n-secs": [10],
    "--skip-generation": ["true"],
    "--variant": ["xlm"],
    "--activation": ["gelu"],
    "--embeddings-scale": ["true"],
    #'-ttim': [HOURS * 60 * 60 - 60 * 30],
    "--load-from-checkpoint": ["true"],
    "--learn-positional-embeddings": ["true"],
    "--save-after-valid": ["true"],
    "--update-freq": ["1"],
    "--fp16": ["false"],
    "--betas": ["0.9,0.999", "0.9,0.98"],
    "--warmup-updates": [2000],
}

if __name__ == "__main__":
    run_grid(
        grid,
        {},
        SWEEP_NAME,
        PARLAI_PATH="/private/home/rajammanabrolu/ParlAI/",
        prefix="python -u examples/train_model.py",
        gpus=1,  # only use a single gpu
        nodes=1,  # only use a single node
        cpus=10,  # generally leave this unchanged
        volta=True,  # set this if using --fp16 true
        volta32=True,  # set this true to request a 32gb machine
        partition="learnfair",  # one of learnfair/dev/priority. read general docs
        jobtime="{}:00:00".format(HOURS),
        hashname=True,  # use short filenames. Cosmetic only, personal preference.
        requeue=True,  # auto resubmit if you get pre-empted
    )
