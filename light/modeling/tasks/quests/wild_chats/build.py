# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from copy import deepcopy, copy
import random
import io, os
import torch
import json
import numpy as np

from parlai.utils.misc import msg_to_str
from parlai.core.agents import create_agent
from parlai.core import build_data
import light.modeling.tasks.utils as utils
from parlai.core.build_data import DownloadableFile


rand = random.Random(42)
mx = 0
cands = {}

FUTURE_PARTNER_TAG = {
    "speech": "_future_partner_say",
    "action": "_future_partner_act",
    "emote": "_future_partner_emote",
}

ALL_ATYPES = ["speech", "action", "emote"]
MASK_WINDOW = 1

NULL_ACT_TAG = "_null_act"

NULL_TAG = {
    "speech": "_null_say",
    "action": "_null_act",
    "emote": "_null_emote",
}

RESOURCES = [
    DownloadableFile(
        "http://parl.ai/downloads/light_project/quests/wild_chats/formatted_wild_completions.json",
        "quests/wild_chats/formatted_wild_completions.json",
        "2ea8ae86a8f1f935d50055205a7d2cab243d8d01b34662cd7368cb2d578f5b8b",
        zipped=False,
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

        # Mark the data as built.
        build_data.mark_done(full_dpath, version)

    return full_dpath, version


def use_feat(opt, field, ttype):
    if "all" in opt.get(field) or opt.get(field) == ttype:
        return True
    else:
        return False


def fix_labels(act, opt):
    labels = act.get("labels", act.get("eval_labels"))
    clip = 100
    while len(act["label_candidates"]) >= clip:
        act["label_candidates"].pop()
    is_label_cand = {}
    for label in labels:
        is_label_cand[label] = False
    for cand in act["label_candidates"]:
        if cand in is_label_cand:
            is_label_cand[cand] = True
    for l, has_label in is_label_cand.items():
        if has_label == False:
            act["label_candidates"].append(l)


def write_dialog(opt, fw, d, masking_entities, noInst):
    d["speech"] = []
    d["action"] = []
    for a in d["acts"]:
        if a["type"] == "speech":
            text = a["text"].replace("\\u2018", "'").replace("\\u2019", "'")
            text = text.replace("\\u201c", '"').replace("\\u201d", '"')
            if "\\u" in text:
                text = (
                    text.encode("utf-8")
                    .decode("unicode-escape")
                    .encode("utf-16", "surrogatepass")
                    .decode("utf-16")
                )
            d["speech"].append(text)
        else:
            d["speech"].append("")

        if a["type"] == "action":
            d["action"].append(a["text"])
        else:
            d["action"].append("")

    l = len(d["speech"])
    msgs = []
    window = MASK_WINDOW
    for label_type in masking_entities:
        # idx is ending index - it should be a self turn
        for idx in range(1, l, 2):
            text = ""
            label = d[label_type][idx]
            if label == None or label == "":
                continue
            text += "_setting_name " + d["room"]["category"] + "\n"
            text += "_setting_desc " + d["room"]["description"] + "\n"
            text += "_partner_name " + d["partner_agent"][1]["name"] + "\n"
            text += "_self_name " + d["self_agent"][1]["name"] + "\n"
            text += "_self_persona " + d["self_agent"][1]["personas"][0] + "\n"
            text += "_partner_persona " + d["partner_agent"][1]["personas"][0] + "\n"
            text += "_self_motivation " + d["self_agent"][1]["motivation"] + "\n"
            text += "_partner_motivation " + d["partner_agent"][1]["motivation"] + "\n"
            future_used = False

            # construct dialogue by iterating from beginning to ending idx
            for i in range(0, l, 2):
                # Add past
                if opt["light_use_past"]:
                    if i <= idx - 1:
                        # add partner's turn - note that partner is always at index 0 (but it could be None)
                        if d["speech"][i] != "":
                            text += "_partner_say " + str(d["speech"][i]) + "\n"
                        if d["action"][i] != "":
                            text += "_partner_act " + str(d["action"][i]) + "\n"

                        if i < idx - 1:
                            # use self's turn if we're not at the end yet
                            if d["speech"][i + 1] != "":
                                text += "_self_say " + str(d["speech"][i + 1]) + "\n"
                            if d["action"][i + 1] != "":
                                text += "_self_act " + str(d["action"][i + 1]) + "\n"

                # Sometimes add current
                if i == idx - 1:
                    if (
                        use_feat(opt, "light_use_current_self_output", "speech")
                        and label_type != "speech"
                        and d["speech"][i + 1] != ""
                    ):
                        if "remove" not in opt["light_use_current_self_output"]:
                            text += "_self_say " + str(d["speech"][i + 1]) + "\n"
                    if (
                        use_feat(opt, "light_use_current_self_output", "action")
                        and label_type != "action"
                        and d["action"][i + 1] != ""
                    ):
                        if "remove" not in opt["light_use_current_self_output"]:
                            text += "_self_act " + str(d["action"][i + 1]) + "\n"

                # Add future
                if i == idx + 1 and idx + 1 < l and opt["light_use_future"]:
                    included_types = []
                    for atype in ALL_ATYPES:
                        dict_atype = "act" if atype == "action" else atype
                        if opt["light_use_future_" + dict_atype]:
                            included_types.append(atype)
                    futures = {}
                    for atype in included_types:
                        if d[atype][i] is not None:
                            future_used = True
                            futures[atype] = d[atype][i]
                    if not opt["strip_future"] and future_used:
                        for atype in included_types:
                            text += (
                                FUTURE_PARTNER_TAG[atype]
                                + " "
                                + futures.get(atype, NULL_TAG[atype])
                                + "\n"
                            )

            # if you're supposed to add a future and there wasn't one, ignore this sample
            if opt["light_use_future"] and not future_used and not opt["use_all_ex"]:
                continue
            msg = {}
            msg["text"] = text
            msg["labels"] = d[label_type][idx : idx + window]
            msg["episode_done"] = True
            add_negs(msg, d, idx, label_type, 100 - window)
            msgs.append(msg)
            noInst[label_type] += 1
    if len(msgs) > 0:
        for m in msgs:
            fix_labels(m, opt)
            global mx
            mx = max(len(m["label_candidates"]), mx)
            txt = msg_to_str(m)
            fw.write(txt + "\n")

    return noInst


def write_alldata(opt, db, dpath, split_name):
    masking_entities = ["speech", "action"]
    noInst = {"speech": 0, "emote": 0, "action": 0}

    fname = os.path.join(dpath, split_name + ".txt")
    fw_tst = io.open(fname, "w")
    for d in db:
        d = d["conv_info"]
        d["self_agent"] = d["characters"][1]
        d["partner_agent"] = d["characters"][0]
        noInst = write_dialog(opt, fw_tst, d, masking_entities, noInst)

    fw_tst.close()
    print("Written instances in " + fname)
    print(noInst)


def add_negs(msg, d, ind, label_type, num_cands):
    if label_type == "emote":
        emote_cands = copy(cands["emote"])
        np.random.shuffle(emote_cands)
        msg["label_candidates"] = emote_cands
    elif label_type == "action":
        msg["label_candidates"] = d["acts"][ind]["task_data"]["actions"]
    elif label_type == "speech":
        cnt = 0
        labels = msg["labels"]
        negs = []
        used = {}
        # find 99 random negs that are != gold label
        while cnt < num_cands:
            ind = rand.randint(0, len(cands["speech"]) - 1)
            txt = cands["speech"][ind]
            if txt not in labels and ind not in used:
                negs.append(txt)
                used[ind] = True
                cnt += 1

        # insert label in a random position
        for label in labels:
            insert_pos = rand.randrange(len(negs) + 1)
            negs.insert(insert_pos, label)
        msg["label_candidates"] = negs


# candidates
def write_out_candidates(db, dpath, dtype):
    emotes = {}
    acts = {}
    cands["action"] = set()
    cands["speech"] = set()
    for d in db:
        for a in d["conv_info"]["acts"]:
            if a["type"] == "speech":
                cands["speech"].add(a["text"])
            elif a["type"] == "action":
                cands["action"].add(a["text"])

    cands["speech"] = list(cands["speech"])
    cands["action"] = list(cands["action"])
    for l in ["speech", "action"]:
        curpath = os.path.join(dpath, l + "_" + dtype + "_cands.txt")
        fw = io.open(curpath, "w")
        for k in cands[l]:
            fw.write(k + "\n")
        fw.close()
    return cands


def build_from_db(opt, db_path, data_path):
    # set up database
    proc_files = [os.path.join(db_path, "formatted_wild_completions.json")]
    for dbp in proc_files:
        with open(dbp) as json_file:
            db_init = json.load(json_file)
        percsize = 0.01 * len(db_init)
        dbs = (
            db_init[: int(80 * percsize)],
            db_init[int(80 * percsize) : int(90 * percsize)],
            db_init[int(90 * percsize) :],
        )

        for db, split_name in zip(dbs, ["train", "valid", "test"]):
            write_out_candidates(db, data_path, split_name)
            write_alldata(opt, db, data_path, split_name)


def opt_to_path(opt):
    """
    Return the proper path to write out for the specific options
    """
    times = ["past", "future"]
    fpath = "predict__using"

    for t in times:
        fpath = fpath + t if opt["light_use_" + t] else fpath
    if opt["light_use_current_self_output"] != "none":
        fpath = fpath + "current" + opt["light_use_current_self_output"]
    fpath += "__"

    fpath += "futureSpeech" + str(opt["light_use_future_speech"]) + "_"
    fpath += "futureAct" + str(opt["light_use_future_act"]) + "_"
    fpath += "futureEmote" + str(opt["light_use_future_emote"])

    if opt["use_all_ex"]:
        fpath += "_useall"
    if opt["strip_future"]:
        fpath += "_stripfuture"

    return fpath


def build(opt):
    # Download if necessary
    dpath, version = download(opt, "quests/wild_chats")

    # create particular instance of dataset depending on flags..
    fpath = opt_to_path(opt)

    opath = os.path.join(dpath, fpath)

    if not build_data.built(opath, version):
        print("rebuilding")
        if build_data.built(opath):
            # An older version exists, so remove these outdated files.
            build_data.remove_dir(opath)
        build_data.make_dir(opath)
        build_from_db(opt, dpath, opath)
        # Mark the data as built.
        build_data.mark_done(opath, version)
