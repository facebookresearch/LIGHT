#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig
import enum

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


# We should make a base ModelLoader class
ModelLoaderClass = Union[Type[ParlAIModelLoader], Type[ParlAIRemoteModelLoader]]
ModelLoader = Union[ParlAIModelLoader, ParlAIRemoteModelLoader]
ModelConfig = Union[ParlAIModelConfig, ParlAIRemoteModelConfig]

ALL_LOADERS: Dict[str, ModelLoaderClass] = {
    ParlAIModelConfig._loader: ParlAIModelLoader,
    ParlAIPolyencoderActingScoreModelConfig._loader: ParlAIPolyencoderActingScoreModelLoader,
    MapStarspaceModelConfig._loader: MapStarspaceModelLoader,
    ParlAIRemoteModelConfig._loader: ParlAIRemoteModelLoader,
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

    def register_model(
        self, config: Union[DictConfig, ModelConfig], model_names: List[ModelTypeName]
    ) -> None:
        """
        Takes the given config, loads the model, and
        stores it in the registry under the given names.
        """
        loader_class = ALL_LOADERS.get(config._loader)
        if loader_class is None:
            raise AssertionError(
                f"Trying to load a model with non-existent loader {config._loader}"
            )
        loader = loader_class(config)
        for model_name in model_names:
            self._model_loaders[model_name.value] = loader

    def has_model(self, model_name: ModelTypeName) -> bool:
        """
        Determine if there's a model registered for the given name.
        """
        return model_name.value in self._model_loaders

    def get_model(
        self, model_name: ModelTypeName, overrides: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """
        Get a copy of the model stored in the given name

        If overrides are provided, pass those to the loader as well
        """
        loader = self._model_loaders.get(model_name.value)
        if loader is None:
            raise AssertionError(
                f"No models registered for requested name {model_name}"
            )
        return loader.get_model(overrides)
