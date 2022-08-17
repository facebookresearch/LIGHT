#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Contains helper functions that allow us to register hydra
structured configs.
"""

import os
from os.path import abspath, dirname
from hydra.core.config_store import ConfigStoreWithProvider
from dataclasses import dataclass, field, fields, Field, make_dataclass
from omegaconf import OmegaConf, MISSING, DictConfig

from light.registry.base_model_loader import ModelLoader, ModelConfig
from light.registry.model_pool import ALL_LOADERS_LIST, ModelTypeName
from light.data_model.db.base import LightDBConfig, ALL_DB_CONFIGS_LIST

from typing import List, Type, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from light.graph.builders.base import GraphBuilderConfig

LIGHT_DIR = dirname(dirname(dirname(abspath(__file__))))

config = ConfigStoreWithProvider("light")

model_type_name_default = [(x.value, ModelConfig, MISSING) for x in ModelTypeName]
ModelPoolConfig = make_dataclass("ModelPoolConfig", model_type_name_default)


def register_model_loader(loader: Type[ModelLoader]):
    # Store this model config as usable to load all of the
    # possible model type names
    for model_type_name in ModelTypeName:
        config.store(
            name=loader.CONFIG_CLASS._loader,
            node=loader.CONFIG_CLASS,
            group=f"light/model_pool/{model_type_name.value}/schema",
            package=f"light.model_pool.{model_type_name.value}",
        )
    config.store(
        name=loader.CONFIG_CLASS._loader,
        node=loader.CONFIG_CLASS,
        group=f"schema/light/model",
        package=f"model",
    )


def register_db_config(db_config: Type[LightDBConfig]):
    config.store(
        name=db_config.backend,
        node=db_config,
        group=f"schema/light/db",
        package="light.db",
    )
    config.store(
        name=db_config.backend,
        node=db_config,
        group=f"light/db",
        package="light.db",
    )


def register_builder_config(builder_config: Type["GraphBuilderConfig"]):
    config.store(
        name=builder_config._builder,
        node=builder_config,
        group=f"schema/light/builder",
        package="builder",
    )


light_default_list = ["_self_", {"model_pool": "base"}]


@dataclass
class LightConfig:
    defaults: List[Any] = field(default_factory=lambda: light_default_list)
    model_pool: ModelPoolConfig = ModelPoolConfig()
    db: LightDBConfig = MISSING
    log_level: str = "info"
    model_root: str = field(
        default=os.path.join(LIGHT_DIR, "models"),
        metadata={"help": "Where LIGHT looks for model files"},
    )
    light_dir: str = LIGHT_DIR


@dataclass
class ScriptConfig:
    light: LightConfig = LightConfig()
    defaults: List[Any] = field(default_factory=lambda: ["_self_"])


def initialize_named_configs():
    """
    Functionality to register the configurations for LIGHT. To be done
    when loading `light`
    """
    config.store(
        name="base",
        node=LightConfig,
        group="light",
    )
    config.store(name="base", node=ModelPoolConfig, group="light/model_pool")
    for loader in ALL_LOADERS_LIST:
        register_model_loader(loader)
    for db_config in ALL_DB_CONFIGS_LIST:
        register_db_config(db_config)
    from light.graph.builders.map_json_builder import MapJsonBuilderConfig

    register_builder_config(MapJsonBuilderConfig)


def register_script_config(name: str, module: Any):
    config.store(name=name, node=module)
