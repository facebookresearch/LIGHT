#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig

from light.registry.models.parlai_model import ParlAIModelConfig, ParlAIModelLoader
from light.registry.models.acting_score_model import (
    ParlAIPolyencoderActingScoreModelConfig,
    ParlAIPolyencoderActingScoreModelLoader,
)

from parlai.core.agents import Agent
from typing import List, Any, Dict, Optional

# At the moment all models are ParlAIModelLoaders. May change as we make more models
ALL_LOADERS: Dict[str, ParlAIModelLoader] = {
    ParlAIModelConfig._loader: ParlAIModelLoader,
    ParlAIPolyencoderActingScoreModelConfig._loader: ParlAIPolyencoderActingScoreModelLoader,
}


class ModelPool:
    def __init__(self):
        self._model_loaders = {}

    def register_model(self, config: DictConfig, model_names: List[str]) -> None:
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
            self._model_loaders[model_name] = loader

    def get_model(self, model_name: str, overrides: Optional[Dict[str, Any]]) -> Agent:
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
