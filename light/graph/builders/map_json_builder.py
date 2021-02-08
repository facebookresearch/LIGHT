#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import json
import random, copy
from light.graph.structured_graph import OOGraph
from light.graph.builders.base import (
    DBGraphBuilder,
    SingleSuggestionGraphBuilder,
    POSSIBLE_NEW_ENTRANCES,
)
from light.graph.events.graph_events import ArriveEvent
from light.world.world import World


class MapJsonBuilder(DBGraphBuilder):
    """Loads maps exported from the structured_graph to_json method.
    """

    def __init__(self, ldb, debug, opt):
        self.db = ldb
        self.opt = opt
        self._no_npc_models = True
        
    def get_graph(self):
        input_json = self.opt['load_map']
        f = open(input_json, "r")
        data = f.read()
        f.close()
        g = OOGraph.from_json(data)
        world = World(self.opt, self)
        world.oo_graph = g
        return g, world

    def add_random_new_agent_to_graph(self, world):
        """Skip adding an agent, a loaded graph for now has no attached model"""
        pass

    def force_add_agent(self, world):
        g = world.oo_graph
        pos_rooms = [x for x in g.rooms.values()]
        random.shuffle(pos_rooms)

        agent_node = g.add_agent('test_agent', {})
        agent_node.move_to(pos_rooms[0])

        # Send message notifying people in room this agent arrived.
        arrival_event = ArriveEvent(
            agent_node, text_content=random.choice(POSSIBLE_NEW_ENTRANCES)
        )
        arrival_event.execute(world)
        return agent_node