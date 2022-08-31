# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import numpy as np
import pickle
import random
import sys

from copy import copy
from light.modeling.agents.quests.rl.shared.process.conversation import Conversation
from light.modeling.agents.quests.rl.shared.process.constants import *
from light.modeling.agents.quests.rl.switch.environments.quest import QuestEnv


class EnvironmentGenerator(object):
    """
    Generates setting (+goal) instances.
    """

    def __init__(self, opt):
        self.writer = None
        self.index = 0
        self.id = 0
        self.opt = opt
        self.goal_types = opt["goal_types"].split(",")
        if opt.get("fixed_episodes_file"):
            self.episodes = self.load_pickle_file(opt["fixed_episodes_file"])
        elif opt["data_file"]:
            self.corpus = []
            self.load_pickle_file(opt["data_file"])

        self.precompute_instances()

        self.priorities = {i: 0 for i in range(len(self.corpus_total))}
        self.priorities_act = {i: 0 for i in range(len(self.corpus_total))}
        self.priorities_speech = {i: 0 for i in range(len(self.corpus_total))}

        # self.EMOTES = []
        # if 'emote' in self.goal_types:
        #     self.EMOTES = copy(ALL_EMOTES)

    def load_pickle_file(self, fname):
        """Just loads the file"""
        file = open(fname, "rb")
        db = pickle.load(file)
        self.corpus_total = db
        if self.opt["curriculum"] is not "none":
            return self.increase_pool(self.opt["curr_step_size"])
        self.corpus = db

    def increase_pool(self, increment):
        curr_pool_size = len(self.corpus)
        new_pool_size = min((curr_pool_size + increment), len(self.corpus_total))

        self.corpus = self.corpus_total[:new_pool_size]
        print("POOL INCREMENTED, NEW POOL SIZE:", new_pool_size)

        self.index = curr_pool_size

    def format_instance(
        self,
        qindex=0,
        goal="",
        # graph=None,
        partner_id=None,
        self_id=None,
        partner_setting="",
        self_setting="",
        score=0.0,
        label=None,
        internal_id=None,
        possible_acts=None,
        quest=None,
    ):
        instance = {}
        instance["qindex"] = qindex
        instance["goal"] = goal
        # instance['graph'] = graph
        instance["partner_id"] = partner_id
        instance["self_id"] = self_id
        instance["partner_setting"] = partner_setting
        instance["self_setting"] = self_setting
        instance["possible_acts"] = possible_acts
        instance["score"] = score
        instance["quest"] = quest
        if label is not None:
            instance["labels"] = label
        if internal_id is not None:
            instance["internal_id"] = internal_id
        return instance

    def precompute_instances(self):
        self.formatted_corpus_total = []
        for qidx, c in enumerate(self.corpus_total):
            data = c  # self.corpus[self.index]
            conv = Conversation(data, self.opt)
            partner_id0_dict, partner_id0_text = conv.convert_to_text(0)
            partner_id1_dict, partner_id1_text = conv.convert_to_text(1)

            partner_name = partner_id0_dict["partner_agent"]["name"]
            self_name = partner_id0_dict["self_agent"]["name"]
            score = partner_id0_dict["score"]
            partner_id = partner_id0_dict["partner_agent"][
                "id"
            ]  # conv.graph.desc_to_nodes(partner_name)[0]
            self_id = partner_id0_dict["self_agent"][
                "id"
            ]  # conv.graph.desc_to_nodes(self_name)[0]
            self_setting, partner_setting = partner_id0_text, partner_id1_text
            """conv.graph.get_possible_actions(
                partner_id, use_actions=USE_ACTIONS
            )"""
            is_done = False
            goal_dict = {"action_seq": [], "speech_seq": [], "score": 0}
            # print('----------')
            # print(partner_id0_dict["action"])
            for i in range(0, len(partner_id0_dict["action"]), 1):
                if is_done:
                    break
                possible_acts = partner_id0_dict["available_actions"][i]
                if "action" in self.goal_types:
                    act = partner_id0_dict["action"][i]
                    # print(act)
                    if act is "" or act is None:
                        if i % 2 == 1:
                            goal_dict["speech_seq"].append(
                                partner_id0_dict["speech"][i]
                            )
                        continue
                    else:
                        goal_dict["action"] = act
                        if act not in possible_acts:
                            possible_acts.append(act)
                        goal_dict["action_seq"].append(act)
                        if score[i] == 5:
                            is_done = True

                if "speech" in self.goal_types:
                    speech = partner_id0_dict["speech"][i]
                    if speech is None:
                        continue
                    goal_dict["speech"] = speech
                if len(goal_dict.items()) == 0:
                    continue
                # if len(goal_dict['action_seq']) < self.opt['quest_len']:
                #    continue
                goal_dict["score"] = score[i]
                if is_done:
                    instance = self.format_instance(
                        qindex=qidx,
                        goal=goal_dict,
                        # graph=conv.graph,
                        partner_id=partner_id,
                        self_id=self_id,
                        partner_setting=partner_setting,
                        self_setting=self_setting,
                        label=partner_id0_dict["speech"][i - 1],
                        possible_acts=possible_acts,
                        quest=QuestEnv(
                            self.goal_types,
                            self.opt["rewshape"],
                            goal_dict,
                            conv.graph,
                            possible_acts,
                            (self_id, self_name),
                            (partner_id, partner_name),
                        ),
                    )
                    self.formatted_corpus_total.append(instance)

    def priority_sample(self):
        if self.opt["priority"] == "true":
            # self.index = self.index % (len(self.corpus))
            priorities = np.array([b for a, b in self.priorities.items()])
            # sm = np.max(priorities) #min(100, priorities.sum())
            sm = np.linalg.norm(priorities)
            if sm is np.isnan(sm) or sm == 0:
                sm = 1
            priorities = (1 - (priorities / sm)) / len(self.priorities.keys())
            idx = random.choices(
                population=range(len(self.priorities.keys())), weights=priorities, k=1
            )[0] % (len(self.corpus))
            # print(idx)
            self.index = idx
            return idx

        else:
            self.index = self.index % (len(self.corpus))
            ret = self.index
            self.index += 1
            # print(self.index)
            if self.opt["eval_mode"] == "test" and self.index >= len(self.corpus_total):
                print("@@@@@@@@@@@@ FINAL @@@@@@@@@@@@")
                print("Q Index", self.index)
                print(
                    "Act and Speech completions: ",
                    sum([a for a in self.priorities.values()]) / self.index,
                )
                print(
                    "Act completions: ",
                    sum([a for a in self.priorities_act.values()]) / self.index,
                )
                print(
                    "Speech completions: ",
                    sum([a for a in self.priorities_speech.values()]) / self.index,
                )
                self.writer.add_scalars(
                    "test_data",
                    {
                        #'reward': np.mean(episode_rewards),
                        "act_goals": sum([a for a in self.priorities.values()])
                        / self.index,
                        "speech_goals": sum([a for a in self.priorities_act.values()])
                        / self.index,
                        #'episodes': total_episodes,
                        # 'dist_entropy': dist_entropy,
                        # 'value_loss': value_loss,
                        # 'action_loss': action_loss,
                        # 'values': values,
                        # 'advantage': advantages,
                        # 'abs_advantage': abs(advantages),
                    },
                    self.index,
                )
                sys.stdout.flush()
                self.writer.close()
                exit(0)
            return ret

    def from_original_dialogs(self, debug_mode=False):
        """
        Generates samples from actual train dialogs for RL train and
        debug mode checking
        """
        idx = self.priority_sample()
        ret = self.formatted_corpus_total[idx]
        return [ret]

        # list_of_envs = []
        """if self.index >= len(self.corpus):
            self.index = 0
            # if self.opt['shuffle_episodes']:
            #     np.random.shuffle(self.corpus)
            if debug_mode:
                print("SET INDEX BACK TO 0")
                return"""
        # self.index = random.randint(0, len(self.corpus) - 1)
        '''self.index = (self.index + 1) % (len(self.corpus) - 1)
        # print(self.index)
        data = self.corpus[self.index]
        conv = Conversation(data, self.opt)
        partner_id0_dict, partner_id0_text = conv.convert_to_text(0)
        partner_id1_dict, partner_id1_text = conv.convert_to_text(1)

        partner_name = partner_id0_dict['partner_agent']['name']
        self_name = partner_id0_dict['self_agent']['name']
        score = partner_id0_dict['score']
        partner_id = partner_id0_dict['partner_agent']['id']# conv.graph.desc_to_nodes(partner_name)[0]
        self_id = partner_id0_dict['self_agent']['id']# conv.graph.desc_to_nodes(self_name)[0]
        self_setting, partner_setting = partner_id0_text, partner_id1_text
        """conv.graph.get_possible_actions(
            partner_id, use_actions=USE_ACTIONS
        )"""
        is_done = False
        goal_dict = {'action_seq': [], 'speech_seq': [], 'score': 0}
        # print('----------')
        # print(partner_id0_dict["action"])
        for i in range(0, len(partner_id0_dict["action"]), 1):
            if is_done:
                break
            possible_acts = partner_id0_dict['available_actions'][i]
            if 'action' in self.goal_types:
                act = partner_id0_dict["action"][i]
                # print(act)
                if act is '' or act is None:
                    if i % 2 == 1:
                        goal_dict['speech_seq'].append(partner_id0_dict["speech"][i])
                    continue
                else:
                    goal_dict['action'] = act
                    if act not in possible_acts:
                        possible_acts.append(act)
                    goal_dict['action_seq'].append(act)
                    if score[i] == 5:
                        is_done = True

            if 'speech' in self.goal_types:
                speech = partner_id0_dict["speech"][i]
                if speech is None:
                    continue
                goal_dict['speech'] = speech
            if len(goal_dict.items()) == 0:
                continue
            #if len(goal_dict['action_seq']) < self.opt['quest_len']:
            #    continue
            goal_dict['score'] = score[i]
            if is_done:
                instance = self.format_instance(
                    index=self.index,
                    goal=goal_dict,
                    # graph=conv.graph,
                    partner_id=partner_id,
                    self_id=self_id,
                    partner_setting=partner_setting,
                    self_setting=self_setting,
                    label=partner_id0_dict["speech"][i - 1],
                    possible_acts=possible_acts,
                    quest=QuestEnv(self.goal_types, self.opt['rewshape'], goal_dict, conv.graph, possible_acts, (self_id, self_name), (partner_id, partner_name))
                )
                list_of_envs.append(instance)
                break
        # print(list_of_envs)
        # print(self_id, self_setting)
        # print(goal_dict)

        # self.index += 1

        return list_of_envs'''

    def from_original_dialogs_shuffled_all(self, debug_mode=False, shuffled=True):
        """"""
        list_of_envs = []
        convs = [Conversation(data, self.opt) for data in self.corpus]
        internal_id = 0
        for conv in convs:
            partner_id0_dict, partner_id0_text = conv.convert_to_text(0)
            partner_id1_dict, partner_id1_text = conv.convert_to_text(1)

            partner_name = partner_id0_dict["partner_agent"]["name"]
            self_name = partner_id0_dict["self_agent"]["name"]
            partner_id = conv.graph.desc_to_nodes(partner_name)[0]
            self_id = conv.graph.desc_to_nodes(self_name)[0]
            self_setting, partner_setting = partner_id0_text, partner_id1_text
            possible_acts = conv.graph.get_possible_actions(
                partner_id, use_actions=USE_ACTIONS
            )
            for i in range(2, len(partner_id0_dict["action"]), 2):
                goal_dict = {}
                if "action" in self.goal_types:
                    act = partner_id0_dict["action"][i]
                    if act is None:
                        continue
                    elif act in possible_acts:
                        goal_dict["action"] = act
                if "emote" in self.goal_types:
                    emote = partner_id0_dict["emote"][i]
                    if emote is None:
                        continue
                    goal_dict["emote"] = emote
                if "speech" in self.goal_types:
                    speech = partner_id0_dict["speech"][i]
                    if speech is None:
                        continue
                    goal_dict["speech"] = speech
                if len(goal_dict.items()) == 0:
                    continue
                instance = self.format_instance(
                    goal=goal_dict,
                    # graph=conv.graph,
                    partner_id=partner_id,
                    self_id=self_id,
                    partner_setting=partner_setting,
                    self_setting=self_setting,
                    label=partner_id0_dict["speech"][i - 1],
                    internal_id=internal_id,
                )
                internal_id += 1
                list_of_envs.append(instance)
            ## Considering the second persona to be Env
            """partner_name = partner_id1_dict['partner_agent']['name']
            self_name = partner_id1_dict['self_agent']['name']
            partner_id = conv.graph.desc_to_nodes(partner_name)[0]
            self_id = conv.graph.desc_to_nodes(self_name)[0]
            self_setting, partner_setting = partner_id1_text, partner_id0_text
            possible_acts = conv.graph.get_possible_actions(
                partner_id, use_actions=USE_ACTIONS
            )
            for i in range(1, len(partner_id1_dict["action"]), 2):
                goal_dict = {}
                if 'action' in self.goal_types:
                    act = partner_id0_dict["action"][i]
                    if act is None:
                        continue
                    elif act in possible_acts:
                        goal_dict['action'] = act
                if 'emote' in self.goal_types:
                    emote = partner_id0_dict["emote"][i]
                    if emote is None:
                        continue
                    goal_dict['emote'] = emote
                if 'speech' in self.goal_types:
                    speech = partner_id0_dict["speech"][i]
                    if speech is None:
                        continue
                    goal_dict['speech'] = speech
                if len(goal_dict.items()) == 0:
                    continue
                instance = self.format_instance(
                    goal=goal_dict,
                    graph=conv.graph,
                    partner_id=partner_id,
                    self_id=self_id,
                    partner_setting=partner_setting,
                    self_setting=self_setting,
                    label=partner_id0_dict["speech"][i - 1],
                    internal_id=internal_id,
                )
                internal_id += 1
                list_of_envs.append(instance)"""
        if shuffled:
            np.random.shuffle(list_of_envs)
        return list_of_envs

    def from_all_possible_goals(self, shuffled=True):
        """"""
        list_of_envs = []
        convs = [Conversation(data, self.opt) for data in self.corpus]
        internal_id = 0
        for conv in convs:
            partner_id0_dict, partner_id0_text = conv.convert_to_text(0)
            partner_id1_dict, partner_id1_text = conv.convert_to_text(1)

            partner_name = partner_id0_dict["partner_agent"]["name"]
            self_name = partner_id0_dict["self_agent"]["name"]
            partner_id = conv.graph.desc_to_nodes(partner_name)[0]
            self_id = conv.graph.desc_to_nodes(self_name)[0]
            self_setting, partner_setting = partner_id0_text, partner_id1_text
            possible_acts = conv.graph.get_possible_actions(
                partner_id, use_actions=USE_ACTIONS
            )
            if "action" in self.goal_types:
                for act in possible_acts:
                    goal_dict = {}
                    goal_dict["action"] = act
                    instance = self.format_instance(
                        goal=goal_dict,
                        graph=conv.graph,
                        partner_id=partner_id,
                        self_id=self_id,
                        partner_setting=partner_setting,
                        self_setting=self_setting,
                        # label=partner_id0_dict["speech"][i - 1],
                        internal_id=internal_id,
                    )
                    internal_id += 1
                    list_of_envs.append(instance)
            if "emote" in self.goal_types:
                for emote in ALL_EMOTES:
                    goal_dict = {}
                    goal_dict["emote"] = emote
                    instance = self.format_instance(
                        goal=goal_dict,
                        graph=conv.graph,
                        partner_id=partner_id,
                        self_id=self_id,
                        partner_setting=partner_setting,
                        self_setting=self_setting,
                        # label=partner_id0_dict["speech"][i - 1],
                        internal_id=internal_id,
                    )
                    internal_id += 1
                    list_of_envs.append(instance)

            ## Considering the second persona to be Env
            """partner_name = partner_id1_dict['partner_agent']['name']
            self_name = partner_id1_dict['self_agent']['name']
            partner_id = conv.graph.desc_to_nodes(partner_name)[0]
            self_id = conv.graph.desc_to_nodes(self_name)[0]
            self_setting, partner_setting = partner_id1_text, partner_id0_text
            possible_acts = conv.graph.get_possible_actions(
                partner_id, use_actions=USE_ACTIONS
            )
        if 'action' in self.goal_types:
            for act in possible_acts:
                goal_dict = {}
                goal_dict['action'] = act
                instance = self.format_instance(
                    goal=goal_dict,
                    graph=conv.graph,
                    partner_id=partner_id,
                    self_id=self_id,
                    partner_setting=partner_setting,
                    self_setting=self_setting,
                    # label=partner_id0_dict["speech"][i - 1],
                    internal_id=internal_id,
                )
                internal_id += 1
                list_of_envs.append(instance)
        if 'emote' in self.goal_types:
            for emote in ALL_EMOTES:
                goal_dict = {}
                goal_dict['emote'] = emote
                instance = self.format_instance(
                    goal=goal_dict,
                    graph=conv.graph,
                    partner_id=partner_id,
                    self_id=self_id,
                    partner_setting=partner_setting,
                    self_setting=self_setting,
                    # label=partner_id0_dict["speech"][i - 1],
                    internal_id=internal_id,
                )
                internal_id += 1
                list_of_envs.append(instance)"""
        if shuffled:
            np.random.shuffle(list_of_envs)
        return list_of_envs

    def from_fixed_episodes_file(self):
        eps = copy(self.episodes)
        if self.opt["shuffle_episodes"] and self.opt["combo"] != "fixed_episodes_test":
            print("SHUFFLED")
            np.random.shuffle(eps)
        return eps
