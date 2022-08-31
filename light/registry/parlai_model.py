#!/usr/bin/env python3


# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
By design changing options can happen in a few places with the
following priority order:

1. Options provided by a specific `ModelPool.get_model` call.
2. Options provided on the command line via `+<model>.overrides.<target>=value`
3. Options provided in the overrides of a particular hydra config yaml file
4. Options specified in the provided (hydra) `<model>.opt_file`
   (either from the yaml, or provided on the command line)
5. Options specified in the `<model_path>.opt file`

Hydra configures the process of making #2 override #3, but the rest
flow due to the semantics of ParlAI and the ParlAIModelLoader implementation here.
"""

from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig

from parlai.core.agents import Agent, create_agent, create_agent_from_shared
from parlai.core.message import Message
from parlai.core.opt import Opt
from parlai.core.params import ParlaiParser
from copy import deepcopy
import os
import asyncio

from typing import List, Any, Dict, Optional


CONTEXT_FILL_COUNT = 200
INIT_CONTEXT = """
_setting_name weathered shack, Abandoned
_setting_desc A weathered shack with a roof made of old broken tiles sits in the middle of the forest. The wood is starting to split and the shack appears as if it will crumble at any moment.
_partner_name animal
_self_name man
_self_persona I am a strong man. I work in the fields and pastures all day. I take of my master's sheep. One day I hope to have my own sheep.
I am very strong
"""


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

    def get(self, attr: str, default_val: Optional[Any] = None):
        """Wrapper to ensure interoperability with hydra DictConfig"""
        val = self.__dict__.get(attr, default_val)
        if val == MISSING:
            val = None
        return val


class ParlAIModelLoader:
    """
    Takes in the configuration for a ParlAI model, and provides options
    for being able to load that model one or multiple times (via sharing).
    """

    def __init__(self, config: DictConfig):
        self._shared = None
        self.config = config

    async def force_load(self) -> None:
        """
        Force the model loader to initialize and query
        the model (to warm up)
        """
        await self.load_model(self.config)

    async def load_model(self, config: DictConfig) -> None:
        """Initialize the model from the given config"""
        opt_from_config = config.get("opt_file", None)
        model_from_config = config.get("model_file", None)
        overrides = dict(config.get("overrides", {}))

        if opt_from_config is None and model_from_config is None:
            raise AssertionError(f"Must provide one of opt_file or model_file")

        if opt_from_config is None:
            parser = ParlaiParser(True, True, "")
            opt = parser.parse_args(args=[])
            opt["override"] = opt.get("override", {})
        else:
            opt_file = os.path.expanduser(opt_from_config)
            opt = Opt.load(os.path.expanduser(opt_file))
            for key, item in opt.items():
                if not isinstance(item, str):
                    continue
                if "$LIGHT_MODEL_ROOT" in item:
                    # Expand path and file keys to capture $LIGHT_MODEL_ROOT
                    opt[key] = os.path.expandvars(opt[key])

            base_overrides = opt.get("base_overrides", {})
            base_overrides.update(opt.copy())
            opt["override"] = base_overrides

        if model_from_config is not None:
            model_file = os.path.expanduser(config.model_file)
            if not os.path.exists(model_file):
                raise AssertionError(
                    f"Provided model file `{model_file}` does not exist."
                )
            opt["model_file"] = model_file

        opt.update(overrides)
        opt["override"].update(overrides)
        model = create_agent(opt)

        context_fill = opt.get("truncate", CONTEXT_FILL_COUNT)
        # Push something through the model to fill context
        try:
            act = {
                "text": INIT_CONTEXT + "Hello " * context_fill,
                "episode_done": True,
            }
            if opt.get("eval_candidates") == "inline":
                act["label_candidates"] = ["hi", "hi there", "whatup"]
            model.observe(act)
            await model.act()
        except Exception as e:
            print(f"Cannot warm model {opt['model']}, hit error {e}")

        # Share the model params for use in `get_model`
        self._shared = model.share()

    def before_return_model(self, model):
        """Do any post-initialization we need for this model"""
        return model

    def get_model(self, overrides: Optional[Dict[str, Any]] = None) -> Agent:
        """Get a copy of the model"""
        use_shared = self._shared
        if use_shared is not None:
            opt = deepcopy(use_shared["opt"])
            if overrides is not None:
                opt.update(overrides)
            use_shared["opt"] = opt
        model = create_agent_from_shared(use_shared)
        return self.before_return_model(model)
