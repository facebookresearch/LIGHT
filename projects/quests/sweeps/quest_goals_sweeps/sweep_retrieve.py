from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid

"""
LIGHT quests retrieval
"""

SWEEP_NAME = "sweep_retrieve_easy"
HOURS = 6

CONFIG_NEWREDDIT = (
    "--dict-file /checkpoint/parlai/zoo/meena/20200227_mlmretrieval_robertasize/model.dict "
    "--init-model /checkpoint/parlai/zoo/meena/20200227_mlmretrieval_robertasize/model "
    "--dict-tokenizer bytelevelbpe "
    "-esz 1024 --ffn-size 4096 --n-heads 16 --n-layers 24 --activation gelu "
    "--embeddings-scale False --output-scaling 1.0 --n-positions 512 --variant xlm "
    "--learn-positional-embeddings true "
)
CONFIG_BASELINE = (
    "--init-model zoo:pretrained_transformers/poly_model_huge_reddit/model "
    "--dict-file zoo:pretrained_transformers/poly_model_huge_reddit/model.dict "
    "--dict-tokenizer bpe --dict-lower True "
    "--output-scaling 0.06 --variant xlm --n-layers 12 --n-heads 12 "
    "--learn-positional-embeddings True "
    "--ffn-size 3072 --n-positions 1024 --embedding-size 768 "
    "--activation gelu  --embeddings-scale False "
    "--n-segments 2 --dict-endtoken __start__ "
)

tasks = [
    "seq_timeline_prediction",
    "boa_timeline_prediction",
]  #'goal_text_prediction', 'short_mot_prediction',

grid_tasks = []
for t in tasks:
    gtask = (
        "parlai_internal.projects.light.quests.tasks.quest_base.teacher:QuestTeacher:stask="
        + t
        + ":datatype=train:easy=False "
        + "-et parlai_internal.projects.light.quests.tasks.quest_base.teacher:QuestTeacher:stask="
        + t
        + ":datatype=valid:easy=True"
    )
    grid_tasks.append(gtask)


grid = {
    "-t": grid_tasks,
    # [
    #'light_dialog:simple_multi:light_label=speech',
    # ],
    "--model": [
        f"transformer/polyencoder {CONFIG_BASELINE}",
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
    "--validation-metric": ["hits@5"],
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
        {},
        SWEEP_NAME,
        partition="learnfair",
        jobtime="{}:00:00".format(HOURS),
        prefix="python -u examples/train_model.py",
        cpus=10,
        gpus=8,
        # mem_gb=400,
        nodes=1,
        data_parallel=True,
        hashname=True,
        volta=True,
        volta32=True,
        copy_env=False,
        PARLAI_PATH="/private/home/rajammanabrolu/ParlAI/",
        include_job_id=True,
        create_model_file=True,
        requeue=True,
    )
