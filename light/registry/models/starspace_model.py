#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from dataclasses import dataclass, field
from parlai.core.agents import Agent, create_agent_from_shared  # type: ignore
import os
from copy import deepcopy

from typing import Optional, Dict, Any

from light.registry.parlai_model import ParlAIModelConfig, ParlAIModelLoader


@dataclass
class MapStarspaceModelConfig(ParlAIModelConfig):
    _loader: str = "MapStarspaceLoader"
    resource_path: str = field(
        default=os.path.expanduser("~/ParlAI/data/light_maps/"),
        metadata={"help": ("Path to the LIGHT maps data")},
    )


class MapStarspaceModelLoader(ParlAIModelLoader):
    """
    Takes in the configuration for a ParlAI model, and provides options
    for being able to load that model one or multiple times (via sharing).

    We do some special post-setup on the acting score model. Ideally this
    could be done as a special opt in the agent itself, but for now it's here.
    """

    CONFIG_CLASS = MapStarspaceModelConfig

    def get_model(self, overrides: Optional[Dict[str, Any]] = None) -> Agent:
        """Get a copy of the model"""
        use_shared = self._shared
        if use_shared is not None:
            opt = deepcopy(use_shared["opt"])
            opt.update(overrides)
            use_shared["opt"] = opt
        else:
            opt = {}
            if overrides is not None:
                opt.update(overrides)

        if opt["target_type"] == "room":
            opt["fixed_candidates_file"] = os.path.join(
                self.config.resource_path, "room_full_cands.txt"
            )
        elif opt["target_type"] in ["agent", "character"]:
            opt["fixed_candidates_file"] = os.path.join(
                self.config.resource_path, "character_full_cands.txt"
            )
        elif opt["target_type"] == "object":
            opt["fixed_candidates_file"] = os.path.join(
                self.config.resource_path, "object_full_cands.txt"
            )
        else:
            raise NotImplementedError(
                f"Given starspace target type {opt['target_type']} not implemented"
            )

        print(self.config.resource_path, opt["fixed_candidates_file"])
        opt["override"]["fixed_candidates_file"] = opt["fixed_candidates_file"]
        model = create_agent_from_shared(use_shared)
        return self.before_return_model(model)
