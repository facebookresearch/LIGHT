#!/usr/bin/env python3


# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import asyncio
from dataclasses import dataclass, field
from parlai.core.agents import Agent
from parlai.core.message import Message
import types

from light.registry.parlai_model import ParlAIModelConfig, ParlAIModelLoader

SCORE_INDS = [1000, 2000, 5000, 10000]


@dataclass
class ParlAIPolyencoderActingScoreModelConfig(ParlAIModelConfig):
    _loader: str = "ParlAIActingScore"


class ParlAIPolyencoderActingScoreModelLoader(ParlAIModelLoader):
    """
    Takes in the configuration for a ParlAI model, and provides options
    for being able to load that model one or multiple times (via sharing).

    We do some special post-setup on the acting score model. Ideally this
    could be done as a special opt in the agent itself, but for now it's here.
    """

    def before_return_model(self, model) -> Agent:
        """Clear boring and setup for being an acting score model"""
        model.boring = None
        # mark this agent as the special RP score agent
        model.actingscore = True
        # override eval step here
        model.eval_step = model.eval_step_scoresonly

        # Override act and observe so that we can catch from remote calls
        # as well
        old_act = model.act
        old_observe = model.observe

        def new_observe(model_self, message: Message):
            model_self._last_observe = message
            old_observe(message)

        model.observe = types.MethodType(new_observe, model)
        model._last_observe = Message({})

        old_act = model.act

        def new_act(model_self):
            if model_self._last_observe.get("label_candidates"):
                # Evalling just one cand
                model_self.opt["candidates"] = "inline"
                model_self.candidates = "inline"
                model_self.opt["eval_candidates"] = "inline"
                model_self.eval_candidates = "inline"
                model_self.reset()
                old_observe(model_self._last_observe)  # re-observe to vectorize
                act = old_act()
                scores = model_self.scores
                act["scores"] = scores[0].tolist()
            else:
                # Evalling against the base candidates
                model_self.opt["candidates"] = "fixed"
                model_self.candidates = "fixed"
                model_self.opt["eval_candidates"] = "fixed"
                model_self.eval_candidates = "fixed"
                # model_self.reset()
                act = old_act()
                list_scores = sorted(model_self.scores[0].tolist())
                list_scores.reverse()
                scores = [list_scores[i] for i in SCORE_INDS]
                act["scores"] = scores
            return act

        model.act = types.MethodType(new_act, model)

        return model
