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

from light.graph.builders.external_map_json_builder import ExternalMapJsonBuilder
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
from longcontext_player_provider import LongcontextPlayerProvider
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
    purgatory.register_filler_soul_provider(
        "model", PartnerHeuristicModelSoul, lambda: [shared_model_content]
    )
    #purgatory.register_filler_soul_provider("repeat", LongcontextSoul, lambda: [])
    #print("init_world")
    for empty_agent in world.oo_graph.agents.values():
        purgatory.fill_soul(empty_agent)
    #return world
    provider = LongcontextPlayerProvider(purgatory)
    return provider, world



async def run_with_builder2(world_builder):
    world = init_world(world_builder)
    while True:
        #import pdb; pdb.set_trace()
        for id, agent in world.purgatory.node_id_to_soul.items():
            agent.handle_act("look")

async def run_with_builder(world_builder):
    player_provider, world = init_world(world_builder)
    player_provider.process_longcontext_act("")  # get an agent
    player_provider.process_longcontext_act("go east")  # get an agent
    while True:
        for soulid, soul in world.purgatory.node_id_to_soul.items():
            # import pdb; pdb.set_trace()
            if str(type(soul)) == "<class 'partner_heuristic_model_soul.PartnerHeuristicModelSoul'>":
                # print(soul)
                soul.take_timestep()

        if player_provider.obs_cnt == 0:
            pass
            #text = "look" #'"hello there!"'
            #player_provider.process_longcontext_act(text)
        else:
            pass #print(player_provider.obs_cnt)
        await asyncio.sleep(0.01)
        
async def run_with_builder0(world_builder):
    """
    Takes in a World object and its OOGraph and allows one to play with a random map
    """
    player_provider = init_world(world_builder)
    player_provider.process_longcontext_act("")  # get an agent
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
            player_provider.process_longcontext_act("")  # get an agent
            await asyncio.sleep(0.01)
        else:
            player_provider.process_longcontext_act(act)
        await asyncio.sleep(0.01)


parser = ParlaiParser()
parser.add_argument(
    "--use-models",
    type=str,
    default="LongcontextSoul",
    choices={"OnEventSoul", "RepeatSoul", "PartnerHeuristicModelSoul"},
)
parser.add_argument(
    "--light-model-root", type=str, default="/checkpoint/light/models/"
)
parser.add_argument(
    "--load-map", type=str, default="projects/longcontext/simple_world.json"
)
parser.add_argument(
    "--safety-classifier-path",
    type=str,
    default="/checkpoint/light/data/safety/reddit_and_beathehobbot_lists/OffensiveLanguage.txt",
)
opt, _unknown = parser.parse_and_process_known_args()

if opt["load_map"] != "none":
    Builder = ExternalMapJsonBuilder
    ldb = ""
    world_builder = Builder(ldb, debug=False, opt=opt)
else:
    StarspaceBuilder.add_parser_arguments(parser)
    opt, _unknown = parser.parse_and_process_known_args()
    ldb = LIGHTDatabase(opt["light_db_file"])
    world_builder = StarspaceBuilder(ldb, debug=False, opt=opt)

if True:
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
