#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from light.modeling.agents.quests.rl.shared.process.constants import *

from light.modeling.agents.quests.rl.shared.environments.history import (
    GoalOrientedHistory,
)
from light.modeling.agents.quests.rl.base.models.transformer import LightBiencoderAgent


class LightRetrievalAgent(LightBiencoderAgent):
    """
    Environment agent that both utters and acts/emotes. Initialized with
    fixed candidates but you can pass in candidates at inference time
    (for acts/emotes) and it will use those instead
    """

    def build_dictionary(self):
        """
        Return the constructed dictionary, which will be set to self.dict.

        If you need to add additional tokens to the dictionary, this is likely
        the right place to do it.
        """
        # Tokens shouldn't be added
        d = self.dictionary_class()(self.opt)
        return d

    @classmethod
    def history_class(cls):
        return GoalOrientedHistory

    def build_history(self):
        """
        Return the constructed history object.
        Use this to define your own P1/P2 tokens
        """
        return self.history_class()(
            self.opt,
            self.text_truncate,
            self.histsz,
            "_partner_say",
            "_self_say",
            self.dict,
            MISSING_SAY_TAG,
        )

    def set_p2_tok(self, p2_tok):
        self.history.p2_token = p2_tok

    def block_repeats(self, cand_preds, batch):
        """Heuristic to block a model repeating a line from the history.
        Edited from TRA's block repeats
        """
        if batch is None:
            return super().block_repeats(cand_preds)
        new_preds = []
        for cp, obs in zip(cand_preds, batch["observations"]):
            raw_history_strings = obs["full_text"].split("\n")
            history_strings = []
            for hs in raw_history_strings:
                sparts = hs.split(" ", 1)
                if len(sparts) > 0 and sparts[0] in ["_self_say", "_partner_say"]:
                    history_strings.append(sparts[1])
            np = []
            for c in cp:
                if c not in history_strings:
                    np.append(c)
            new_preds.append(np)
        return new_preds

    def self_observe(self, self_message, p2_tok=None):
        if p2_tok:
            self.history.p2_token = p2_tok
        return super().self_observe()


# TODO Add generator agent w/ env wrapper here
