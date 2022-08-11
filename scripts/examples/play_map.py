#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# To run, use:
# python scripts/examples/play_map.py --use-models GenerativeHeuristicModelSoul

import sys

import parlai.utils.misc as parlai_utils
from parlai.core.params import ParlaiParser

from light import LIGHT_DIR
from light.graph.builders.map_json_builder import MapJsonBuilder
from light.graph.builders.starspace_all import StarspaceBuilder
from light.data_model.light_database import LIGHTDatabase
from light.world.utils.terminal_player_provider import TerminalPlayerProvider

from light.world.world import World, WorldConfig
from light.world.souls.base_soul import BaseSoul
from light.world.souls.repeat_soul import RepeatSoul
from light.world.souls.on_event_soul import OnEventSoul
from light.world.souls.models.generative_heuristic_model_soul import (
    GenerativeHeuristicModelSoul,
)
from light.world.souls.models.generative_heuristic_model_with_start_feature_soul import (
    GenerativeHeuristicModelWithStartFeatureSoul,
)
from light.registry.model_pool import ModelPool
from light.registry.parlai_model import ParlAIModelConfig
from light.registry.models.acting_score_model import (
    ParlAIPolyencoderActingScoreModelConfig,
)

from typing import Dict, Any


import os
import random
import numpy
import asyncio

CONFIG_DIR = os.path.join(LIGHT_DIR, "light/registry/models/config")
random.seed(6)
numpy.random.seed(6)
shared_model_content = None


def init_world(world_builder, opt, model_pool):
    g, world = asyncio.run(
        world_builder.get_graph(world_config=WorldConfig(model_pool=model_pool))
    )
    purgatory = world.purgatory

    # Choose the type of NPC souls.
    if opt["agent_soul"] == "GenerativeHeuristicModelSoul":
        purgatory.register_filler_soul_provider(
            "model", GenerativeHeuristicModelSoul, lambda: []
        )
    elif opt["agent_soul"] == "GenerativeHeuristicModelWithStartFeatureSoul":
        purgatory.register_filler_soul_provider(
            "model",
            GenerativeHeuristicModelWithStartFeatureSoul,
            lambda: [],
        )
    elif opt["agent_soul"] == "OnEventSoul":
        purgatory.register_filler_soul_provider("repeat", OnEventSoul, lambda: [])
    else:
        purgatory.register_filler_soul_provider("repeat", RepeatSoul, lambda: [])

    for empty_agent in world.oo_graph.agents.values():
        purgatory.fill_soul(empty_agent)
    provider = TerminalPlayerProvider(purgatory)
    return provider


async def run_with_builder(world_builder, opt, model_pool):
    """
    Takes in a World object and its OOGraph and allows one to play with a random map
    """
    player_provider = init_world(world_builder, opt, model_pool)
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
            player_provider = init_world(world_builder, opt, model_pool)
            await player_provider.process_terminal_act("")  # get an agent
            await asyncio.sleep(0.01)
        else:
            await player_provider.process_terminal_act(act)
        await asyncio.sleep(0.01)


def parse_and_return_args():
    parser = ParlaiParser()
    parser.add_argument(
        "--agent-soul",
        type=str,
        default="OnEventSoul",
        choices={
            "OnEventSoul",
            "RepeatSoul",
            "GenerativeHeuristicModelSoul",
            "GenerativeHeuristicModelWithStartFeatureSoul",
        },
    )
    parser.add_argument(
        "--light-model-root",
        type=str,
        default=os.path.join(LIGHT_DIR, "models")
        # default="/checkpoint/light/models/"
    )
    parser.add_argument(
        "--load-map",
        type=str,
        default=os.path.join(LIGHT_DIR, "scripts/examples/simple_world.json"),
    )
    parser.add_argument("--dont-catch-errors", type="bool", default=True)
    parser.add_argument(
        "--safety-classifier-path",
        type=str,
        default="",
        # default="/checkpoint/light/data/safety/reddit_and_beathehobbot_lists/OffensiveLanguage.txt",
    )
    parser.add_argument(
        "--magic-db-path",
        type=str,
        # default=""
        default="/checkpoint/light/magic/magic.db,scripts/examples/special_items.db"
        # default = "scripts/examples/special_items.db"
    )
    parser.add_argument("--allow-save-world", type="bool", default=True)
    parser.add_argument(
        "--roleplaying-score-opt-file",
        type=str,
        default=os.path.join(CONFIG_DIR, "baseline_roleplaying_scorer.opt"),
    )
    parser.add_argument(
        "--acting-model-opt-file",
        type=str,
        default=os.path.join(CONFIG_DIR, "baseline_main_act_model.opt"),
    )
    parser.add_argument(
        "--generic-act-opt-file",
        type=str,
        default=os.path.join(CONFIG_DIR, "generic_act_model.opt"),
    )
    parser.add_argument(
        "--parser-opt-file",
        type=str,
        default=os.path.join(CONFIG_DIR, "baseline_parser.opt"),
    )
    parser.add_argument("--no-models", default=False, action="store_true")
    parser.add_argument("--use-safety-model", default=False, action="store_true")
    opt, _unknown = parser.parse_and_process_known_args()
    return opt


