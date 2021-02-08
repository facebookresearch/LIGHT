#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai.utils.safety import OffensiveStringMatcher
from parlai.core.agents import create_agent
from parlai.core.params import ParlaiParser
from parlai.agents.transformer.transformer import TransformerClassifierAgent
from parlai_internal.agents.safety_wrapper.multiturn_safety import (
    MultiturnOffensiveLanguageClassifier,
)


class AdversarialOffensiveLanguageClassifier(MultiturnOffensiveLanguageClassifier):
    """
    Load model trained to detect offensive language in the context of multi- turn
    dialogue utterances.
    This model was trained to be robust to adversarial examples created by humans. See
    <http://parl.ai/projects/dialogue_safety/> for more information.
    """

    def _create_safety_model(self):
        parser = ParlaiParser(False, False)
        TransformerClassifierAgent.add_cmdline_args(parser)
        parser.set_params(
            model_file="zoo:bot_adversarial_dialogue/multi_turn/model",
            print_scores=True,
            split_lines=True,
            model_parallel=False,
            threshold=0.999,
            bs=1,
        )
        safety_opt = parser.parse_args([])
        return create_agent(safety_opt, requireModelExists=True)


class SafetyClassifier:
    def __init__(self, datapath, use_model=False):
        if datapath != "":
            self.string_matcher = OffensiveStringMatcher(datapath)
        else:
            self.string_matcher = None
        if use_model:
            self.classifier = AdversarialOffensiveLanguageClassifier()
        else:
            self.classifier = None

    def is_safe(self, text):
        if self.string_matcher is not None:
            if text in self.string_matcher:
                print("broke matcher")
                return False
        if self.classifier is not None:
            print(text)
            if text in self.classifier:
                print("broke classifier")
                return False
        return True
