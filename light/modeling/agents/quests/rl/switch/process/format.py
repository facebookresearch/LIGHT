#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import pickle
from glob import glob
import json
from light.graph.structured_graph import OOGraph
from light.world.world import World
from light.constants import LIGHT_DATAPATH
import copy

import os
from light.modeling.agents.quests.rl.switch.environments import quest
import math

import light.modeling.tasks.utils as utils
from parlai.core.build_data import DownloadableFile
import parlai.core.build_data as build_data


RESOURCES = [
    DownloadableFile(
        "http://parl.ai/downloads/light_project/quests/rl_quests_resources.tar.gz",
        "quests/rl_quests_resources.tar.gz",
        "baf958329e04d7366900b4c02f5af3d4b9e2db731fa24a72d2c3d2f0d0643f95",
        zipped=True,
    ),
]


def download(version):
    base_dpath = LIGHT_DATAPATH
    full_dpath = os.path.join(base_dpath, "quests/rl_quests_resources/")
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


conv_pickle_template = {
    "graph": None,
    "accepted_agents": [],
    "conv_info": {
        "acts": [],
        "room": {
            "category": "",
            "setting": "",
            "description": "",
            "background": "",
            "neighbors": [],
            "in_characters": [],
            "ex_characters": [],
            "in_objects": [],
            "ex_objects": [],
            "id": 0,
        },
        "characters": [],
        "needs-pickle": None,
    },
}

act_template = {
    "text": "",
    "type": "",
    "score": 0,
    "task_data": {
        "action": "",
        "carrying": [],
        "wearing": [],
        "wielding": [],
        "actions": [],
        "text_context": "",
        "room_objects": [],
        "room_agents": [],
        "setting": "",
        "persona": "",
    },
    "id": "",
    "message_id": "",
    "episode_done": False,
    "duration": 0,
}

char_template = [
    ("", ""),
    {
        "base_form": [],
        "corrected_name": "",
        "personas": [],
        "character_id": 0,
        "name": "",
        "is_plural": 0,
        "char_type": "person",
        "orig_room_id": 0,
        "carrying_objects": [],
        "wearing_objects": [],
        "wielding_objects": [],
        "desc": "",
        "goal": "",
        "motivation": "",
        "motivation_type": "",
        "id": 0,
    },
]

USE_ACTIONS = [
    "follow",
    "hit",
    "hug",
    "get",
    "put",
    "drop",
    "steal",
    "give",
    "wear",
    "wield",
    "remove",
    "eat",
    "drink",
]


