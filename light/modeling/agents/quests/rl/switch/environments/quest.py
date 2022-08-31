#!/usr/bin/env python3


import json
from glob import glob
from copy import deepcopy, copy
from light.world.world import World, WorldConfig
from light.graph.structured_graph import OOGraph


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


def reverse_task(act_goal, self_name, partner_name):
    reverse_act_goal = ""

    if "drop" in act_goal or "put" in act_goal:
        reverse_act_goal = act_goal
    elif "get" in act_goal:
        arg = act_goal.replace("get", "").strip()
        reverse_act_goal = "give " + arg + " to " + self_name
    elif "steal" in act_goal:
        arg = act_goal.replace("steal", "").split("from")[0].strip()
        reverse_act_goal = "give " + arg + " to " + self_name
    elif "hug" in act_goal:
        reverse_act_goal = "hug " + partner_name

    return reverse_act_goal


class QuestEnv(object):
    def __init__(
        self, goal_types, rewshape, data, graph, possible_acts, selfs, partners
    ):
        # differentiate between quest actions and utterances and keep track of seq progression for both
        # subclass directly from Teacher
        """self.short_motivation = data['short_motivation']
        self.mid_motivation = data['mid_motivation']
        self.long_motivation = data['long_motivation']
        self.goal = data['goal']
        self.graph = OOGraph.from_json(data['graph'])
        self.character = data['character']
        self.persona = data['persona']
        self.description = data['description']"""

        self.act_quest = data["action_seq"]
        self.act_goal = self.act_quest[-1]
        self.rewshape = rewshape

        self.speech_quest = data["speech_seq"]
        self.graph_data = deepcopy(graph)
        self.possible_acts_data = deepcopy(possible_acts)
        # self.possible_actions = data['available_actions']
        self.possible_says = []
        self.self_id, self.self_name = selfs
        self.partner_id, self.partner_name = partners

        self.reverse_act_goal = reverse_task(
            self.act_goal, self.self_name, self.partner_name
        )

    def reset(self):
        self.done = False
        self.act_done = False
        self.speech_done = False
        self.act_progress = 0
        self.speech_progress = 0
        self.score = 0
        self.real_speech_score = 0
        self.real_act_score = 0
        # self.world = World(WorldConfig())
        # g = OOGraph.from_json(deepcopy(self.graph_data))
        # self.world.oo_graph = g
        self.world = deepcopy(self.graph_data)
        self.possible_acts = self.possible_acts_data

    def check_reverse_act_progress(self, action, id=None):
        done = False
        reward = 0
        try:
            executed, _ = self.world.parse_exec(id, action)
        except:
            executed = False
            id_chk = id + "__dead__"
            if id_chk in self.world.oo_graph.dead_nodes.keys():
                done = True

        if not executed:
            return reward, done

        if action == self.reverse_act_goal:  # and self.real_act_score == 0:
            # print('REGOALLLL', action)
            reward = 5
            done = True

        return reward, done

    def check_act_progress(self, action, id=None):
        done = False
        reward = 0
        try:
            executed, _ = self.world.parse_exec(id, action)
        except:
            executed = False
            id_chk = id + "__dead__"
            print("failure")
            if id_chk in self.world.oo_graph.dead_nodes.keys():
                print("dead")
                done = True

        if not executed:
            return reward, done

        self.possible_acts = self.world.get_possible_actions(id, USE_ACTIONS)

        """quest_action_gold = self.act_quest[self.act_progress]
        if action == quest_action_gold:
            self.act_progress += 1
            if self.act_progress == len(self.act_quest):
                #print('GOALLLL', action)
                reward = 5
            else:
                reward = self.rewshape
        else:
            reward = 0

        if self.act_progress >= len(self.act_quest):
            done = True"""

        if action == self.act_goal:  # and self.real_act_score == 0:
            # print('GOALLLL', action)
            reward = 5
            done = True

        return reward, done

    def check_speech_progress(self, action, id=None, mode="train"):
        if self.real_speech_score == 1:
            return 0, True
        done = False
        reward = 0
        if mode == "train":
            quest_speech_gold = self.speech_quest[self.speech_progress]
            if action == quest_speech_gold:
                # if action in self.speech_quest:
                self.speech_progress += 1
                if self.speech_progress == len(self.speech_quest):
                    # print('SPEECH GOALLLL', action)
                    reward = 5
                else:
                    reward = self.rewshape
            else:
                reward = 0

            if self.speech_progress >= len(self.speech_quest):
                done = True
        elif mode == "test":
            if action in self.speech_quest:
                reward = 5
                done = True

        return reward, done

    def act(self, action, id=None, mode="train"):
        # print(action)
        # reward, done = 0, False

        act_rew, act_done = self.check_act_progress(action, id)
        speech_rew, speech_done = self.check_speech_progress(action, id, mode)

        reward = act_rew + speech_rew
        self.act_done = act_done
        self.speech_done = speech_done
        # TODO figure this out for the env and rl act/say combos
        self.done = act_done and speech_done
        # self.done = speech_done
        # print(act_done, speech_done)

        self.score += reward
        if act_done:
            self.real_act_score = 1

        if speech_done:
            self.real_speech_score = 1

        return reward, self.done

    def reverse_act(self, action, id=0):
        reward, done = self.check_reverse_act_progress(action, id)
        self.act_done = done
        self.score += reward
        self.done = done  # and (self.real_speech_score == 1)
        if done:
            self.real_act_score = 1

        return reward, self.done
