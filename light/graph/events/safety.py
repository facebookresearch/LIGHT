#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai.utils.safety import OffensiveStringMatcher
from parlai.agents.transformer.transformer import TransformerClassifierAgent
from parlai.utils.typing import TShared

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from light.registry.model_pool import ModelPool


class SafetyClassifier:
    def __init__(self, datapath: Optional[str], model_pool: "ModelPool"):
        if datapath is not None and datapath != "":
            self.string_matcher = OffensiveStringMatcher(datapath)
        else:
            self.string_matcher = None
        if model_pool.has_model("safety"):
            self.classifier = model_pool.get_model("safety")
        else:
            self.classifier = None

    async def contains_offensive_language(self, text):
        """
        Returns the probability that a message is safe according to the classifier.
        """
        act = {"text": text, "episode_done": True}
        self.classifier.observe(act)
        response_act = await self.classifier.act()
        response = response_act["text"]
        pred_class, prob = [x.split(": ")[-1] for x in response.split("\n")]
        pred_not_ok = self.classes[pred_class]  # check whether classified as NOT OK
        prob = float(prob)  # cast string to float
        return pred_not_ok, prob

    async def is_safe(self, text: str):
        if self.string_matcher is not None:
            if text in self.string_matcher:
                return False
        if self.classifier is not None:
            not_ok, _prob = await self.contains_offensive_language(text)
            return not_ok
        return True
