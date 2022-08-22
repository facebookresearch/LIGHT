#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from dataclasses import dataclass, field
from parlai.core.agents import Agent

from light.registry.parlai_model import ParlAIModelConfig, ParlAIModelLoader


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
        return model
