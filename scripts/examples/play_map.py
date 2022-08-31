#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# To run, use:
# python scripts/examples/play_map.py --use-models GenerativeHeuristicModelSoul

import sys

import parlai.utils.misc as parlai_utils

from light.graph.builders.map_json_builder import MapJsonBuilder
from light.graph.builders.starspace_all import StarspaceBuilder
from light.data_model.light_database import LIGHTDatabase
from light.world.utils.terminal_player_provider import TerminalPlayerProvider
from parlai.core.params import ParlaiParser
from light.world.world import World
from light.world.souls.base_soul import BaseSoul
from light.world.souls.repeat_soul import RepeatSoul
from light.world.souls.on_event_soul import OnEventSoul
from light.world.souls.models.generative_heuristic_model_soul import (
    GenerativeHeuristicModelSoul,
)
from light.world.souls.models.generative_heuristic_model_with_start_feature_soul import (
    GenerativeHeuristicModelWithStartFeatureSoul,
)

import os
import random
import numpy
import asyncio

random.seed(6)
numpy.random.seed(6)
shared_model_content = None


def init_world(world_builder):
    g, world = world_builder.get_graph()
    purgatory = world.purgatory
    purgatory.register_shared_args("rpg_model", rpg_model_content)
    purgatory.register_shared_args("generic_act_model", generic_act_model_content)

    # Choose the type of NPC souls.
    if opt["use_models"] == "GenerativeHeuristicModelSoul":
        purgatory.register_filler_soul_provider(
            "model", GenerativeHeuristicModelSoul, lambda: [shared_model_content]
        )
    elif opt["use_models"] == "GenerativeHeuristicModelWithStartFeatureSoul":
        print("on it")
        purgatory.register_filler_soul_provider(
            "model",
            GenerativeHeuristicModelWithStartFeatureSoul,
            lambda: [shared_model_content],
        )
    elif opt["use_models"] == "OnEventSoul":
        purgatory.register_filler_soul_provider("repeat", OnEventSoul, lambda: [{}])
    else:
        purgatory.register_filler_soul_provider("repeat", RepeatSoul, lambda: [])

    for empty_agent in world.oo_graph.agents.values():
        purgatory.fill_soul(empty_agent)
    provider = TerminalPlayerProvider(purgatory)
    return provider


async def run_with_builder(world_builder):
    """
    Takes in a World object and its OOGraph and allows one to play with a random map
    """
    player_provider = init_world(world_builder)
    player_provider.process_terminal_act("")  # get an agent
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
            player_provider = init_world(world_builder)
            player_provider.process_terminal_act("")  # get an agent
            await asyncio.sleep(0.01)
        else:
            player_provider.process_terminal_act(act)
        await asyncio.sleep(0.01)


parser = ParlaiParser()
parser.add_argument(
    "--use-models",
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
    default="/checkpoint/light/models/"
    # default="/checkpoint/light/models/"
)
parser.add_argument(
    "--load-map", type=str, default="scripts/examples/simple_world.json"
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
    "--roleplaying-score-model-file",
    type=str,
    default="",
    # default="/checkpoint/light/models/game2020/roleplay_scorer/model",
)
parser.add_argument(
    "--generic-act-model-file",
    type=str,
    default="/checkpoint/light/models/game2021/act_model/model",
)
parser.add_argument(
    "--parser-model-file",
    type=str,
    default="",  # "/checkpoint/jase/projects/light/parser/parser3/34c_jobid=1/model"
)
opt, _unknown = parser.parse_and_process_known_args()

if opt["load_map"] != "none":
    Builder = MapJsonBuilder
    ldb = ""
    world_builder = Builder(ldb, debug=False, opt=opt)
else:
    StarspaceBuilder.add_parser_arguments(parser)
    opt, _unknown = parser.parse_and_process_known_args()
    ldb = LIGHTDatabase(opt["light_db_file"], read_only=True)
    world_builder = StarspaceBuilder(ldb, debug=False, opt=opt)

if opt["roleplaying_score_model_file"] != "":
    # Load RPG scorer.
    rpg_model_content = BaseSoul.load_roleplaying_score_model(
        opt["roleplaying_score_model_file"]
    )
else:
    rpg_model_content = None

if opt["generic_act_model_file"] != "":
    generic_act_model_content = BaseSoul.load_generic_act_model(
        opt["generic_act_model_file"]
    )
else:
    generic_act_model_content = None

if opt["use_models"] == "GenerativeHeuristicModelSoul":
    light_model_root = opt["light_model_root"]
    shared_model_content = GenerativeHeuristicModelSoul.load_models(
        light_model_root + "game2021/gen_dialog_model/model.checkpoint",
    )
    shared_model_content["shared_action_model"] = generic_act_model_content.share()

if opt["use_models"] == "GenerativeHeuristicModelWithStartFeatureSoul":
    light_model_root = opt["light_model_root"]
    shared_model_content = GenerativeHeuristicModelWithStartFeatureSoul.load_models(
        light_model_root
        + "game2021/gen_dialog_model_with_start_feature/model.checkpoint",
        # light_model_root + "game2021/gen_dialog_model/model.checkpoint",
    )
    shared_model_content["shared_action_model"] = generic_act_model_content.share()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_with_builder(world_builder))
