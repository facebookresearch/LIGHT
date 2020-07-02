#!/usr/bin/env python3
# To run locally, use:
# python play_random_map.py --light-model-root /checkpoint/jase/projects/light/dialog/:no_npc_models  --light-db-file labeling/light_jfixed_environment.pkl

import sys

import parlai.utils.misc as parlai_utils

# sys.modules['parlai.core.utils'] = parlai_utils

from light.graph.builders.starspace_all import StarspaceBuilder
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
    # import parlai.utils.misc as parlai_utils

    # sys.modules['parlai.core.utils'] = parlai_utils

    player_provider = init_world(world_builder)
    player_provider.process_terminal_act("")  # get an agent
    while True:
        act = input("\raction> ")
        # import pdb; pdb.set_trace()
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
            player_provider.process_terminal_act(act)  # get an agent


parser = ParlaiParser()
StarspaceBuilder.add_parser_arguments(parser)
opt, _unknown = parser.parse_and_process_known_args()
world_builder = StarspaceBuilder(debug=False, opt=opt)

run_with_builder(world_builder)
