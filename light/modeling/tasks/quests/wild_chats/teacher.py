#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from light.modeling.tasks.quests.wild_chats.build import build, opt_to_path
from parlai.core.teachers import ParlAIDialogTeacher
from parlai.core.loader import register_teacher
from light.constants import LIGHT_DATAPATH
from parlai.utils.misc import str_to_msg

import copy
import os
import random


def _path(opt):
    opt["datatype"] = opt["datatype"].split(":")[0]
    return os.path.join(
        opt["light_datapath"],
        "quests/wild_chats",
        opt_to_path(opt),
        opt["datatype"] + ".txt",
    )


@register_teacher("light:quest_wild_completions")
class QuestHobbotTeacher(ParlAIDialogTeacher):
    """
    Teacher of supervised dialogue turns that agents used towards completing
    quests in the messenger release of the LIGHT game.
    """

    def __init__(self, opt, shared=None):
        opt = copy.deepcopy(opt)
        self.opt = opt
        opt["light_datapath"] = opt.get("light_datapath", LIGHT_DATAPATH)
        build(opt)
        opt["parlaidialogteacher_datafile"] = _path(opt)
        super().__init__(opt, shared)

    @staticmethod
    def add_cmdline_args(argparser, partial_opt=None):
        argparser.add_argument(
            "--light_use_current_self_output",
            type=str,
            default="none",
            choices=[
                "none",
                "speech",
                "act",
                "emote",
                "all",
                "all_filtered",
                "all_filtered_remove",
            ],
        )

        argparser.add_argument("--light_use_future", action="store_true")
        argparser.add_argument("--light_use_past", action="store_true")

        argparser.add_argument("--light_use_future_speech", action="store_true")
        argparser.add_argument("--light_use_future_act", action="store_true")
        argparser.add_argument("--light_use_future_emote", action="store_true")

        argparser.add_argument("--use_all_ex", action="store_true")
        argparser.add_argument("--strip_future", action="store_true")

        argparser = ParlAIDialogTeacher.add_cmdline_args(argparser, partial_opt)
        return argparser


class DefaultTeacher(QuestHobbotTeacher):
    def __init__(self, opt, shared=None):
        super().__init__(opt, shared)
