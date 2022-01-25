# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory


from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid

SWEEP_NAME = "light_poly_env_init"
NUM_GPUS = 8

name_keys = {}

CONFIG_INIT = "zoo:pretrained_transformers/bi_model_huge_reddit/model \
--model transformer/biencoder --eval-batchsize 8 \
--data-parallel True \
--history-size 20 --label-truncate 100 --text-truncate 400 \
--num-epochs 10.0 --max_train_time 200000 -veps 0.5 -vme 8000 \
--validation-metric accuracy --validation-metric-mode max \
--save-after-valid True --log_every_n_secs 20 --candidates batch \
--dict-tokenizer bpe --dict-lower True --optimizer adamax \
--output-scaling 0.06 \
--variant xlm --reduction-type mean --share-encoders False \
--learn-positional-embeddings True --n-layers 12 --n-heads 12 \
--ffn-size 3072 --attention-dropout 0.1 --relu-dropout 0.0 --dropout 0.1 \
--n-positions 1024 --embedding-size 768 --activation gelu \
--embeddings-scale False --n-segments 2 --learn-embeddings True \
--share-word-embeddings False --dict-endtoken __start__ --fp16 True"

CONFIG_BASELINE = (
    "zoo:pretrained_transformers/poly_model_huge_reddit/model "
    "--model transformer/polyencoder "
    "--dict-file zoo:pretrained_transformers/poly_model_huge_reddit/model.dict "
    "--dict-tokenizer bpe --dict-lower True "
    "--output-scaling 0.06 --variant xlm --n-layers 12 --n-heads 12 "
    "--learn-positional-embeddings True "
    "--ffn-size 3072 --n-positions 1024 --embedding-size 768 "
    "--activation gelu  --embeddings-scale False "
    "--n-segments 2 --dict-endtoken __start__ "
)

CONFIG_BASELINE_INIT = (
    "--init-model zoo:pretrained_transformers/poly_model_huge_reddit/model "
    "--dict-file zoo:pretrained_transformers/poly_model_huge_reddit/model.dict "
    "--dict-tokenizer bpe --dict-lower True "
    "--output-scaling 0.06 --variant xlm --n-layers 12 --n-heads 12 "
    "--learn-positional-embeddings True "
    "--ffn-size 3072 --n-positions 1024 --embedding-size 768 "
    "--activation gelu  --embeddings-scale False "
    "--n-segments 2 --dict-endtoken __start__ "
)
"""grid = {
    '-t': [
        'parlai_internal.projects.light.quests.tasks.quest_hobbot.teacher:QuestHobbotTeacher'
    ],
    '-et': [
        'parlai_internal.projects.light.quests.tasks.quest_hobbot.teacher:QuestHobbotTeacher'
    ],
    # '--multitask-weights': ['0.5,0.5', '0.8,0.2', '0.2,0.8', '0.25,0.75'],
    '-bs': [64],
    '--warmup_updates': [200],
    '--lr-scheduler': ['reduceonplateau'],
    '--lr-scheduler-patience': [3],
    '--lr-scheduler-decay': [0.9],
    '-lr': [1e-5],
    # val every 1000 seconds, ~17 minutes
    '--init-model': [
        CONFIG_BASELINE
    ],
}"""

CONFIG_SCRATCH = (
    # '--init-model zoo:pretrained_transformers/poly_model_huge_reddit/model '
    # '--dict-file zoo:pretrained_transformers/poly_model_huge_reddit/model.dict '
    "--dict-tokenizer bpe --dict-lower True "
    "--output-scaling 0.06 --variant xlm --n-layers 6 --n-heads 6 "
    "--learn-positional-embeddings True "
    "--ffn-size 1536 --n-positions 512 --embedding-size 384 "
    "--activation gelu  --embeddings-scale False "
    "--n-segments 2"
)

grid = {
    "-t": [
        "parlai_internal.projects.light.quests.tasks.quest_hobbot.teacher:QuestHobbotTeacher"
    ],
    "-et": [
        "parlai_internal.projects.light.quests.tasks.quest_hobbot.teacher:QuestHobbotTeacher"
    ],
    "--model": [
        f"transformer/polyencoder {CONFIG_SCRATCH}",
    ],
    "--batchsize": [32],
    "--eval-batchsize": [64],
    "--warmup-updates": [250],
    "-lr": [1e-4],
    "--lr-scheduler": ["reduceonplateau"],
    "--data-parallel": [True],
    "--label-truncate": [72],
    "--text-truncate": [360],
    "-vp": [10],
    "-vtim": [60 * 30],
    "--validation-metric": ["hits@1"],
    "--validation-metric-mode": ["max"],
    "--save-after-valid": [True],
    "--log-every-n-secs": [30],
    "--candidates": ["batch"],
    "--eval-candidates": ["inline"],
    "--optimizer": ["adamw"],
    "--reduction-type": ["mean"],
    "--share-encoders": [False],
    "--learn-positional-embeddings": [True],
    "--dropout": [0.1],
    "--learn-embeddings": [True],
    "--share-word-embeddings": [True],
    "--fp16": [True],
    # Poly-specific params
    "--polyencoder-type": ["codes --codes-attention-type basic"],
    "--poly-n-codes": [64],
    "--gradient-clip": [1.0],
    "--poly-attention-type": ["basic"],
    #'--polyencoder-attention-keys': ['context'],
    "--ignore-bad-candidates": ["true"],
    "-tblog": ["true"],
}


if __name__ == "__main__":
    run_grid(
        grid,
        name_keys,
        SWEEP_NAME,
        partition="learnfair",
        jobtime="8:00:00",
        prefix="python -u examples/train_model.py",
        PARLAI_PATH="/private/home/rajammanabrolu/ParlAI/",
        gpus=NUM_GPUS,
        create_model_file=True,
        data_parallel=True,
        include_job_id=True,
        requeue=True,
        copy_env=False
        # copy_dirs=['tests', 'examples', 'projects', 'data/light_predictive_machines'],
    )
