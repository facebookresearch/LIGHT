#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import pickle
from glob import glob
import json
from light.graph.structured_graph import OOGraph
from light.world.world import World
import copy

import os


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
    "",
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

# with open('/private/home/rajammanabrolu/ParlAI/data/light_quests/hobbot/filtered_light_cands.txt', 'r') as f:
#    for line in f:
#        speech_cands.add(str(line))


def preprocess(args):
    def sequence(dialogue):
        c = 0
        for dial in dialogue[1:]:

            if dial["type"] == "action" and dial["text"] != "":
                c += 1

            if dial["id"] == "human":
                if dial["score"] == 5:
                    break

        if c <= args["quest_len"] - 1:
            return False

        return True

    all_quests = []
    speech_cands = set()

    quests_original_raw = []

    for fname in glob(
        "/private/home/rajammanabrolu/ParlAI/data/light_quests" + "/raw/*.json"
    ):
        with open(fname, "r") as f:
            quests_original_raw.append(json.load(f)["data"])

    hobbot_raw = json.loads(
        open(
            "/private/home/rajammanabrolu/ParlAI/data/light_quests/hobbot/raw/perfect1.json",
            "r",
        ).read()
    )

    act_cands = set()

    # hobbot_raw = hobbot_raw[0:8]
    save_idx = range(args["num_quests"])
    save_act_cands = set()
    save_speech_cands = set()

    hobbot_raw_filtered = []

    for rawuf in hobbot_raw:
        if int(rawuf["score"]) < 10:
            continue
        dialogue = rawuf["dialogue"]
        if not sequence(dialogue):
            continue
        hobbot_raw_filtered.append(rawuf)

    for j, raw in enumerate(hobbot_raw_filtered):
        dialogue = raw["dialogue"]
        human = raw["human_persona"]
        bot = raw["bot_persona"]
        location = raw["location"]
        quest_file = json.load(
            open(
                "/private/home/rajammanabrolu/ParlAI/data/light_quests/raw/"
                + location["quest_file"]
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

        act_cands.update(actions)
        # if j in save_idx:
        #    save_act_cands.update(actions)

        for char in [bot, human]:
            cur_char = copy.deepcopy(char_template)
            cur_char[0] = char["name"]
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

    if args["num_quests"] >= 5:
        splt = int(args["num_quests"] * 0.2)
        all_quests_train = all_quests[: splt * 4]
        all_quests_test = all_quests[splt * 4 : splt * 5]
    else:
        all_quests_train = all_quests_test = [all_quests[i] for i in save_idx]

    path = os.path.join(
        "/private/home/rajammanabrolu/ParlAI/data/light_quests/hobbot/",
        args["allfname"],
    )

    if not os.path.exists(path):
        os.makedirs(path)
    ofile = open(os.path.join(path, "formatted_hobbot_quests_train.pkl"), "wb")
    pickle.dump(all_quests_train, ofile)
    ofile.close()

    ofile = open(os.path.join(path, "formatted_hobbot_quests_test.pkl"), "wb")
    pickle.dump(all_quests_test, ofile)
    ofile.close()

    # ofile = open('/private/home/rajammanabrolu/ParlAI/data/light_quests/hobbot/supervised/formatted_hobbot_quests.pkl', 'wb')
    # pickle.dump(all_quests, ofile)
    # ofile.close()

    with open(os.path.join(path, "quest_act_cands.txt"), "w") as f:
        for a in act_cands:
            f.write(a + "\n")

    speech_cands = list(speech_cands)[:1000]

    with open(os.path.join(path, "quest_speech_cands.txt"), "w") as f:
        for s in speech_cands:
            # print(s)
            f.write(s + "\n")

    if args["k_value"] == -1:
        args["k_value"] = len(save_act_cands)

    for cand in act_cands:
        if len(save_act_cands) >= args["k_value"]:
            break
        save_act_cands.add(cand)

    for cand in speech_cands:
        if len(save_speech_cands) >= args["k_value"]:
            break
        save_speech_cands.add(cand)

    if len(save_act_cands) < args["k_value"]:
        args["k_value"] = len(save_act_cands)

    with open(os.path.join(path, "quest_clip_act_cands.txt"), "w") as f:
        for a in list(save_act_cands)[: args["k_value"]]:
            f.write(a + "\n")

    with open(os.path.join(path, "quest_clip_speech_cands.txt"), "w") as f:
        for s in list(save_speech_cands)[: args["k_value"]]:
            # print(s)
            f.write(s + "\n")

    return path, len(act_cands)