def preprocess(args):
    version = "1.0"
    download(version)

    target_path = os.path.join(
        LIGHT_DATAPATH,
        "quests/rl_quests_resources/",
        args["allfname"],
    )

    if build_data.built(target_path, version):
        # Build already exists, return values
        with open(os.path.join(target_path, "meta.json")) as jsonf:
            res = json.load(res)
        return res[0], (res[1], res[2]), res[3]
    elif build_data.built(target_path):
        # Build data exists, but isn't correct version
        build_data.remove_dir(target_path)

    # Build things anew
    def sequence(dialogue):
        c = 0
        s = 0
        for dial in dialogue[1:]:

            if dial["type"] == "action" and dial["text"] != "":
                c += 1

            if dial["type"] == "speech" and dial["text"] != "":
                s += 1

            if dial["id"] == "human":
                if dial["score"] == 5:
                    break

        if c <= args["quest_len"] - 1:
            return False, c, s

        return True, c, s

    all_quests = []
    speech_cands = set()

    hobbot_raw = json.loads(
        open(
            os.path.join(
                LIGHT_DATAPATH,
                "quests/rl_quests_resources/wild_quest_completions/perfect2.json",
            ),
            "r",
        ).read()
    )

    act_cands = set()
    reverse_act_cands = set()

    # hobbot_raw = hobbot_raw[0:8]
    save_act_cands = set()
    save_speech_cands = set()

    hobbot_raw_filtered = []

    act_quest_len, speech_quest_len = 0, 0

    for rawuf in hobbot_raw:
        if int(rawuf["score"]) < 10:
            continue
        dialogue = rawuf["dialogue"]
        chk, a, s = sequence(dialogue)
        if not chk:
            continue
        act_quest_len += a
        speech_quest_len += s
        hobbot_raw_filtered.append(rawuf)

    avg_act_seq = float(act_quest_len) / len(hobbot_raw_filtered)
    avg_speech_seq = float(speech_quest_len) / len(hobbot_raw_filtered)
    print("Avg seq lengths act and speech: ", avg_act_seq, avg_speech_seq)
    act_len = 0
    save_idx = list(range(args["num_quests"])) + list(
        range(500, len(hobbot_raw_filtered))
    )

    for j, raw in enumerate(hobbot_raw_filtered):
        dialogue = raw["dialogue"]
        human = raw["human_persona"]
        bot = raw["bot_persona"]
        location = raw["location"]
        quest_file = json.load(
            open(
                os.path.join(
                    LIGHT_DATAPATH, "quests/stems/batch_1", location["quest_file"]
                ),
                "r",
            )
        )["data"]

        # TODO Add timeline actions and also all actions that the players have actually taken as bag of actions
        graph_json = quest_file["graph"]

        g = OOGraph.from_json(graph_json)
        world = World({}, None)
        world.oo_graph = g

        # print(world.get_possible_actions(human['id'], USE_ACTIONS))

        curr_conv = copy.deepcopy(conv_pickle_template)

        curr_conv["graph"] = world  # graph_json
        curr_conv["accepted_agents"] = [bot["name"], human["name"]]
        actions = world.get_possible_actions(human["id"], USE_ACTIONS)
        act_len += len(actions)
        act_cands.update(actions)
        reverse_actions = world.get_possible_actions(bot["id"], USE_ACTIONS)
        reverse_act_cands.update(reverse_actions)
        rev_goal = quest.reverse_task(human["goal"], human["name"], bot["name"])
        if rev_goal != "":
            reverse_act_cands.add(rev_goal)

        # if j in save_idx:
        #    save_act_cands.update(actions)

        for cidx, char in enumerate([bot, human]):
            cur_char = copy.deepcopy(char_template)
            cur_char[0] = (char["name"], char["id"])
            cur_char[1]["base_form"] = [char["name"]]
            cur_char[1]["corrected_name"] = cur_char[1]["name"] = char["name"]
            # print(world.node_to_desc_raw(char['id']))
            cur_char[1]["desc"] = char["persona"]
            cur_char[1]["personas"].append(char["persona"])
            if "motivation" in char.keys():
                cur_char[1]["motivation"] = char["motivation"]
                for mot in ["long", "mid", "short"]:
                    if char["motivation"] == quest_file[mot + "_motivation"]:
                        cur_char[1]["motivation_type"] = mot
                        break
            if "goal" in char.keys():
                cur_char[1]["goal"] = char["goal"]
                act_cands.add(char["goal"])
                if j in save_idx:
                    save_act_cands.add(char["goal"])

            curr_conv["conv_info"]["characters"].append(cur_char)

        curr_conv["conv_info"]["room"]["category"] = location["name"]
        """a = world.desc_to_nodes(dialogue[0]['id'])
        print(a)
        b = world.get_prop(a[0], 'desc')
        print(b)
        exit()"""

        curr_conv["conv_info"]["room"]["setting"] = curr_conv["conv_info"]["room"][
            "description"
        ] = curr_conv["conv_info"]["room"]["background"] = location["description"]

        for dial in dialogue[1:]:
            curr_dial_act = copy.deepcopy(act_template)
            if dial["type"] == "choice":
                continue
            if dial["id"] == "human":
                curr_dial_act["id"] = human["id"]
                curr_dial_act["task_data"]["persona"] = human["persona"]
            else:
                curr_dial_act["id"] = bot["id"]
                curr_dial_act["task_data"]["persona"] = bot["persona"]

            curr_dial_act["text"] = dial["text"]  # str(dial['text'].decode('utf-8'))
            curr_dial_act["type"] = dial["type"]
            if dial["type"] == "action":
                curr_dial_act["task_data"]["action"] = curr_dial_act["text"]
                act_cands.add(curr_dial_act["text"])
                if curr_dial_act["text"] != "" and j in save_idx:
                    save_act_cands.add(curr_dial_act["text"])
            elif dial["type"] == "speech":
                speech_cands.add(curr_dial_act["text"])
                if j in save_idx:
                    save_speech_cands.add(curr_dial_act["text"])

            if "score" in dial.keys():
                curr_dial_act["score"] = int(dial["score"])
            curr_dial_act["task_data"]["setting"] = curr_dial_act["task_data"][
                "text_context"
            ] = curr_conv["conv_info"]["room"]["setting"]
            curr_dial_act["task_data"]["actions"] = actions

            # curr_dial_conv = copy.deepcopy(curr_conv)

            # curr_dial_conv['conv_info']['acts'].append(curr_dial_act)
            # all_quests.append(curr_dial_conv)
            curr_conv["conv_info"]["acts"].append(curr_dial_act)
        # all_quests[-1]['conv_info']['acts'][-1]['episode_done'] = True
        curr_conv["conv_info"]["acts"][-1]["episode_done"] = True

        """c = 0
        for ac in curr_conv['conv_info']['acts']:
            a = ac['task_data']['action']
            if a != '':
                c += 1

        if c <= 1:
            save_act_cands.remove(curr_conv['conv_info']['characters'][1][1]['goal'])
            continue"""

        all_quests.append(curr_conv)

    print(len(all_quests), float(act_len) / len(all_quests))
    if args["num_quests"] >= 10:
        splt = int(len(all_quests) * 0.1)
        all_quests_train = all_quests[: min(args["num_quests"], splt * 9)]
        # print(splt, min(args['num_quests'], splt * 4))
        all_quests_test = all_quests[splt * 9 : splt * 10]
        print(
            "Total quests, train quests, test quests",
            len(all_quests),
            len(all_quests_train),
            len(all_quests_test),
        )
        # exit()
        # all_quests_test = all_quests[500:]
    else:
        all_quests_train = all_quests_test = [
            all_quests[i] for i in range(args["num_quests"])
        ]

    path = os.path.join(
        LIGHT_DATAPATH,
        "quests/rl_quests_resources/",
        args["allfname"],
    )
    print(path)

    if not os.path.exists(path):
        os.makedirs(path)
    if args["run_num"] == "debug":
        speech_cands = list(speech_cands)[:1000]
    if args["eval_mode"] == "train":
        ofile = open(os.path.join(path, "formatted_hobbot_quests_train.pkl"), "wb")
        pickle.dump(all_quests_train, ofile)
        ofile.close()

        ofile = open(os.path.join(path, "formatted_hobbot_quests_test.pkl"), "wb")
        pickle.dump(all_quests_test, ofile)
        ofile.close()

        act_cands = list(act_cands)
        speech_cands = list(speech_cands)
        with open(os.path.join(path, "quest_all_cands.txt"), "w") as f:
            for a in act_cands + speech_cands:
                f.write(a + "\n")

        with open(os.path.join(path, "quest_act_cands.txt"), "w") as f:
            for a in act_cands:
                f.write(a + "\n")

        with open(os.path.join(path, "quest_speech_cands.txt"), "w") as f:
            for s in speech_cands:
                # print(s)
                f.write(s + "\n")

        with open(os.path.join(path, "env_all_cands.txt"), "w") as f:
            for s in speech_cands + list(reverse_act_cands):
                # print(s)
                f.write(s + "\n")
        with open(os.path.join(path, "env_act_cands.txt"), "w") as f:
            for s in list(reverse_act_cands):
                # print(s)
                f.write(s + "\n")
        if args["k_value"] == -1:
            args["k_value"] = len(save_act_cands)

        for cand in act_cands:
            if len(save_act_cands) >= args["k_value"]:
                break
            save_act_cands.add(cand)

        if len(save_act_cands) < args["k_value"]:
            args["k_value"] = len(save_act_cands)
        if args["k_value"] == -1:
            args["k_value"] = len(save_speech_cands)

        for cand in speech_cands:
            if len(save_speech_cands) >= args["k_value"]:
                break
            save_speech_cands.add(cand)

        with open(os.path.join(path, "quest_clip_act_cands.txt"), "w") as f:
            for a in list(save_act_cands)[: args["k_value"]]:
                f.write(a + "\n")

        with open(os.path.join(path, "quest_clip_speech_cands.txt"), "w") as f:
            for s in list(save_speech_cands)[: args["k_value"]]:
                # print(s)
                f.write(s + "\n")
    print(
        "Length candidates act and speech: ",
        len(act_cands) + len(reverse_act_cands),
        len(speech_cands),
    )
    ratio = (math.pow(float(len(act_cands)), avg_act_seq)) / (
        math.pow(float(len(speech_cands)), min(avg_speech_seq, 1))
    )
    print("Branching factor ratio: ", ratio)

    # write out build results
    with open(os.path.join(path, "meta.json"), "w+") as jsonf:
        json.dump([path, len(act_cands), len(speech_cands), ratio], jsonf)
    build_data.mark_done(path)

    return path, (len(act_cands), len(speech_cands)), ratio
