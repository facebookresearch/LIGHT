#!/usr/bin/env python3
# To run locally, use:
# python play_random_map.py --light-model-root /checkpoint/jase/projects/light/dialog/:no_npc_models  --light-db-file labeling/light_jfixed_environment.pkl

import sys

import parlai.utils.misc as parlai_utils

sys.modules['parlai.core.utils'] = parlai_utils

from light.graph.builders.starspace_all import (
    StarspaceBuilder,
)
from parlai.core.params import ParlaiParser
from light.world.world import World
import os
import random
import numpy

random.seed(6)
numpy.random.seed(6)


def run_graph(world):
    '''
    Takes in a World object and its OOGraph and allows one to play with a random map
    '''
    import parlai.utils.misc as parlai_utils

    sys.modules['parlai.core.utils'] = parlai_utils

    player_id = world.spawn_player()
    agent_id = world.playerid_to_agentid(player_id)
    world.parse_exec(agent_id, 'look')
    print(world.get_text(agent_id).rstrip('\n'))
    while True:
        act = input('action> ')
        if act == '':
            continue
        if act == 'exit':
            print('Exiting graph run')
            return
        elif act in ['new', 'reset']:
            print('A mist fills the world and everything resets')
            graph, world = world.graph_builder.get_graph()
            world.get_text(agent_id).rstrip('\n')
            world.parse_exec(agent_id, 'look')
            print(world.get_text(agent_id).rstrip('\n'))
        else:
            status, c_acts_text = world.parse_exec(agent_id, act)
            if status:
                world.update_world()
            agent_id = world.playerid_to_agentid(player_id)  # this might change
            print(world.get_text(agent_id).rstrip('\n'))


parser = ParlaiParser()
StarspaceBuilder.add_parser_arguments(parser)
opt, _unknown = parser.parse_and_process_known_args()
worldBuilder = StarspaceBuilder(debug=False, opt=opt)

g, world = worldBuilder.get_graph()
run_graph(world)
