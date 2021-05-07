# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.


from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid

SWEEP_NAME = "gen_withstarter"
name_keys = {}

grid = {
    "-t": [
        '"fromfile:fromfile_datapath=/checkpoint/light/projects/dialog_and_act_trainer/light_withstarter_train.txt,fromfile:fromfile_datapath=/checkpoint/light/projects/dialog_and_act_trainer/light_withstarter_wild_train.txt"'
    ],
    "-et": [
        '"fromfile:fromfile_datapath=/checkpoint/light/projects/dialog_and_act_trainer/light_withstarter_wild_valid.txt"',
    ],
    "--max-train-time": [(60 * 60) * 36],
    "--model": ["parlai_internal.projects.meena.unlikely.boringul:UnlikelihoodAgent"],
    "--eval-skip-generation": [False],
    "--validation-max-exs": [200],
    "-vp": [1000],
    "-vmt": ["boring_fails"],
    "-vmm": ["min"],
    "--save-after-valid": [True],
    "-vtim": [(60 * 60) * 30],
    "-stim": [(60) * 60 * 1],
    "--inference": ["beam"],
    "--beam_min_length": [20],
    "--beam_context_block_ngram": [-1],
    "--beam_block_ngram": [-1],
    "--beam_size": [1],
    "--ul-type": ["std0"],
    "--seq-ul-nc": [4],
    "--seq-ul-nl": [4],
    "--seq-ul-ratio": [0.25],
    "--train-boring-repeats": [True],
    "--train-context-repeats": [False],
    "--train-label-repeats": [False],
    "--attention-dropout": [0.00],
    "--batchsize": ["64"],
    "--embedding-size": [2560],
    "--ffn-size": [10240],
    "--variant": ["prelayernorm"],
    "--n-heads": [32],
    "--n-positions": [128],
    "--n-encoder-layers": [2],
    "--n-decoder-layers": [24],
    "--history-add-global-end-token": [
        "end",  # hack to get newline delimiter
    ],
    "--dict-tokenizer": ["bytelevelbpe"],
    "--dict-file": [
        "/checkpoint/parlai/zoo/meena/20200319_meenav0data_tall_2.7B_adamoptimizer/20200319_13.3ppl_200kupdates/model.dict"
    ],
    "--dropout": [0.1],
    "--fp16": [True],
    "--init-model": [
        # emily's good good
        "/checkpoint/parlai/zoo/q_function/generative2.7B_bst_0331/model",
    ],
    "--label-truncate": [128],
    "--lr-scheduler": ["reduceonplateau"],
    "--lr-scheduler-patience": [3],
    "--optimizer": ["adam"],
    "--relu-dropout": [0.0],
    "--activation": ["gelu"],
    "--model-parallel": ["true"],
    "--text-truncate": [128],
    "--truncate": [128],
    "--warmup_updates": [200],
    "--fp16-impl": ["mem_efficient"],
    "--update-freq": [4],
    "--gradient-clip": [0.1],
    "--skip-generation": [True],
    "--log_every_n_secs": [10],
    "-lr": [7e-6],
}

if __name__ == "__main__":
    run_grid(
        grid,
        name_keys,
        SWEEP_NAME,
        partition="learnfair",
        # partition='dev',
        jobtime="24:00:00",
        PARLAI_PATH="/private/home/jase/src/ParlAI/",
        gpus=8,
        nodes=1,
        volta=True,
        volta32=True,
        saveroot="/checkpoint/light/projects/dialog_and_act_trainer/models/"
        + SWEEP_NAME,
        include_job_id=True,
        create_model_file=True,
        hashname=False,
        # fixedname='model',
        requeue=True,
        mem_gb=400,
        data_parallel=True,
        copy_env=False,
    )