def init_correct_models(opt: Dict[str, Any]) -> ModelPool:
    """Produces the correct ModelPool for the given opts"""
    model_pool = ModelPool()
    if opt["no_models"]:
        return model_pool

    os.environ["LIGHT_MODEL_ROOT"] = opt["light_model_root"]

    # Initialize dialog model
    agent_soul = opt["agent_soul"]
    if agent_soul == "GenerativeHeuristicModelSoul":
        model_pool.register_model(
            ParlAIModelConfig(
                opt_file=os.path.join(CONFIG_DIR, "baseline_generative.opt")
            ),
            ["dialog"],
        )
    elif agent_soul == "GenerativeHeuristicModelWithStartFeatureSoul":
        model_pool.register_model(
            ParlAIModelConfig(
                opt_file=os.path.join(CONFIG_DIR, "baseline_generative_with_start.opt")
            ),
            ["dialog"],
        )

    # Initialize Scoring model
    roleplaying_opt_target = opt["roleplaying_score_opt_file"]
    if roleplaying_opt_target is not None and roleplaying_opt_target != "":
        model_pool.register_model(
            ParlAIPolyencoderActingScoreModelConfig(opt_file=roleplaying_opt_target),
            ["role_playing_score"],
        )

    # Initialize Acting model
    acting_model_opt_target = opt["acting_model_opt_file"]
    if acting_model_opt_target is not None and acting_model_opt_target != "":
        model_pool.register_model(
            ParlAIModelConfig(opt_file=acting_model_opt_target), ["action"]
        )

    # Initialize Generic Acting model
    generic_act_opt_target = opt["generic_act_opt_file"]
    if generic_act_opt_target is not None and generic_act_opt_target != "":
        model_pool.register_model(
            ParlAIModelConfig(opt_file=generic_act_opt_target), ["generic_action"]
        )

    # Initialize Parser model
    parser_opt_targert = opt["parser_opt_file"]
    if parser_opt_targert is not None and parser_opt_targert != "":
        model_pool.register_model(
            ParlAIModelConfig(opt_file=parser_opt_targert), ["parser"]
        )

    # Initialize Safety model
    if opt["use_safety_model"]:
        model_pool.register_model(
            ParlAIModelConfig(
                opt_file=os.path.join(CONFIG_DIR, "baseline_adversarial_safety.opt")
            ),
            ["safety"],
        )

    return model_pool


def main():
    opt = parse_and_return_args()
    model_pool = init_correct_models(opt)

    if opt["load_map"] != "none":
        Builder = MapJsonBuilder
        ldb = ""
        world_builder = Builder(None, opt=opt)
    else:
        # TODO FIXME make this all work with Hydra instead
        # to have stacked configs
        StarspaceBuilder.add_parser_arguments(parser)
        opt, _unknown = parser.parse_and_process_known_args()
        ldb = LIGHTDatabase(opt["light_db_file"], read_only=True)
        world_builder = StarspaceBuilder(ldb, debug=False, opt=opt)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_with_builder(world_builder, opt, model_pool))


if __name__ == "__main__":
    main()
