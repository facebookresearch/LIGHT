from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import time

SWEEP_NAME = "sweep_retrieve_dm"
HOURS = 24


CONFIG_QUEST_PRED_MACHINES_TRAIN = "parlai_internal.projects.light.quests.tasks.quest_predictive_machines.teacher:datatype=train:light_use_repeat=none:light_use_setting=True:light_unseen_test=False:light_use_person_names=True:light_use_persona=all:light_use_objects=False:light_use_emote=none:light_use_speech=all:light_use_action=all:light_use_current_self_output=none:light_label_type=speech:light_use_cands=20:light_use_clip_cands=20:light_mask_speech=True:light_mask_emote=False:light_mask_action=True:light_mask_window=1:light_use_future=False:light_use_past=False:light_use_future_speech=False:light_use_future_act=False:light_use_future_emote=False:light_use_only_cluster=False:num_clusters=50:light_add_cluster=False:cluster_folder=/checkpoint/rajammanabrolu/saved/light/clusters/:cluster_encoder_file=/checkpoint/rajammanabrolu/saved/light/biranker_dialogue/model:use_all_ex=False:strip_future=False"

CONFIG_QUEST_PRED_MACHINES_VALID = "parlai_internal.projects.light.quests.tasks.quest_predictive_machines.teacher:datatype=valid:light_use_repeat=none:light_use_setting=True:light_unseen_test=False:light_use_person_names=True:light_use_persona=all:light_use_objects=False:light_use_emote=none:light_use_speech=all:light_use_action=all:light_use_current_self_output=none:light_label_type=speech:light_use_cands=20:light_use_clip_cands=20:light_mask_speech=True:light_mask_emote=False:light_mask_action=True:light_mask_window=1:light_use_future=False:light_use_past=False:light_use_future_speech=False:light_use_future_act=False:light_use_future_emote=False:light_use_only_cluster=False:num_clusters=50:light_add_cluster=False:cluster_folder=/checkpoint/rajammanabrolu/saved/light/clusters/:cluster_encoder_file=/checkpoint/rajammanabrolu/saved/light/biranker_dialogue/model:use_all_ex=False:strip_future=False"

CONFIG_QUEST_BOA_TRAIN = "light.modeling.tasks.quests.goals.teacher:QuestTeacher:stask=boa_timeline_prediction:datatype=train:easy=none:maxexperc=1.0:motivation=short"

CONFIG_QUEST_BOA_VALID = "light.modeling.tasks.quests.goals.teacher:QuestTeacher:stask=boa_timeline_prediction:datatype=valid:easy=none:maxexperc=1.0:motivation=short"

CONFIG_QUEST_SEQ_TRAIN = "light.modeling.tasks.quests.goals.teacher:QuestTeacher:stask=seq_timeline_prediction:datatype=train:easy=none:maxexperc=1.0:motivation=short"

CONFIG_QUEST_SEQ_VALID = "light.modeling.tasks.quests.goals.teacher:QuestTeacher:stask=seq_timeline_prediction:datatype=valid:easy=none:maxexperc=1.0:motivation=short"

CONFIG_QUEST_HOBBOT = (
    "light.modeling.tasks.quests.wild_chats.teacher:QuestHobbotTeacher"
)

CONFIG_NEG_HIST_TRAIN = "parlai_internal.projects.light.quests.tasks.light_agent_neg_hist.teacher:light_agent_neg_hist:control_task=light_dialog:neg_hist_cands=100:neg_hist_negs=1:neg_speaker_negs=2:neg_speaker_negs_type=0.5"

CONFIG_NEG_HIST_VALID = "parlai_internal.projects.light.quests.tasks.light_agent_neg_hist.teacher:light_agent_neg_hist:control_task=light_dialog:neg_hist_cands=20:neg_hist_negs=0:neg_speaker_negs=0"

grid = {
    "--image-mode": ["none"],
    # model args
    "-t": [
        f"light_dialog:simple_multi:light_label_type=action:light_use_speech=all,{CONFIG_QUEST_HOBBOT},{CONFIG_NEG_HIST_TRAIN}"
    ],
    "-et": [
        f"light_dialog:simple_multi:light_label_type=action:light_use_speech=all,{CONFIG_QUEST_HOBBOT},{CONFIG_NEG_HIST_VALID}"
    ],
    "--multitask_weights": ["1.0,2.0,1.0"],
    # "--neg-hist-cands": [100],
    # "--neg-hist-negs": [1],
    # "--neg-speaker-negs": [2],
    # "--neg-speaker-negs-type": [0.5],
    "-veps": [0.5],
    "-vme": [8000],
    "--activation": ["gelu"],
    "--attention-dropout": [0.20],
    "--batchsize": ["64 --eval-batchsize 16"],
    "--candidates": ["inline"],
    "--data-parallel": [True],
    "--dict-endtoken": ["__start__"],
    "--dict-file": ["zoo:pretrained_transformers/poly_model_huge_reddit/model.dict"],
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
    "--text-truncate": [768],
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
        # saveroot="/checkpoint/r/projects/light/beatthehobbot/" + SWEEP_NAME,
        prefix="python -u examples/train_model.py",
        PARLAI_PATH="/private/home/rajammanabrolu/ParlAI/",
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
