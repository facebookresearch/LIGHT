#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig
import asyncio
import enum

from light.registry.base_model_loader import ModelConfig, ModelLoader
from light.registry.parlai_model import ParlAIModelConfig, ParlAIModelLoader
from light.registry.parlai_remote_model import (
    ParlAIRemoteModelConfig,
    ParlAIRemoteModelLoader,
)
from light.registry.models.acting_score_model import (
    ParlAIPolyencoderActingScoreModelConfig,
    ParlAIPolyencoderActingScoreModelLoader,
)
from light.registry.models.starspace_model import (
    MapStarspaceModelConfig,
    MapStarspaceModelLoader,
)

from parlai.core.agents import Agent
from typing import List, Any, Union, Dict, Optional, Type

ALL_LOADERS_LIST: List[ModelLoader] = {
    ParlAIModelLoader,
    ParlAIPolyencoderActingScoreModelLoader,
    MapStarspaceModelLoader,
    ParlAIRemoteModelLoader,
}

ALL_LOADERS_MAP: Dict[str, ModelLoader] = {
    k.CONFIG_CLASS._loader: k for k in ALL_LOADERS_LIST
}


class ModelTypeName(enum.Enum):
    """Common model names of use in LIGHT, for use in register_model"""

    SAFETY = "safety"  # Models used to evaluate dialog or env safety
    DIALOG = "dialog"  # Models for generating dialogue
    SCORING = "role_playing_score"  # Models to score player utterances
    ACTION = "action"  # Models used by model agents for generating actions
    GENERIC_ACTS = "generic_action"  # Models to select a next action from cands
    PARSER = "parser"  # Models to parse raw text to in-game actions


class ModelPool:
    def __init__(self):
        self._model_loaders = {}

    async def register_model_async(
        self, config: Union[DictConfig, ModelConfig], model_names: List[str]
    ) -> None:
        """
        Takes the given config, loads the model, and
        stores it in the registry under the given names.
        """
        loader_class = ALL_LOADERS_MAP.get(config._loader)
        if loader_class is None:
            raise AssertionError(
                f"Trying to load a model with non-existent loader {config._loader}"
            )
        loader = loader_class(config)
        await loader.load_model()
        for model_name in model_names:
            self._model_loaders[model_name] = loader

    def register_model(
        self, config: Union[DictConfig, ModelConfig], model_names: List[str]
    ) -> None:
        """
        Syncronous model registration for server and script setups
        """
        return asyncio.run(self.register_model_async(config, model_names))

    def has_model(self, model_name: str) -> bool:
        """
        Determine if there's a model registered for the given name.
        """
        return model_name in self._model_loaders

    def get_model(
        self, model_name: str, overrides: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """
        Get a copy of the model stored in the given name

        If overrides are provided, pass those to the loader as well
        """
        loader = self._model_loaders.get(model_name)
        if loader is None:
            raise AssertionError(
                f"No models registered for requested name {model_name}"
            )
        return loader.get_model(overrides)
