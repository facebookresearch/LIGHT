from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid


SWEEP_NAME = "sweep_retrieve_multitask_pred_mach_hobbot_et"
NUM_GPUS = 8
HOURS = 24

name_keys = {}


CONFIG_QUEST_PRED_MACHINES = "parlai_internal.projects.light.quests.tasks.quest_predictive_machines.teacher:datatype=train:light_use_repeat=none:light_use_setting=True:light_unseen_test=False:light_use_person_names=True:light_use_persona=all:light_use_objects=False:light_use_emote=none:light_use_speech=all:light_use_action=all:light_use_current_self_output=none:light_label_type=speech:light_use_cands=20:light_use_clip_cands=20:light_mask_speech=True:light_mask_emote=False:light_mask_action=True:light_mask_window=1:light_use_future=False:light_use_past=False:light_use_future_speech=False:light_use_future_act=False:light_use_future_emote=False:light_use_only_cluster=False:num_clusters=50:light_add_cluster=False:cluster_folder=/checkpoint/rajammanabrolu/saved/light/clusters/:cluster_encoder_file=/checkpoint/rajammanabrolu/saved/light/biranker_dialogue/model:use_all_ex=False:strip_future=False"


grid = {
    "--init-model": [
        "zoo:pretrained_transformers/bi_model_huge_reddit/model",
        # 'zoo:pretrained_transformers/bi_model_huge_wikito/model'
    ],
    "--batchsize": [
        32,
    ],
    "-t": [
        f"light.modeling.tasks.quests.wild_chats.teacher:QuestHobbotTeacher,{CONFIG_QUEST_PRED_MACHINES}"
    ],
    "-et": ["light.modeling.tasks.quests.wild_chats.teacher:QuestHobbotTeacher"],
    "--multitask-weights": ["0.2,0.8"],
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
    "--label-truncate": [100],
    "--text-truncate": [720],
    "-vp": [10],
    "-vtim": [60 * 30],
    #'-vme': [
    #    1000
    # ],
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