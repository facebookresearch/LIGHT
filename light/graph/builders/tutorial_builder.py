#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from dataclasses import dataclass
from light.graph.builders.map_json_builder import MapJsonBuilder, MapJsonBuilderConfig
from light.world.world import World, WorldConfig
from light.world.purgatory import TutorialPurgatory
from light.graph.structured_graph import OOGraph

import asyncio
from typing import Dict, Optional, Any, TYPE_CHECKING, ClassVar, Type

if TYPE_CHECKING:
    from light.data_model.light_database import LIGHTDatabase


@dataclass
class TutorialBuilderConfig(MapJsonBuilderConfig):
    _builder: str = "TutorialWorldBuilder"
    load_map: str = ""


class TutorialWorldBuilder(MapJsonBuilder):
    """
    Simple world builder to deal with worlds that are
    made to run tutorials. Generally like a single room builder.
    """

    CONFIG_CLASS = ClassVar[Type[TutorialBuilderConfig]]

    async def add_random_new_agent_to_graph(self, target_graph):
        """Add an agent to the graph in a random room somewhere"""
        raise Exception("Agents should not be added to tutorials!")

    def build_new_graph(self, world_config: WorldConfig):
        """
        Create a tutorial graph, not from file
        """
        graph = OOGraph(title="tutorial")
        room_node = graph.add_room(
            "Impossible Tavern",
            {
                "room": True,
                "desc": "The tavern is odd. It almost feels like a dream, as nothing you "
                "see appears to stay for very long. It's almost hard to focus in "
                "here. There's a ton of background chatter you can't make out, "
                "yet the space is almost entirely empty. One thing is certain, "
                "this is a strange yet suited place to start an adventure.",
                "extra_desc": "You wonder if this place is all in the dungeon master's mind, "
                "after all they do seem to be entirely at home here.",
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
                "persona": "You are, well, yourself... a wandering soul who has yet to "
                "become someone in the full LIGHT world. Perhaps you may be "
                "granted admission by the dungeon master?\nYour Mission: Find out how to "
                "get to LIGHT, then get in to play.",
                "mission": "Find out how to get to LIGHT, then get in to play.",
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
                "persona": "I am the dungeon master, and am looking for new people to "
                "explore my fantasy world. Players may be able to find help "
                "by exploring their surroundings and the interface. I would "
                "like to help you get started in a text-adventure game. The "
                "goal is to explore, be curious, interact with others, and "
                "live an experience as somebody entirely different.",
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
                "desc": "A nice pair of boots, just your size! You might want to wear these.",
                "wearable": True,
                "name_prefix": "some",
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
                "desc": "A welcome ticket to LIGHT! 'Admits one soul to try out LIGHT'"
                "it reads across the front. You don't recall where you got "
                "this, but it seems important.",
            },
        )
        ticket_node.move_to(agent_node)

        exit_node = graph.add_room(
            "Ethereal Mist",
            {
                "room": True,
                "desc": "You feel yourself stretched into a different reality",
                "extra_desc": "The swirling is all-encompassing!",
                "size": 2000,
                "contain_size": 2000,
                "name_prefix": "the",
                "surface_type": "in",
                "classes": {"room"},
            },
        )
        room_node.add_neighbor(
            exit_node,
            "a shimmering portal",
            None,
            "You feel as if this portal leads somewhere unusual.",
        )
        dungeon_master_node.block(agent_node)
        return graph

    async def get_graph(self, world_config: Optional[WorldConfig] = None):
        """Create and return a tutorial graph"""
        world_config = self._get_attached_config(world_config)
        if self.map is not None and self.map != "":
            graph, _ = await super().get_graph(world_config)
        else:
            graph = self.build_new_graph(world_config)
        world = World(world_config)

        world.oo_graph = graph
        # Force the logging mode to tutorial PRE_LAUNCH_TUTORIAL
        world.oo_graph.title = "tutorial"
        world.purgatory = TutorialPurgatory(world)
        return graph, world
