from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid


SWEEP_NAME = "sweep_retrieve_hobbot_env_bienc"
NUM_GPUS = 8
HOURS = 12

name_keys = {}

grid = {
    "--init-model": [
        "zoo:pretrained_transformers/bi_model_huge_reddit/model",
        # 'zoo:pretrained_transformers/bi_model_huge_wikito/model'
    ],
    "--batchsize": [
        64,
    ],
    "-t": ["light.modeling.tasks.quests.wild_chats.teacher:QuestHobbotTeacher"],
    "--model": ["transformer/biencoder"],
    "--eval-batchsize": [1],
    "--warmup_updates": [
        200,
    ],
    "--lr-scheduler-patience": [0],
    "--lr-scheduler-decay": [0.4],
    "-lr": [
        5e-5,
    ],
    "--data-parallel": [True],
    "--history-size": [20],
    "--label-truncate": [360],
    "--text-truncate": [360],
    "-vp": [5],
    "-veps": [0.1],
    "-vme": [1000],
    "--validation-metric": ["accuracy"],
    "--validation-metric-mode": ["max"],
    "--save-after-valid": [True],
    "--log_every_n_secs": [20],
    "--candidates": ["batch"],
    "--dict-tokenizer": ["bpe"],
    "--dict-file": ["/checkpoint/parlai/dicts/20190222_bpelower_ost+toronto+wiki/dict"],
    "--dict-lower": [True],
    "--optimizer": ["adamax"],
    "--output-scaling": [
        0.06,
        # 1
    ],
    "--variant": ["xlm"],
    "--reduction_type": ["mean"],
    "--share-encoders": [False],
    "--learn-positional-embeddings": [
        True,
    ],
    "--n-layers": [12],
    "--n-heads": [12],
    "--ffn-size": [3072],
    "--attention-dropout": [
        "0.1 --dropout 0.1",
    ],
    "--relu-dropout": [0.0],
    "--n-positions": [1024],
    "--embedding-size": [768],
    "--activation": ["gelu"],
    "--embeddings-scale": [False],
    "--n-segments": [2],
    "--learn-embeddings": [True],
    "--share-word-embeddings": [False],
    "--dict-endtoken": ["__start__"],
    "--fp16": [True],
    "--train-predict": [False],
    "-cands": [
        "inline",
    ],
    "-ecands": ["inline"],
}

if __name__ == "__main__":
    run_grid(
        grid,
        name_keys,
        SWEEP_NAME,
        partition="learnfair",
        jobtime="{}:00:00".format(HOURS),
        prefix="python -u examples/train_model.py",
        PARLAI_PATH="/private/home/rajammanabrolu/ParlAI/",
        gpus=NUM_GPUS,
        create_model_file=True,
        data_parallel=True,
        include_job_id=True,
        hashname=True,
        requeue=True,
        copy_env=False,
    )
