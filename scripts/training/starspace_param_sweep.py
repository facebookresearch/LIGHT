#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid

SWEEP_NAME = "light_maps1"
# PARTITION = 'uninterrupted'
PARTITION = "priority"
name_keys = {}

grid = {
    "--task": [
        "internal:light_maps",
    ],
    "--evaltask": ["internal:light_maps"],
    "--model": ["starspace"],
    "-lr": [0.05, 0.1, 0.2],
    "--dict-file": [
        "/private/home/jase/src/ParlAI/parlai_internal/projects/light/light_maps/all.dict"
    ],
    "--embedding-type": ["fasttext_cc"],
    "--input_dropout": [0, 0.5, 0.8, 0.9],
    "--lins": [0],
    "--embeddingsize": [300],
    "--share_embeddings": [True],
    "--margin": [0.1],
    "--max_train_time": [28800 / 2],
    "-vtim": [100],
    "-vp": [100],
    "-vshare": [False],
    "--validation-metric": ["accuracy"],
    "--validation-metric-mode": ["max"],
    "--save-after-valid": [True],
    "--dict_maxtokens": [80000],
    "--log_every_n_secs": [10],
    "--numthreads": [40],
}

if __name__ == "__main__":
    run_grid(
        grid,
        name_keys,
        SWEEP_NAME,
        partition=PARTITION,
        jobtime="40:00:00",
        PARLAI_PATH="/private/home/jase/src/ParlAI/",
        prefix="python -u examples/train_model.py",
        include_job_id=True,
        create_model_file=True,
        cpus=40,
        gpus=0,
    )


#  run_grid(grid, name_keys, SWEEP_NAME, partition='priority', jobtime='18:00:00', PARLAI_PATH='/private/home/jase/src/ParlAI/',prefix='python -u parlai_internal/projects/retrieve_n_refine/seq2seq_exp/eval_rnr_ppl.py',hide_keys={'--rnr-modelfile'},include_job_id=True,create_model_file=False)
