#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Base model config and loader classes to specify how models are loaded
throughout LIGHT. Allows for everything to be configured via Hydra
"""

from dataclasses import dataclass
from omegaconf import MISSING, DictConfig
from abc import ABC, abstractmethod
from parlai.core.agents import Agent  # TODO perhaps non-agent? Or some other interface
import asyncio

from typing import Optional, Any, Dict, Type, ClassVar


@dataclass
class ModelConfig:
    """
    Model configs, at a minimum, must register a loader key to process this
    config type
    """

    _loader: str = MISSING

    def get(self, attr: str, default_val: Optional[Any] = None):
        """Wrapper to ensure interoperability with hydra DictConfig"""
        val = self.__dict__.get(attr, default_val)
        if val == MISSING:
            val = None
        return val


class ModelLoader(ABC):
    """
    Class responsible for preparing a model for use within LIGHT's ModelPool
    """

    CONFIG_CLASS: ClassVar[Type[ModelConfig]]

    @abstractmethod
    def __init__(self, config: DictConfig):
        """Model Loaders must be able to init from their corresponding ModelConfig"""
        raise NotImplementedError

    @abstractmethod
    async def load_model(self) -> None:
        """This method is used after initialization to be sure resources are loaded"""
        raise NotImplementedError

    @abstractmethod
    def get_model(self, overrides: Optional[Dict[str, Any]] = None) -> "Agent":
        """Return a copy of the running model"""
        raise NotImplementedError
