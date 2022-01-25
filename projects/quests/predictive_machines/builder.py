#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import parlai_internal.tasks.light_maps.utils as utils
from copy import deepcopy, copy
import random
import io, os
import torch
import pickle
import numpy as np

# from constants import *

from parlai.utils.misc import msg_to_str
from parlai.core.agents import create_agent

rand = random.Random(42)
mx = 0
cands = {}

FUTURE_PARTNER_TAG = {
    "speech": "_future_partner_say",
    "action": "_future_partner_act",
    "emote": "_future_partner_emote",
}

ALL_ATYPES = ["speech", "action", "emote"]

NULL_ACT_TAG = "_null_act"

NULL_TAG = {
    "speech": "_null_say",
    "action": "_null_act",
    "emote": "_null_emote",
}


def use_feat(opt, field, ttype):
    if "all" in opt.get(field) or opt.get(field) == ttype:
        return True
    else:
        return False


def fix_labels(act, opt):
    labels = act.get("labels", act.get("eval_labels"))
    clip = int(opt.get("light_use_clip_cands", 1000))
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
            # print("***ADDING A LABEL CAND****")
            act["label_candidates"].append(l)


def load_cluster(opt):
    cluster_encoder_file = os.path.join(
        opt["cluster_folder"], str(opt["num_clusters"]), "kmeans", "KMeans_clust.v0.pt"
    )
    checkpoint = torch.load(cluster_encoder_file)
    algo = checkpoint["algo"]
    return algo


def get_encoding(input, encoder):
    inp_dict = {"text": input, "episode_done": True}
    encoder.observe(inp_dict)
    output = deepcopy(encoder.act())
    encoding = output["embedding_ctx"]

    return encoding


def write_dialog(opt, fw, d, masking_entities, noInst, algo, encoder):
    l = len(d["speech"])
    msgs = []
    window = opt["light_mask_window"]
    for label_type in masking_entities:
        # idx is ending index - it should be a self turn
        for idx in range(1, l, 2):
            text = ""
            label = d[label_type][idx]
            if label == None:
                continue
            if not opt["light_use_only_cluster"]:
                if opt["light_use_setting"]:
                    text += (
                        "_setting_name "
                        + d["setting"]["name"]
                        + ", "
                        + d["setting"]["category"]
                        + "\n"
                    )
                    text += "_setting_desc " + d["setting"]["description"] + "\n"
                if opt["light_use_person_names"]:
                    text += "_partner_name " + d["partner_agent"]["name"] + "\n"
                    text += "_self_name " + d["self_agent"]["name"] + "\n"
                if use_feat(opt, "light_use_persona", "self"):
                    text += "_self_persona " + d["self_agent"]["persona"] + "\n"
                if use_feat(opt, "light_use_persona", "other"):
                    text += "_other_persona " + d["partner_agent"]["persona"] + "\n"
                future_used = False

                # construct dialogue by iterating from beginning to ending idx
                for i in range(0, l, 2):
                    # Add past
                    if opt["light_use_past"]:
                        if i <= idx - 1:
                            # add partner's turn - note that partner is always at index 0 (but it could be None)
                            if (
                                use_feat(opt, "light_use_speech", "partner")
                                and d["speech"][i] != None
                            ):
                                text += "_partner_say " + str(d["speech"][i]) + "\n"
                            if (
                                use_feat(opt, "light_use_action", "partner")
                                and d["action"][i] != None
                            ):
                                text += "_partner_act " + str(d["action"][i]) + "\n"
                            if (
                                use_feat(opt, "light_use_emote", "partner")
                                and d["emote"][i] != None
                            ):
                                text += "_partner_emote " + str(d["emote"][i]) + "\n"

                            if i < idx - 1:
                                # use self's turn if we're not at the end yet
                                if (
                                    use_feat(opt, "light_use_speech", "self")
                                    and d["speech"][i + 1] != None
                                ):
                                    text += (
                                        "_self_say " + str(d["speech"][i + 1]) + "\n"
                                    )
                                if (
                                    use_feat(opt, "light_use_action", "self")
                                    and d["action"][i + 1] != None
                                ):
                                    text += (
                                        "_self_act " + str(d["action"][i + 1]) + "\n"
                                    )
                                if (
                                    use_feat(opt, "light_use_emote", "self")
                                    and d["emote"][i + 1] != None
                                ):
                                    text += (
                                        "_self_emote " + str(d["emote"][i + 1]) + "\n"
                                    )
                    # Sometimes add current, always add missing label
                    if i == idx - 1:
                        if (
                            use_feat(opt, "light_use_current_self_output", "speech")
                            and label_type != "speech"
                            and use_feat(opt, "light_use_speech", "self")
                            and d["speech"][i + 1] != None
                        ):
                            if "remove" not in opt["light_use_current_self_output"]:
                                text += "_self_say " + str(d["speech"][i + 1]) + "\n"
                        if (
                            use_feat(opt, "light_use_current_self_output", "action")
                            and label_type != "action"
                            and use_feat(opt, "light_use_action", "self")
                            and d["action"][i + 1] != None
                        ):
                            if "remove" not in opt["light_use_current_self_output"]:
                                text += "_self_act " + str(d["action"][i + 1]) + "\n"
                        if (
                            use_feat(opt, "light_use_current_self_output", "emote")
                            and label_type != "emote"
                            and use_feat(opt, "light_use_emote", "self")
                            and d["emote"][i + 1] != None
                        ):
                            if "remove" not in opt["light_use_current_self_output"]:
                                text += "_self_emote " + str(d["emote"][i + 1]) + "\n"
                        if (
                            "all_filtered" in opt["light_use_current_self_output"]
                            and used_current == False
                        ):
                            label = None
                        text += "_missing_self_" + label_type + "\n"
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

                        # if opt['light_use_future_speech'] and d['speech'][i] != None:
                        #     future_used = True
                        #     if not opt['strip_future']:
                        #         text +=  '_future_partner_say ' + str(d['speech'][i]) + '\n'
                        # if opt['light_use_future_act'] and d['action'][i] != None:
                        #     future_used = True
                        #     if not opt['strip_future']:
                        #         text +=  '_future_partner_act ' + str(d['action'][i]) + '\n'
                        # if opt['light_use_future_emote'] and d['emote'][i] != None:
                        #     future_used = True
                        #     if not opt['strip_future']:
                        #         text +=  '_future_partner_emote ' + str(d['emote'][i]) + '\n'
                # if you're supposed to add a future and there wasn't one, ignore this sample
                if (
                    opt["light_use_future"]
                    and not future_used
                    and not opt["use_all_ex"]
                ):
                    continue
            msg = {}
            if algo:
                encoding = get_encoding(d[label_type][idx], encoder)
                encoding = encoding.unsqueeze(0)
                cluster = algo.predict(encoding.cpu().numpy())
                text += "_cluster" + str(cluster[0])
            msg["text"] = text
            msg["labels"] = d[label_type][idx : idx + window]
            msg["episode_done"] = True
            add_negs(
                msg, d, idx, label_type, int(opt.get("light_use_cands", 100)) - window
            )
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


