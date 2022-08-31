#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import parlai.core.build_data as build_data
import os
from .builder import build_from_db
from parlai.core.params import ParlaiParser
import light.modeling.tasks.utils as utils
from parlai.core.build_data import DownloadableFile

ParlaiParser()  # instantiate to set PARLAI_HOME environment var

PARLAI_PATH = os.environ["PARLAI_HOME"]
USER = os.environ["USER"]


RESOURCES = [
    DownloadableFile(
        "http://parl.ai/downloads/light_project/quests/quest_predictive_machine_resources.tar.gz",
        "quests/quest_predictive_machine_resources.tar.gz",
        "cb966bd6b7a4d0bd56e8b39abf99fbdd30f8df80b2d2cafc577f39f16b96ff43",
        zipped=True,
    ),
]


def download(opt, version):
    base_dpath = opt["light_datapath"]
    full_dpath = os.path.join(base_dpath, "quests/pred_mach_models/")
    if not build_data.built(full_dpath, version):
        print("[building data: " + full_dpath + "]")
        if build_data.built(full_dpath):
            # An older version exists, so remove these outdated files.
            build_data.remove_dir(full_dpath)
        build_data.make_dir(full_dpath)

        # Download the data.
        for downloadable_file in RESOURCES:
            utils.download_for_light(base_dpath, downloadable_file)

        # Mark the data as built.
        build_data.mark_done(full_dpath, version)

    return full_dpath, version


def build(opt):
    version = "3"
    dpath = os.path.join(opt["light_datapath"], "quests/predictive_machines/")

    # create particular instance of dataset depending on flags..
    fields = ["emote", "speech", "action"]
    times = ["past", "future"]
    fpath = "predict"

    print("BUILD light_mask_speech", opt["light_mask_speech"])
    for f in fields:
        if opt["light_mask_" + f]:
            print(f, opt["light_mask_" + f])
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
    print(fpath)
    dpath2 = os.path.join(dpath, fpath)

    if not build_data.built(dpath2, version):
        if build_data.built(dpath2):
            # An older version exists, so remove these outdated files.
            build_data.remove_dir(dpath2)
        build_data.make_dir(dpath2)
        build_from_db(opt, dpath, dpath2)
        # Mark the data as built.
        build_data.mark_done(dpath2, version)
