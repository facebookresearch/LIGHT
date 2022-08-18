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
    """Register a model loader and it's config for use in LIGHT"""
    # Store this model config as a usable schema load all of the
    # possible model type names. This allows usage of
    # light.model_pool.<model_type> = CONFIG_CLASS after setting
    # light/model_pool/<model_type>/schema: CONFIG_CLASS in the defaults list
    for model_type_name in ModelTypeName:
        config.store(
            name=loader.CONFIG_CLASS._loader,
            node=loader.CONFIG_CLASS,
            group=f"light/model_pool/{model_type_name.value}/schema",
            package=f"light.model_pool.{model_type_name.value}",
        )

    # We also store the schema directly, such that someone can use
    # schema/light/model: ParlAI
    # model=<some ParlAI model config> directly.
    # See `deploy/web/server/model_server.py` for an example of this.
    config.store(
        name=loader.CONFIG_CLASS._loader,
        node=loader.CONFIG_CLASS,
        group=f"schema/light/model",
        package=f"model",
    )


def register_db_config(db_config: Type[LightDBConfig]):
    """
    Register a db backend's configuration
    """
    # Store the schema, allowing defaults list values like
    # defaults:
    # - /schema/light/db: local
    # - /light/db: <my config matching local schema>
    config.store(
        name=db_config.backend,
        node=db_config,
        group=f"schema/light/db",
        package="light.db",
    )
    # Store the default value by name, such that the default
    # can be used directly:
    # defaults:
    # - /schema/light/db: local
    # - /light/db: local
    config.store(
        name=db_config.backend,
        node=db_config,
        group=f"light/db",
        package="light.db",
    )


def register_builder_config(builder_config: Type["GraphBuilderConfig"]):
    """Register a graph builders schema and default configuration"""
    # Store the schema and default values, similar to register_db_config
    config.store(
        name=builder_config._builder,
        node=builder_config,
        group=f"schema/light/builder",
        package="builder",
    )
    config.store(
        name=builder_config._builder,
        node=builder_config,
        group=f"builder",
        package="builder",
    )


light_default_list = ["_self_", {"model_pool": "base"}]


# Basic LIGHT config initializes an empty model pool, no DB, and standard dirs
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
    """
    Register the given script config into LIGHT's hydra store
    for use in hydra.main() by `name`.
    """
    config.store(name=name, node=module)
