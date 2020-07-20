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

from light.graph.builders.starspace_all import StarspaceBuilder
from light.data_model.light_database import LIGHTDatabase
from light.world.utils.terminal_player_provider import TerminalPlayerProvider
from parlai.core.params import ParlaiParser
from light.world.world import World
from light.world.souls.repeat_soul import RepeatSoul
import os
import random
import numpy

random.seed(6)
numpy.random.seed(6)


def init_world(world_builder):
    g, world = world_builder.get_graph()
    purgatory = world.purgatory
    # TODO load this from models!
    purgatory.register_filler_soul_provider("repeat", RepeatSoul, lambda: [])
    for empty_agent in world.oo_graph.agents.values():
        purgatory.fill_soul(empty_agent)
    provider = TerminalPlayerProvider(purgatory)
    return provider


def run_with_builder(world_builder):
    """
    Takes in a World object and its OOGraph and allows one to play with a random map
    """
    player_provider = init_world(world_builder)
    player_provider.process_terminal_act("")  # get an agent
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
        else:
            player_provider.process_terminal_act(act)


parser = ParlaiParser()
StarspaceBuilder.add_parser_arguments(parser)
opt, _unknown = parser.parse_and_process_known_args()
ldb = LIGHTDatabase(opt['light_db_file'])
world_builder = StarspaceBuilder(ldb, debug=False, opt=opt)

run_with_builder(world_builder)
