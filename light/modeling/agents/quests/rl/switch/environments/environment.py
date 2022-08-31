# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3


import copy
import torch


class Environment(object):
    def __init__(self, opt):
        self.steps = 0
        self.self_setting = None
        self.partner_setting = None
        # self.graph = None
        self.index = 0
        self.goal = None
        self.partner_id = None
        self.self_id = None
        self.labels = None
        self.rl_say_mappings = None
        self.rl_act_mappings = None
        self.internal_id = None
        self.possible_acts = None
        self.quest = None

    def set_attrs(self, instance):
        self.steps = 0
        self.qindex = copy.copy(instance["qindex"])
        self.self_setting = copy.copy(instance["self_setting"])
        self.partner_setting = copy.copy(instance["partner_setting"])
        # self.graph = copy.deepcopy(instance['graph'])
        self.goal = instance["goal"]
        self.partner_id = copy.copy(instance["partner_id"])
        self.self_id = copy.copy(instance["self_id"])
        self.possible_acts = copy.copy(instance["possible_acts"])
        self.quest = copy.copy(instance["quest"])
        if instance.get("embeddings", None) is not None:
            self.embeddings = torch.FloatTensor(instance["embeddings"])
        if instance.get("internal_id", None) is not None:
            self.internal_id = instance["internal_id"]
        if instance.get("labels", None):
            self.labels = instance["labels"]
        if instance.get("cluster_label", None):
            self.cluster_label = instance["cluster_label"][0]
        if instance.get("output_label", None):
            self.output_label = instance["output_label"][0]
