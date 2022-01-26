from parlai_internal.projects.light.quests.agents.quest_learner import QuestLearner
import random
import argparse

from parlai.scripts.display_data import display_data
from parlai.scripts.train_model import TrainLoop, setup_args
from parlai.scripts.eval_model import eval_model
from parlai.scripts.build_dict import build_dict

# from parlai.core.params import ParlaiParser
# from parlai.agents.transformer.transformer import add_common_cmdline_args
# from parlai.core.torch_agent import Batch
# from parlai.core.loader import load_agent_module


if __name__ == "__main__":
    random.seed(42)

    # Python Dict -> CLI wrapper because this is more convenient

    stask = "seq_timeline_prediction"
    # stask = 'goal_text_prediction'
    # stask = 'short_mot_prediction'
    # stask = 'boa_timeline_prediction'
    # model = 'transformer/generator'
    model = "transformer/polyencoder"
    # model = 'parlai.agents.bert_ranker.bi_encoder_ranker:BiEncoderRankerAgent'

    # """
    opt_display = {
        #'task': 'light.modeling.tasks.quests.goals.teacher:QuestTeacher:stask=' + stask + ':datatype=train:easy=True',
        "task": "light.modeling.tasks.atomic.teacher:AtomicTeacher:datatype=valid:fill=rand",
        "datatype": "valid",
        "display_verbose": True,
        "batchsize": 1,
        "num_examples": 10,
        "max-display-len": 1000,
        "display-ignore-fields": "agent_reply",
    }
    display_data(opt_display)
    exit()
    # """
    task = (
        "light_dialog:simple_multi:light_label_type=action,light.modeling.tasks.quests.goals.teacher:QuestTeacher:stask="
        + stask
        + ":datatype=train:easy=True"
    )
    tname = "multitasklight_quests"

    opt = {
        "task": task,
        # "multitask_weights": [1.0, 2.0],
        #'stask': 'seq_timeline_prediction',
        "model": model,
        #'dict-file': '/checkpoint/rajammanabrolu/lighttest/all.dict',
        "dict_maxexs": 100000,
        #'model': 'bert_ranker/bi_encoder_ranker',
        #'model': 'parlai.agents.bert_ranker.bi_encoder_ranker:BiEncoderRankerAgent',
        "datatype": "train",
        "evaltask": "light.modeling.tasks.quests.goals.teacher:QuestTeacher:stask="
        + stask
        + ":datatype=valid",
        "validation-every-n-epochs": 30,
        "model_file": "/checkpoint/rajammanabrolu/lighttest/" + tname + "_" + model,
        "save_every_n_secs": 30,
        "num_epochs": 150,
        #'num_examples': 10,
        #'max-display-len': 1000,
        #'display-ignore-fields': 'agent_reply',
        #'model_parallel': True
    }

    opt_cli = []
    print(opt.items())
    for k, v in opt.items():
        opt_cli.extend(["--" + k, str(v)])

    print(opt_cli)

    default_args = setup_args()
    default_args = default_args.parse_args(opt_cli)

    print(default_args)

    TrainLoop(default_args).train()

    opt = {
        "datatype": "test",
        "report_filename": "/checkpoint/rajammanabrolu/lighttest/"
        + tname
        + "_"
        + model
        + "_evals",
        "model_file": "/checkpoint/rajammanabrolu/lighttest/" + tname + "_" + model,
        "save_world_logs": "/checkpoint/rajammanabrolu/lighttest/"
        + tname
        + "_"
        + model
        + "_evals",
    }

    default_args.update(opt)

    eval_model(default_args)
