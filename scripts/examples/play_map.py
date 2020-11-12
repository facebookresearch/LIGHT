#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# To run on a devfair, use:
# python scripts/examples/play_random_map.py
# To run on Jack's laptop, run:
# python scripts/examples/play_random_map.py --light-model-root ~/Desktop/LIGHT/LIGHT_models/ --light-db-file ~/ParlAI/data/light/environment/db/database3.db

import sys

import parlai.utils.misc as parlai_utils

from light.graph.builders.map_json_builder import MapJsonBuilder
from light.graph.builders.starspace_all import StarspaceBuilder
from light.data_model.light_database import LIGHTDatabase
from light.world.utils.terminal_player_provider import TerminalPlayerProvider
from parlai.core.params import ParlaiParser
from light.world.world import World
from light.world.souls.repeat_soul import RepeatSoul
from light.world.souls.on_event_soul import OnEventSoul
from light.world.souls.models.partner_heuristic_model_soul import (
    PartnerHeuristicModelSoul,
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
    # Choose the type of NPC souls.
    if opt["use_models"] == "PartnerHeuristicModelSoul":
        purgatory.register_filler_soul_provider(
            "model", PartnerHeuristicModelSoul, lambda: [shared_model_content]
        )
    elif opt["use_models"] == "OnEventSoul":
        purgatory.register_filler_soul_provider("repeat", OnEventSoul, lambda: [ {} ])
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
    choices={"OnEventSoul", "RepeatSoul", "PartnerHeuristicModelSoul"},
)
parser.add_argument(
    "--light-model-root", type=str, default="/checkpoint/light/models/"
)
parser.add_argument(
    "--load-map", type=str, default="scripts/examples/simple_world.json"
)
parser.add_argument(
    "--dont-catch-errors",
    type="bool",
    default=True
)
parser.add_argument(
    "--safety-classifier-path",
    type=str,
    default="/checkpoint/light/data/safety/reddit_and_beathehobbot_lists/OffensiveLanguage.txt",
)
parser.add_argument(
    "--parser-model-file",
    type=str,
    default="/checkpoint/jase/projects/light/parser/parser3/34c_jobid=1/model"
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

if opt["use_models"] == "PartnerHeuristicModelSoul":
    light_model_root = opt["light_model_root"]
    shared_model_content = PartnerHeuristicModelSoul.load_models(
        light_model_root + "game_speech1/model",
        light_model_root + "speech_train_cands.txt",
        light_model_root + "agent_to_utterance_trainset.txt",
        light_model_root + "main_act/model",
    )

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_with_builder(world_builder))
