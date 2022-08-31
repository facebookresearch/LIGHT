#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import json
from glob import glob
from light.graph.structured_graph import OOGraph


class QuestEnv(object):
    def __init__(self, data):
        self.quest = data["timeline"]
        # differentiate between quest actions and utterances and keep track of seq progression for both
        # subclass directly from Teacher
        self.short_motivation = data["short_motivation"]
        self.mid_motivation = data["mid_motivation"]
        self.long_motivation = data["long_motivation"]
        self.goal = data["goal"]
        self.graph = OOGraph.from_json(data["graph"])
        self.character = data["character"]
        self.persona = data["persona"]
        self.description = data["description"]
        print(self.quest)
        self.reset()

    def reset(self):
        self.done = False
        self.quest_completion = 0
        self.reward = 0
        self.score = 0

    def act(self, action):
        # TODO add rews if it does stuff that's grounded
        quest_action_gold = self.quest[self.quest_completion]["action"]
        if action == quest_action_gold:
            self.quest_completion += 1
            self.reward = 1
            self.score += self.reward

        if self.quest_completion == len(self.quest):
            self.reset()


if __name__ == "__main__":
    from light.constants import LIGHT_DATAPATH

    data = []
    for fname in glob(os.path.join(LIGHT_DATAPATH, "quests/stems/batch_1/*.json")):
        with open(fname, "r") as f:
            data.append(json.load(f))
    print(data[0].keys())
    env = QuestEnv(data[0]["data"])
