#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import json
from glob import glob


class QuestEnv(object):
    def __init__(self, goal_types, rewshape, data):
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
        # self.possible_actions = data['available_actions']

    def reset(self):
        self.done = False
        self.act_progress = 0
        self.speech_progress = 0
        self.score = 0
        self.real_score = 0

    def act(self, action):
        # TODO add rews if it does stuff that's grounded
        # print(action)
        quest_action_gold = self.act_quest[self.act_progress]
        if action == quest_action_gold:
            self.act_progress += 1
            if self.act_progress == len(self.act_quest):
                # print('GOALLLL', )
                reward = 5
            else:
                reward = self.rewshape
        else:
            reward = 0
        self.score += reward
        if reward == 5:
            self.real_score = 1

        if self.act_progress >= len(self.act_quest):
            self.done = True

        return reward, self.done


if __name__ == "__main__":
    data = []
    for fname in glob("/checkpoint/light/data/quests/raw" + "/*"):
        with open(fname, "r") as f:
            data.append(json.load(f))
    print(data[0].keys())
    env = QuestEnv(data[0]["data"])
