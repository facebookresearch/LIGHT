# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import parlai.core.build_data as build_data
import os
from parlai.tasks.light_dialog.builder import build_from_db

import json
import shutil
from glob import glob
import light.modeling.tasks.utils as utils
from parlai.core.build_data import DownloadableFile
from parlai.utils.misc import msg_to_str
import random
import itertools
import json


RESOURCES = [
    DownloadableFile(
        "http://parl.ai/downloads/light_project/quests/quest_stems.tar.gz",
        "quests/stems/batch_1.tar.gz",
        "743d9a9dc85e9fd7737c6cb51762deae684382de326bf724cde5b72bcf7c7c7d",
        zipped=True,
    ),
]


def download(opt, task):
    version = "v1.0"
    base_dpath = opt["light_datapath"]
    full_dpath = os.path.join(base_dpath, task)
    if not build_data.built(full_dpath, version):
        print("[building data: " + full_dpath + "]")
        if build_data.built(full_dpath):
            # An older version exists, so remove these outdated files.
            build_data.remove_dir(full_dpath)
        build_data.make_dir(full_dpath)

        # Download the data.
        for downloadable_file in RESOURCES:
            utils.download_for_light(base_dpath, downloadable_file)

        # correct batch_1 stem name
        os.rename(
            os.path.join(base_dpath, "quests/stems/quest_stems"),
            os.path.join(base_dpath, "quests/stems/batch_1"),
        )

        # Mark the data as built.
        build_data.mark_done(full_dpath, version)

    return full_dpath, version


def clean(string):
    string = " ".join(string.split()).strip()
    string = string.replace(".", "")
    return string


def build_quests(dpath, odpath, opt):
    task = opt["subtask"]
    data_raw_all = []
    output_fname = os.path.join(odpath, task + "_sample")

    target_stems = os.path.join(dpath, "../stems/batch_1/*.json")
    for fname in glob(target_stems):
        with open(fname, "r") as f:
            data_raw_all.append(json.load(f)["data"])

    x = int(0.1 * len(data_raw_all))
    # fixed seed shuffle
    random.seed(42)
    random.shuffle(data_raw_all)
    data_raw_splits = {"train": [], "valid": [], "test": []}
    data_raw_splits["train"] = data_raw_all[: 8 * x]
    data_raw_splits["valid"] = data_raw_all[8 * x : 9 * x]
    data_raw_splits["test"] = data_raw_all[9 * x :]

    for spl in ["train", "valid", "test"]:
        data_raw_all = data_raw_splits[spl]
        data_curr = []
        output_file = open(output_fname + "_" + spl + ".txt", "w")

        if task == "goal_text_prediction":
            label_candidates_all = [utils.clean(d["goal"]) for d in data_raw_all]
        elif task == "boa_timeline_prediction" or task == "seq_timeline_prediction":
            label_candidates_all = list(
                itertools.chain.from_iterable(
                    [
                        [utils.clean(a["action"]) for a in d["timeline"]]
                        for d in data_raw_all
                    ]
                )
            )
            label_candidates_all += [utils.clean(d["goal"]) for d in data_raw_all]
        elif task == "short_mot_prediction":
            label_candidates_all = [
                utils.clean(d["short_motivation"]) for d in data_raw_all
            ]

        for data in data_raw_all:
            text = ""
            text += "_task_" + task + "\n"
            text += "_setting_name " + data["description"].replace("\n", " ") + "\n"
            text += "_name " + data["character"] + "\n"
            text += "_persona " + data["persona"] + "\n"
            queries = []

            if task == "seq_timeline_prediction":
                text += "_long_mot " + data["long_motivation"] + "\n"
                text += "_mid_mot " + data["mid_motivation"] + "\n"
                text += "_short_mot " + data["short_motivation"]
                text += "[ACT] "

                actions = [utils.clean(a["action"]) for a in data["timeline"]]
                actions.insert(3, utils.clean(data["goal"]))
                # always only within the quest
                label_candidates = actions

                for i in range(len(actions) - 1):
                    cur_acts = actions[i]
                    label = actions[i + 1]

                    label_candidates_curr = utils.get_fixed_candidates(
                        label_candidates_all, label_candidates
                    )
                    assert label in label_candidates_curr

                    queries.append(
                        {
                            "text": text + cur_acts,
                            "labels": label,
                            "label_candidates": label_candidates_curr,
                        }
                    )
                    text = "[ACT] "

            elif task == "goal_text_prediction":
                text += "_long_mot " + data["long_motivation"] + "\n"
                text += "_mid_mot " + data["mid_motivation"] + "\n"
                text += "_short_mot " + data["short_motivation"]
                label = utils.clean(data["goal"])
                label_candidates = utils.get_fixed_candidates(
                    label_candidates_all, [label]
                )
                assert label in label_candidates
                queries.append(
                    {
                        "text": text,
                        "labels": label,
                        "label_candidates": label_candidates,
                    }
                )
            elif task == "short_mot_prediction":
                text += "_long_mot " + data["long_motivation"] + "\n"
                text += "_mid_mot " + data["mid_motivation"] + "\n"
                text += "_goal " + data["goal"]
                label = utils.clean(data["short_motivation"])
                label_candidates = utils.get_fixed_candidates(
                    label_candidates_all, [label]
                )
                assert label in label_candidates
                queries.append(
                    {
                        "text": text,
                        "labels": label,
                        "label_candidates": label_candidates,
                    }
                )
            elif task == "boa_timeline_prediction":
                text += "_long_mot " + data["long_motivation"] + "\n"
                text += "_mid_mot " + data["mid_motivation"] + "\n"
                text += "_short_mot " + data["short_motivation"]
                actions = [utils.clean(d["action"]) for d in data["timeline"]]
                actions.insert(3, utils.clean(data["goal"]))

                label = actions
                label_candidates = utils.get_fixed_candidates(
                    label_candidates_all, label
                )
                queries.append(
                    {
                        "text": text,
                        "labels": label,
                        "label_candidates": label_candidates,
                    }
                )

            queries[-1]["episode_done"] = True
            for q in queries:
                output_file.write(msg_to_str(q) + "\n")

        output_file.close()


def build(opt):
    # get path to data directory
    dpath, version = download(opt, "quests/base")

    subtask = opt["subtask"]
    odpath = os.path.join(dpath, subtask)

    if not build_data.built(odpath, version_string=version):
        if build_data.built(odpath):
            # an older version exists, so remove these outdated files.
            build_data.remove_dir(odpath)
        build_data.make_dir(odpath)
        build_quests(dpath, odpath, opt)
        build_data.mark_done(odpath, version_string=version)
