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
from parlai.core.params import ParlaiParser
from light.world.world import World
from light.world.souls.repeat_soul import RepeatSoul
from light.world.souls.on_event_soul import OnEventSoul
import os
import random
import numpy
import asyncio

# local classes
from longcontext_soul import LongcontextSoul
from partner_heuristic_model_soul import (
    PartnerHeuristicModelSoul,
)

random.seed(6)
numpy.random.seed(6)
shared_model_content = None


def init_world(world_builder):
    g, world = world_builder.get_graph()
    purgatory = world.purgatory
    # Choose the type of NPC souls.
    if world.opt["use_models"] == "PartnerHeuristicModelSoul":
        purgatory.register_filler_soul_provider(
            "model", PartnerHeuristicModelSoul, lambda: [shared_model_content]
        )
    else:
        purgatory.register_filler_soul_provider("model", LongcontextSoul, lambda: [])
    # print("init_world")
    for empty_agent in world.oo_graph.agents.values():
        purgatory.fill_soul(empty_agent)
    return world


async def run_with_builder(world_builder):
    world = init_world(world_builder)

    # make first character the one that we vie
    for soulid, soul in world.purgatory.node_id_to_soul.items():
        if hasattr(soul, "take_timestep"):
            soul.is_viewed = True
            soul.target_node.is_viewed = True
            world.view_soul = soul
            world.tasks = {}
            for soulid2, soul2 in world.purgatory.node_id_to_soul.items():
                if soulid != soulid2:
                    world.tasks[soul2.target_node] = False

            print("You are: " + soul.target_node.names[0])
            # agent.handle_act("inventory")
            break

    await asyncio.sleep(0.01)
    while True:
        for soulid, soul in world.purgatory.node_id_to_soul.items():
            if hasattr(soul, "take_timestep"):
                soul.take_timestep()
            await asyncio.sleep(0.00001)


parser = ParlaiParser()
parser.add_argument(
    "--use-models",
    type=str,
    # default="LongcontextSoul",
    default="PartnerHeuristicModelSoul",
    choices={"LongcontextSoul", "PartnerHeuristicModelSoul"},
)
parser.add_argument("--light-model-root", type=str, default="/checkpoint/light/models/")
parser.add_argument(
    "--load-map",
    type=str,
    default="scripts/examples/complex_world.json"
    # "--load-map", type=str, default="scripts/examples/simple_world.json"
)
parser.add_argument(
    "--safety-classifier-path",
    type=str,
    default="",  # "/checkpoint/light/data/safety/reddit_and_beathehobbot_lists/OffensiveLanguage.txt",
)
opt, _unknown = parser.parse_and_process_known_args()


if opt["load_map"] != "none":
    Builder = MapJsonBuilder
    ldb = ""
    world_builder = Builder(ldb, debug=False, opt=opt)
else:
    StarspaceBuilder.add_parser_arguments(parser)
    opt, _unknown = parser.parse_and_process_known_args()
    ldb = LIGHTDatabase(opt["light_db_file"])
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
    # run_with_builder(world_builder)