def write_alldata(opt, db, dpath, split_name, algo, encoder):
    masking_entities = []
    if opt["light_mask_speech"]:
        masking_entities.append("speech")
    if opt["light_mask_emote"]:
        masking_entities.append("emote")
    if opt["light_mask_action"]:
        masking_entities.append("action")
    noInst = {"speech": 0, "emote": 0, "action": 0}

    # for now train, valid and test will all be identical
    fname = os.path.join(dpath, split_name + ".txt")
    fw_tst = io.open(fname, "w")
    for d in db:
        d["self_agent"] = d["agents"][1]
        d["partner_agent"] = d["agents"][0]
        noInst = write_dialog(opt, fw_tst, d, masking_entities, noInst, algo, encoder)
        # break
        # now flip the conversation around so the target is the other speaker..
        d2 = d.copy()
        d2["self_agent"] = d2["agents"][0]
        d2["partner_agent"] = d2["agents"][1]
        d2["speech"] = list(d2["speech"])
        d2["speech"].insert(0, None)
        d2["emote"] = list(d2["emote"])
        d2["emote"].insert(0, None)
        d2["action"] = list(d2["action"])
        d2["action"].insert(0, None)
        d2["available_actions"] = list(d2["available_actions"])
        d2["available_actions"].insert(0, None)
        noInst = write_dialog(opt, fw_tst, d2, masking_entities, noInst, algo, encoder)

    fw_tst.close()
    print("Written instances in " + fname)
    print(noInst)


def add_negs(msg, d, ind, label_type, num_cands):
    if label_type == "emote":
        emote_cands = copy(cands["emote"])
        np.random.shuffle(emote_cands)
        msg["label_candidates"] = emote_cands
        # print(emote_cands)
    elif label_type == "action":
        msg["label_candidates"] = d["available_actions"][ind]
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
    cands["emote"] = []
    cands["action"] = []
    cands["speech"] = []
    for d in db:
        for e in d.get("emote", []):
            if e != None and e not in emotes:
                cands["emote"].append(e)
                emotes[e] = True
        for act in d["action"]:
            if act != None and act not in acts:
                cands["action"].append(act)
                acts[act] = True
        for s in d["speech"]:
            if s != None:
                cands["speech"].append(s)

    for l in ["emote", "speech", "action"]:
        fw = io.open(os.path.join(dpath, l + "_" + dtype + "_cands.txt"), "w")
        for k in cands[l]:
            fw.write(k + "\n")
        fw.close
    return cands


def build_from_db(opt, db_path, data_path):

    if opt["light_add_cluster"] or opt["light_use_only_cluster"]:
        algo = load_cluster(opt)
        Encoder_opt = {
            "model_file": opt["cluster_encoder_file"],
            "override": {
                "model": "parlai_internal.projects.light_rl." "rl_agent:RLAgent"
            },
        }
        encoder = create_agent(Encoder_opt)
    else:
        algo = None
        encoder = None

    # set up database
    proc_files = os.listdir(db_path)
    for fname in proc_files:
        dbp = os.path.join(db_path, fname)
        file = open(dbp, "rb")
        db = pickle.load(file)
        split_name = fname.split("_")[0]
        write_out_candidates(db, data_path, split_name)
        write_alldata(opt, db, data_path, split_name, algo, encoder)
