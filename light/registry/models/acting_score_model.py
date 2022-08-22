#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import asyncio
from dataclasses import dataclass, field
from parlai.core.agents import Agent
from parlai.core.message import Message

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

        def new_observe(model, message: Message):
            model._last_observe = message
            old_observe(message)

        model.observe = new_observe
        model._last_observe = Message({})

        def new_act(model):
            if model._last_observe.get("label_candidates"):
                # Evalling just one cand
                model.roleplaying_score_model.opt["label_candidates"] = "inline"
                model.roleplaying_score_model.label_candidates = "inline"
                act = model.act()
                scores = model.scores
                act["scores"] = model.scores
            else:
                # Evalling against the base candidates
                model.roleplaying_score_model.opt["eval_candidates"] = "fixed"
                model.roleplaying_score_model.eval_candidates = "fixed"
                act = model.act()
                scores = [model.scores[i] for i in SCORE_INDS]
                act["scores"] = scores

        return model
