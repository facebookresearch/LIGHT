#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Script for launching and playing a local map

Some usage examples:
Default:
python scripts/examples/play_map.py

Complex map:
python scripts/examples/play_map.py builder.load_map=scripts/examples/complex_world.json

Using some models:
python scripts/examples/play_map.py /light/model_pool=simple agent_soul=GenerativeHeuristicModelSoul

Using all models:
python scripts/examples/play_map.py /light/model_pool=baseline agent_soul=GenerativeHeuristicModelSoul
"""

import hydra
import os
from dataclasses import dataclass, field
from omegaconf import DictConfig, OmegaConf
from light.registry.hydra_registry import register_script_config, ScriptConfig

from light import LIGHT_DIR
from light.graph.builders.base import GraphBuilderConfig
from light.graph.builders.map_json_builder import MapJsonBuilder, MapJsonBuilderConfig
from light.graph.builders.starspace_all import StarspaceBuilder
from light.data_model.light_database import LIGHTDatabase
from light.world.utils.terminal_player_provider import TerminalPlayerProvider

from light.world.world import World, WorldConfig
from light.world.souls.repeat_soul import RepeatSoul
from light.world.souls.on_event_soul import OnEventSoul
from light.world.souls.models.generative_heuristic_model_soul import (
    GenerativeHeuristicModelSoul,
)
from light.world.souls.models.generative_heuristic_model_with_start_feature_soul import (
    GenerativeHeuristicModelWithStartFeatureSoul,
)
from light.registry.model_pool import ModelPool, ModelTypeName


from typing import Dict, Any, List


import os
import random
import numpy
import asyncio

CONFIG_DIR = os.path.join(LIGHT_DIR, "light/registry/models/config")
HYDRA_CONFIG_DIR = os.path.join(LIGHT_DIR, "hydra_configs")
random.seed(6)
numpy.random.seed(6)


async def run_with_builder(init_world):
    """
    Takes in a World object and its OOGraph and allows one to play with a random map
    """
    player_provider = await init_world()
    await player_provider.process_terminal_act("")  # get an agent
    await asyncio.sleep(0.01)
    while True:
        act = input("\raction> ")
        if act == "":
            continue
        if act == "exit":
            print("Exiting graph run")
            return
        elif act in ["new", "reset"]:
            print("A mist fills the world and everything resets")
            player_provider = await init_world()
            await player_provider.process_terminal_act("")  # get an agent
            await asyncio.sleep(0.01)
        else:
            await player_provider.process_terminal_act(act)
        await asyncio.sleep(0.01)


@dataclass
class PlayMapScriptConfig(ScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: ["_self_", {"conf": "local"}])
    builder: GraphBuilderConfig = MapJsonBuilderConfig()
    agent_soul: str = field(
        default="OnEventSoul",
        metadata={
            "help": "The type of soul to populate NPCs with."
            "One of OnEventSoul, RepeatSoul, GenerativeHeuristicModelSoul, "
            "GenerativeHeuristicModelWithStartFeatureSoul",
        },
    )
    magic_db_path: str = field(
        # default=""
        default="/checkpoint/light/magic/magic.db,scripts/examples/special_items.db"
        # default = "scripts/examples/special_items.db"
    )
    safety_classifier_path: str = field(
        default="",
        # default="/checkpoint/light/data/safety/reddit_and_beathehobbot_lists/OffensiveLanguage.txt",
    )
    allow_save_world: bool = field(
        default=True,
    )


register_script_config("scriptconfig", PlayMapScriptConfig)


@hydra.main(
    config_path=HYDRA_CONFIG_DIR, config_name="scriptconfig", version_base="1.2"
)
def main(cfg: PlayMapScriptConfig):
    os.environ["LIGHT_MODEL_ROOT"] = os.path.abspath(cfg.light.model_root)
    model_pool = ModelPool.get_from_config(cfg.light.model_pool)
    if not model_pool.has_model(ModelTypeName.DIALOG):
        assert cfg.agent_soul in [
            "RepeatSoul",
            "OnEventSoul",
        ], "Can only use Repeat or OnEvent souls if no models provided"

    # TODO move builder initialization from builder into base GraphBuilder
    if cfg.builder._builder == "MapJsonBuilder":
        world_builder = MapJsonBuilder(cfg.builder)
    else:
        # TODO FIXME make this all work with Hydra instead
        # to have stacked configs
        StarspaceBuilder.add_parser_arguments(parser)
        opt, _unknown = parser.parse_and_process_known_args()
        ldb = LIGHTDatabase(opt["light_db_file"], read_only=True)
        world_builder = StarspaceBuilder(ldb, debug=False, opt=opt)

    async def init_new_world() -> TerminalPlayerProvider:
        g, world = await world_builder.get_graph(
            world_config=WorldConfig(model_pool=model_pool)
        )
        purgatory = world.purgatory

        # Choose the type of NPC souls.
        if cfg.agent_soul == "GenerativeHeuristicModelSoul":
            purgatory.register_filler_soul_provider(
                "model", GenerativeHeuristicModelSoul, lambda: []
            )
        elif cfg.agent_soul == "GenerativeHeuristicModelWithStartFeatureSoul":
            purgatory.register_filler_soul_provider(
                "model",
                GenerativeHeuristicModelWithStartFeatureSoul,
                lambda: [],
            )
        elif cfg.agent_soul == "OnEventSoul":
            purgatory.register_filler_soul_provider("repeat", OnEventSoul, lambda: [])
        else:
            purgatory.register_filler_soul_provider("repeat", RepeatSoul, lambda: [])

        for empty_agent in world.oo_graph.agents.values():
            purgatory.fill_soul(empty_agent)
        provider = TerminalPlayerProvider(purgatory)
        return provider

    asyncio.run(run_with_builder(init_new_world))


if __name__ == "__main__":
    main()
