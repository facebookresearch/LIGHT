#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from parlai.core.teachers import ParlAIDialogTeacher
from parlai.core.loader import register_teacher
from light.constants import LIGHT_DATAPATH
from light.modeling.tasks.quests.goals.build import build
import copy
import os


def _path(opt):
    task = opt["subtask"]
    filname = task + "_sample"

    opt["datatype"] = opt["datatype"].split(":")[0]

    if opt["datatype"] == "train":
        filname += "_train.txt"
    elif opt["datatype"] == "valid":
        filname += "_valid.txt"
    elif opt["datatype"] == "test":
        filname += "_test.txt"
    path = os.path.join(opt["light_datapath"], "quests/base", task, filname)
    return path


@register_teacher("light:quest_goals")
class QuestTeacher(ParlAIDialogTeacher):
    @staticmethod
    def add_cmdline_args(argparser, partial_opt=None):
        argparser.add_argument(
            "-stask",
            "--subtask",
            type=str,
            default="goal_text_prediction",
            choices=[
                "goal_text_prediction",
                "seq_timeline_prediction",
                "boa_timeline_prediction",
                "short_mot_prediction",
            ],
            help=(
                "Subtask to check. Options are ['goal_text_prediction', 'boa_timeline_prediction', "
                "'seq_timeline_prediction', 'short_mot_prediction'], and goal_text is the default"
            ),
        )
        argparser = ParlAIDialogTeacher.add_cmdline_args(argparser, partial_opt)
        return argparser

    def __init__(self, opt, shared=None):
        opt = copy.deepcopy(opt)
        opt["light_datapath"] = opt.get("light_datapath", LIGHT_DATAPATH)
        build(opt)
        datafile = _path(opt)
        opt["parlaidialogteacher_datafile"] = datafile
        if shared is None:
            self._setup_data(datafile)
        self.id = datafile
        super().__init__(opt, shared)


class DefaultTeacher(QuestTeacher):
    def __init__(self, opt, shared=None):
        super().__init__(opt, shared)
