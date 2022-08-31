#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import json
import random, copy
import asyncio
from light.graph.structured_graph import OOGraph
from light.graph.builders.base import (
    GraphBuilder,
    SingleSuggestionGraphBuilder,
    POSSIBLE_NEW_ENTRANCES,
)
from light.graph.events.graph_events import ArriveEvent
from light.world.world import World, WorldConfig

from typing import TYPE_CHECKING, List, Dict, Tuple, Any, Optional

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import (
        GraphRoom,
        GraphNode,
        NodeProps,
        GraphAgent,
    )
    from light.data_model.db.episodes import EpisodeDB


class MapJsonBuilder(GraphBuilder):
    """Loads maps exported from the structured_graph to_json method."""

    def __init__(
        self, episode_db: Optional["EpisodeDB"], opt: Optional[Dict[str, Any]]
    ):
        """Store initialization options"""
        self.opt = opt if opt is not None else {}
        self.episode_db = episode_db
        self.original_agents: Dict[str, Tuple["GraphRoom", "NodeProps"]] = {}
        self._no_npc_models = True

    def _get_attached_config(
        self, world_config: Optional[WorldConfig] = None, opt: Dict[str, Any] = None
    ) -> WorldConfig:
        """
        Get a copy of the given world config attached to this builder
        """
        if opt is None:
            opt = self.opt
        if world_config is None:
            return WorldConfig(episode_db=self.episode_db, opt=opt, graph_builder=self)
        else:
            world_config = world_config.copy()
            world_config.graph_builder = self
            return world_config

    async def get_graph(self, world_config: Optional[WorldConfig] = None):
        input_json = self.opt["load_map"]
        f = open(input_json, "r")
        data = f.read()
        f.close()
        g = OOGraph.from_json(data, self.opt)
        g._opt = self.opt
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
