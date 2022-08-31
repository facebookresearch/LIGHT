#!/usr/bin/env python3


# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai.core.teachers import ParlAIDialogTeacher, MultiTaskTeacher
from parlai.utils.misc import str_to_msg
from parlai_internal.projects.light.quests.tasks.quest_predictive_machines.build import (
    build,
)

from light.constants import LIGHT_DATAPATH

import copy
import os
import random

from parlai.core.params import ParlaiParser

ParlaiParser()  # instantiate to set PARLAI_HOME environment var

PARLAI_PATH = os.environ["PARLAI_HOME"]

DEFAULT_CLUSTER_DIR = os.path.join(LIGHT_DATAPATH, "quests/pred_mach_models/clusters")
CLUSTER_ENCODER_MODEL_FILE = os.path.join(
    LIGHT_DATAPATH, "quests/pred_mach_models/biranker_dialogue/model"
)


def _path(opt):
    # Build the data if it doesn't exist.
    build(opt)
    dt = opt["datatype"].split(":")[0]
    fields = ["emote", "speech", "action"]
    times = ["past", "future"]
    fpath = "predict"
    # print('AGENTS light_mask_speech', opt['light_mask_speech'])
    for f in fields:
        # if opt['light_mask_' + f]:
        #     print(f, opt['light_mask_' + f])
        fpath = fpath + f if opt["light_mask_" + f] else fpath
    fpath += "___using"
    if opt["light_use_only_cluster"]:
        fpath += "ClusterOnly"
    else:
        for t in times:
            fpath = fpath + t if opt["light_use_" + t] else fpath
        fpath = (
            fpath + "current" + opt["light_use_current_self_output"]
            if opt["light_use_current_self_output"] != "none"
            else fpath
        )
        fpath += "___"

        fpath += "futureSpeech" + str(opt["light_use_future_speech"]) + "_"
        fpath += "futureAct" + str(opt["light_use_future_act"]) + "_"
        fpath += "futureEmote" + str(opt["light_use_future_emote"]) + "_"
        fpath += "cluster" + str(opt["light_add_cluster"])
        if opt["light_add_cluster"]:
            fpath += str(opt["num_clusters"])
        if opt["use_all_ex"]:
            fpath += "_useall"
        if opt["strip_future"]:
            fpath += "_stripfuture"
    # print(fpath)
    return os.path.join(
        opt["light_datapath"], "quests/predictive_machines/", fpath, dt + ".txt"
    )


class DefaultTeacher(ParlAIDialogTeacher):
    @staticmethod
    def add_cmdline_args(argparser, partial_opt=None):
        agent = argparser.add_argument_group("LIGHT Dialogue options")
        agent.add_argument(
            "--light_use_repeat",
            type=str,
            default="none",
            choices=["self_last", "partner_last", "none", "both_last"],
        )
        agent.add_argument("--light_use_setting", type="bool", default=True)
        agent.add_argument("--light_unseen_test", type="bool", default=False)
        agent.add_argument("--light_use_person_names", type="bool", default=True)
        agent.add_argument(
            "--light_use_persona",
            type=str,
            default="self",
            choices=["partner", "self", "all", "none"],
        )
        agent.add_argument("--light_use_objects", type="bool", default=False)
        agent.add_argument(
            "--light_use_emote",
            type=str,
            default="all",
            choices=["partner", "self", "all", "none"],
        )
        agent.add_argument(
            "--light_use_speech",
            type=str,
            default="all",
            choices=["partner", "self", "all", "none"],
        )
        agent.add_argument(
            "--light_use_action",
            type=str,
            default="all",
            choices=["partner", "self", "all", "none"],
        )
        agent.add_argument(
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
        agent.add_argument(
            "--light_label_type",
            type=str,
            default="speech",
            choices=["speech", "action", "emote"],
            help="type of target in light dialogues",
        )
        agent.add_argument("--light_use_cands", type=int, default=20)
        agent.add_argument("--light_use_clip_cands", type=int, default=20)

        # Flags for masking
        agent.add_argument("--light_mask_speech", type="bool", default=False)
        agent.add_argument("--light_mask_emote", type="bool", default=False)
        agent.add_argument("--light_mask_action", type="bool", default=False)
        agent.add_argument("--light_mask_window", type=int, default=1)
        agent.add_argument("--light_use_future", type=bool, default=False)
        agent.add_argument("--light_use_future_speech", type="bool", default=False)
        agent.add_argument("--light_use_future_act", type="bool", default=False)
        agent.add_argument("--light_use_future_emote", type="bool", default=False)

        # Flag for clusters
        agent.add_argument("--light_use_only_cluster", type="bool", default=False)
        agent.add_argument("--num_clusters", type=int, default=50)
        agent.add_argument("--light_add_cluster", type=str, default=False)
        agent.add_argument("--cluster_folder", type=str, default=DEFAULT_CLUSTER_DIR)
        agent.add_argument(
            "--cluster_encoder_file", type=str, default=CLUSTER_ENCODER_MODEL_FILE
        )

        # Flag to use future
        agent.add_argument("--light_use_past", type="bool", default=True)

        agent.add_argument("--use_all_ex", type="bool", default=False)
        agent.add_argument("--strip_future", type="bool", default=False)
        argparser = ParlAIDialogTeacher.add_cmdline_args(argparser, partial_opt)
        return argparser

    def __init__(self, opt, shared=None):
        opt = copy.deepcopy(opt)
        opt["light_datapath"] = opt.get("light_datapath", LIGHT_DATAPATH)
        self.opt = opt
        opt["parlaidialogteacher_datafile"] = _path(opt)
        super().__init__(opt, shared)

    def _setup_data(self, path):
        print("[loading parlAI text data:" + path + "]")
        self.episodes = []
        self.num_exs = 0
        eps = []
        with open(path) as read:
            for line in read:
                msg = str_to_msg(line.rstrip("\n"))
                if msg:
                    self.num_exs += 1
                    lab_cand = msg.get("label_candidates")
                    if lab_cand is None:
                        print(msg)
                        continue
                    no_labs = self.opt["light_use_clip_cands"]
                    if len(lab_cand) > no_labs:
                        label = msg.get("labels")
                        lab_idx = lab_cand.index(label[0])
                        lab_cand.pop(lab_idx)
                        cand_trim = random.sample(lab_cand, no_labs - 1)
                        insert_pos = random.randrange(len(cand_trim) + 1)
                        cand_trim.insert(insert_pos, label[0])
                        msg["label_candidates"] = cand_trim

                    eps.append(msg)
                    if msg.get("episode_done", False):
                        self.episodes.append(eps)
                        eps = []
        if len(eps) > 0:
            # add last episode
            eps[-1]["episode_done"] = True
            self.episodes.append(eps)
