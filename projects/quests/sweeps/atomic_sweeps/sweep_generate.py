from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid

SWEEP_NAME = "sweep_atomic_generate_rand"
HOURS = 8

# grid must be a Dict[str, List[value]]. Nested options are not allowed.
# see below for an example of how to tie weights

grid = {
    "-t": [
        "light.modeling.tasks.atomic.teacher:AtomicTeacher:datatype=train:fill=rand"
    ],
    "-et": [
        "light.modeling.tasks.atomic.teacher:AtomicTeacher:datatype=valid:fill=rand"
    ],
    # ['"light.modeling.tasks.quests.goals.teacher:QuestTeacher:stask=seq_timeline_prediction"'],
    "--model": ["transformer/generator"],
    # , 'parlai.agents.bert_ranker.bi_encoder_ranker:BiEncoderRankerAgent'],
    # '--dict-file': ['/checkpoint/rajammanabrolu/lighttest/all.dict'],
    "--dict_maxexs": [1000000],
    "--dict-tokenizer": ["bpe"],
    "--dict-lower": [True],
    "-esz": [512],
    "--optimizer": ["adamax"],
    "-lr": [1e-4, 1e-5, 1e-6],  # 1e-4 is best 1e-6, 1e-5,
    "--lr-scheduler": ["reduceonplateau"],
    "-bs": ["32"],
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
    "--validation-metric": ["f1"],
    "--validation-metric-mode": ["max"],
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
    "--betas": ["0.9,0.999"],
    # "--validation-metric": ["accuracy"],
    # "--validation-metric-mode": ["max"],
    "--warmup_updates": [100],
    #'--inference': [ 'beam' ],
    #'--beam_min_length': [ 20 ],
    #'--beam_context_block_ngram': [ -1 ],
    #'--beam_block_ngram': [ -1 ],
    #'--beam_size': [ 1 ],
    # existing ones..
    "--validation-every-n-secs": [60 * 30],
    "--validation-patience": [10],
    "--log-every-n-secs": [10],
    "-ttim": [HOURS * 60 * 60 - 60 * 30],
}

if __name__ == "__main__":
    run_grid(
        grid,
        {},
        SWEEP_NAME,
        PARLAI_PATH="/private/home/rajammanabrolu/ParlAI/",
        prefix="python -u examples/train_model.py",
        nodes=1,  # only use a single node
        # cpus=10,        # generally leave this unchanged
        create_model_file=True,
        include_job_id=True,
        data_parallel=True,
        gpus=4,
        volta=True,
        volta32=True,
        partition="learnfair",
        # partition='dev',
        jobtime="{}:00:00".format(HOURS),
        hashname=False,
        requeue=True,
        copy_env=False,
    )
