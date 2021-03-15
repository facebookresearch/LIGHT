#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig

from parlai.core.params import ParlaiParser
from parlai.core.agents import create_agent, create_agent_from_shared
from parlai.core.opt import Opt
from copy import deepcopy
import os

from typing import List, Any, Dict, Optional
from parlai.core.agents import Agent


@dataclass
class ParlAIModelConfig:
    # As of now, ParlAI is the only model loader.
    # Eventually this could be split into more classes
    # as we incorporate other models.
    _loader: str = "ParlAI"
    model_file: str = field(
        default=MISSING, metadata={"help": ("Path to the model file for this model.")}
    )
    opt_file: str = field(
        default=MISSING,
        metadata={"help": ("Path to the ParlAI opt file for this model.")},
    )
    overrides: Dict[str, Any] = field(
        default_factory=dict,
        metadata={"help": ("Additional overrides for this model's opt")},
    )


class ParlAIModelLoader:
    """
    Takes in the configuration for a ParlAI model, and provides options
    for being able to load that model one or multiple times (via sharing).
    """

    def __init__(self, config: DictConfig):
        self._shared = None
        self.config = config
        self.load_model(config)

    def load_model(self, config: DictConfig) -> None:
        """Initialize the model from the given config"""
        opt_from_config = config.get("opt_file", None)
        model_from_config = config.get("model_file", None)
        overrides = dict(config.get("overrides", {}))

        if opt_from_config is None and model_from_config is None:
            raise AssertionError(f"Must provide one of opt_file or model_file")

        if opt_from_config is None:
            parser = ParlaiParser(True, True, "")
            opt = parser.parse_args(args=[])
        else:
            opt_file = os.path.expanduser()
            opt = Opt.load(os.path.expanduser(opt_file))

        if model_from_config is not None:
            model_file = os.path.expanduser(config.opt_file)
            if not os.path.exists(model_file):
                raise AssertionError(
                    f"Provided model file `{model_file}` does not exist."
                )
            opt["model_file"] = model_file

        opt.update(overrides)
        model = create_agent(opt)
        self._shared = model.share()

    def before_return_model(self, model):
        """Do any post-initialization we need for this model"""
        return model

    def get_model(self, overrides: Optional[Dict[str, Any]] = None) -> Agent:
        """Get a copy of the model"""
        use_shared = self._shared
        if use_shared is not None:
            opt = deepcopy(use_shared["opt"])
            opt.update(overrides)
            use_shared["opt"] = opt
        model = create_agent_from_shared(use_shared)
        return self.before_return_model(model)
