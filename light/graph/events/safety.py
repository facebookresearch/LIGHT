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

try:
    from parlai_internal.agents.safety_wrapper.multiturn_safety import (
        MultiturnOffensiveLanguageClassifier,
    )
except:

    class MultiturnOffensiveLanguageClassifier:
        # Temporary until using public safety
        pass


class AdversarialOffensiveLanguageClassifier(MultiturnOffensiveLanguageClassifier):
    """
    Load model trained to detect offensive language in the context of multi- turn
    dialogue utterances.
    This model was trained to be robust to adversarial examples created by humans. See
    <http://parl.ai/projects/dialogue_safety/> for more information.
    """

    def __init__(self, model_pool: "ModelPool"):
        self.__model_pool = model_pool
        super().__init__()

    def _create_safety_model(self):
        return self.__model_pool.get_model("safety")


class SafetyClassifier:
    print("Initializing safety classifier")

    def __init__(self, datapath: Optional[str], model_pool: "ModelPool"):
        if datapath is not None and datapath != "":
            self.string_matcher = OffensiveStringMatcher(datapath)
        else:
            self.string_matcher = None
        if model_pool.has_model("safety"):
            self.classifier = AdversarialOffensiveLanguageClassifier(model_pool)
        else:
            self.classifier = None

    def is_safe(self, text: str):
        if self.string_matcher is not None:
            if text in self.string_matcher:
                return False
        if self.classifier is not None:
            if text in self.classifier:
                return False
        return True
