#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import json
import random, copy
import asyncio
import os
from dataclasses import dataclass, field
from light.graph.structured_graph import OOGraph
from light.graph.builders.base import (
    GraphBuilder,
    GraphBuilderConfig,
    SingleSuggestionGraphBuilder,
    POSSIBLE_NEW_ENTRANCES,
)
from light.graph.events.graph_events import ArriveEvent
from light.world.world import World, WorldConfig
from light import LIGHT_DIR

from typing import TYPE_CHECKING, List, Dict, Tuple, Any, Optional, ClassVar, Type

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import (
        GraphRoom,
        GraphNode,
        NodeProps,
        GraphAgent,
    )
    from light.data_model.db.episodes import EpisodeDB


@dataclass
class MapJsonBuilderConfig(GraphBuilderConfig):
    _builder: str = "MapJsonBuilder"
    load_map: str = field(
        default=os.path.join(LIGHT_DIR, "scripts/examples/simple_world.json"),
        metadata={"help": "Map file to load to play the game on"},
    )


class MapJsonBuilder(GraphBuilder):
    """Loads maps exported from the structured_graph to_json method."""

    CONFIG_CLASS = MapJsonBuilderConfig

    def __init__(self, cfg: MapJsonBuilderConfig):
        """Store initialization options"""
        self.map = cfg.load_map
        self.original_agents: Dict[str, Tuple["GraphRoom", "NodeProps"]] = {}

    def _get_attached_config(self, world_config: WorldConfig) -> WorldConfig:
        """
        Get a copy of the given world config attached to this builder
        """
        world_config = world_config.copy()
        world_config.graph_builder = self
        return world_config

    async def get_graph(self, world_config: WorldConfig):
        input_json = self.map
        f = open(input_json, "r")
        data = f.read()
        f.close()
        g = OOGraph.from_json(data)
        self.original_agents = {
            agent.name: (agent.get_room(), agent.get_props())
            for agent in g.agents.values()
        }
        world = World(self._get_attached_config(world_config))
        world.oo_graph = g
        return g, world

    def _get_agent_to_respawn(self, world: World) -> Optional[str]:
        """Return an agent that once existed in this graph, but no longer does"""
        # Only spawn agents if they don't already exist
        agents_to_use = [
            agent_name
            for agent_name in self.original_agents.keys()
            if len(world.oo_graph.find_nodes_by_name(agent_name)) == 0
        ]
        if len(agents_to_use) == 0:
            return None

        return random.choice(agents_to_use)

    def _spawn_agent_in_room(
        self, world: World, agent: "GraphAgent", room: "GraphRoom"
    ) -> None:
        """Spawn the given agent in the given room of the given world"""
        agent.move_to(room)
        arrival_event = ArriveEvent(
            agent, text_content=f"arrives from {random.choice(POSSIBLE_NEW_ENTRANCES)}"
        )
        arrival_event.execute(world)

    async def add_random_new_agent_to_graph(self, world) -> Optional["GraphAgent"]:
        """
        Add an agent from the stored original_agents list that isn't
        currently present in the world, if such an agent exists.

        Return that agent if it is created, otherwise return None
        """
        possible_respawn_name = self._get_agent_to_respawn(world)
        if possible_respawn_name is None:
            return None

        g = world.oo_graph
        agent_location, agent_props = self.original_agents[possible_respawn_name]
        agent_node = g.add_agent(possible_respawn_name, agent_props)
        self._spawn_agent_in_room(world, agent_node, agent_location)

        return agent_node

    def force_add_agent(self, world) -> "GraphAgent":
        g = world.oo_graph
        pos_rooms = [x for x in g.rooms.values()]
        random.shuffle(pos_rooms)

        agent_node = g.add_agent("test_agent", {})
        self._spawn_agent_in_room(world, agent_node, pos_rooms[0])
        return agent_node
