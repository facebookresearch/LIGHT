#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from light.graph.builders.map_json_builder import MapJsonBuilder
from light.world.world import World
from light.world.purgatory import TutorialPurgatory
from light.graph.structured_graph import OOGraph

from typing import Dict, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from light.data_model.light_database import LIGHTDatabase


class TutorialWorldBuilder(MapJsonBuilder):
    """
    Simple world builder to deal with worlds that are
    made to run tutorials. Generally like a single room builder.
    """

    def __init__(self, db: "LIGHTDatabase", opt: Dict[str, Any] = None):
        """Store initialization options"""
        self.db = db
        self.opt = opt if opt is not None else {}

    def add_random_new_agent_to_graph(self, target_graph):
        """Add an agent to the graph in a random room somewhere"""
        raise Exception("Agents should not be added to tutorials!")

    def build_new_graph(self):
        """
        Create a tutorial graph, not from file
        """
        graph = OOGraph(self.opt)
        room_node = graph.add_room(
            "Impossible Tavern",
            {
                "room": True,
                "desc": "A tutorial tavern",
                "extra_desc": "Extra tutorial description",
                "size": 2000,
                "contain_size": 2000,
                "name_prefix": "the",
                "surface_type": "in",
                "classes": {"room"},
            },
        )

        agent_node = graph.add_agent(
            "You",
            {
                "agent": True,
                "size": 20,
                "contain_size": 20,
                "health": 2,
                "food_energy": 1,
                "aggression": 0,
                "speed": 5,
                "char_type": "person",
                "desc": "Looks like someone who plays LIGHT...",
                "name_prefix": "",
                "persona": "You are, well, yourself... a wandering soul who "
                "has yet to become someone in the full LIGHT world. ",
            },
        )
        agent_node.move_to(room_node)
        dungeon_master_node = graph.add_agent(
            "Dungeon Master",
            {
                "agent": True,
                "size": 20,
                "contain_size": 20,
                "health": 200,
                "food_energy": 1,
                "aggression": 0,
                "speed": 5,
                "char_type": "person",
                "desc": "The ever-wise curious dungeon master. They appear to be observing you closely.",
                "persona": "You are the dungeon master, and should be able to help people learn to play LIGHT!",
            },
        )
        dungeon_master_node.move_to(room_node)

        boots_node = graph.add_object(
            "boots",
            {
                "object": True,
                "size": 1,
                "food_energy": 0,
                "value": 1,
                "desc": "A nice pair of boots. You might want to put these on.",
                "wearable": True,
            },
        )
        boots_node.move_to(agent_node)

        ticket_node = graph.add_object(
            "ticket to LIGHT",
            {
                "object": True,
                "size": 1,
                "food_energy": 0,
                "value": 1,
                "desc": "Your welcome ticket to LIGHT! You don't recall where you got this, but it seems important.",
            },
        )
        ticket_node.move_to(agent_node)

        exit_node = graph.add_room(
            "Ethereal Mist",
            {
                "room": True,
                "desc": "You feel yourself stretched into a different reality",
                "extra_desc": "Extra tutorial description",
                "size": 2000,
                "contain_size": 2000,
                "name_prefix": "the",
                "surface_type": "in",
                "classes": {"room"},
            },
        )
        room_node.add_neighbor(
            exit_node,
            "A shimmering portal",
            None,
            "You feel as if this portal leads somewhere unusual.",
        )
        return graph

    def get_graph(self):
        """Create and return a tutorial graph"""
        if self.opt.get("load_map", None) is not None:
            graph, _ = super().get_graph()
        else:
            graph = self.build_new_graph()

        world = World(self.opt, self)
        world.oo_graph = graph
        world.purgatory = TutorialPurgatory(world)
        return graph, world
