#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from light.graph.builders.starspace_all import StarspaceBuilder
from light.graph.builders.map_json_builder import MapJsonBuilder
from light.graph.builders.tutorial_builder import TutorialWorldBuilder
from light.graph.builders.base import GraphBuilderConfig
from light.world.souls.repeat_soul import RepeatSoul
from light.world.souls.models.generative_heuristic_model_soul import (
    GenerativeHeuristicModelSoul,
)
from light.world.souls.models.tutorial_model_soul import (
    TutorialModelSoul,
)
from light.registry.model_pool import ModelPool, ModelTypeName

import os.path
import time
import asyncio

from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from light.data_model.db.environment import EpisodeDB
    from light.world.world import WorldConfig
    from light.graph.structured_graph import OOGraph


class Player:
    """
    A player in an instance of the light game. Maintains any required
    connections and IO such that the game doesn't need to worry about
    that stuff
    """

    def __init__(self, graph: "OOGraph", player_id: str):
        self.g = graph
        self.id = player_id
        self.init_observe()

    def get_player_id(self) -> str:
        return self.id

    def get_agent_id(self) -> str:
        return self.g.playerid_to_agentid(self.id)

    def act(self):
        """
        Get an action to take on the graph if one exists
        """
        raise NotImplementedError

    def observe(self):
        """
        Send any observed content to the player.
        This method should query the graph for what it needs, and should
        clear the graph content when this happens.
        """
        raise NotImplementedError

    def init_observe(self):
        """
        Send any required initialization observations to the player. Will
        only be called the first time this player is initialized.
        """
        raise NotImplementedError

    def is_alive(self):
        """
        Should be checking to see if connections are still maintained.
        Will be called once before the above two methods in every main loop
        of the running game.
        """
        raise NotImplementedError


class PlayerProvider:
    """
    A player provider is an API for adding new players into the game. It
    will be given opportunities to check for new players and should return
    an array of new players during these calls
    """

    def __init__(self, graphs: Dict[str, "OOGraph"]):
        # Graphs should be a map of game_ids to the associated game graph
        self.graphs = graphs

    def get_new_players(self):
        """
        Should check the potential source of players for new players. If
        a player exists, this should instantiate a relevant Player object
        for each potential new player and return them.
        """
        raise NotImplementedError


class GameInstance:
    """
    This class serves to create a wrapper around a specific graph and manage
    all of the agents on the inside. It accepts players in the form of a
    class that extends the Player class, which itself extends Agent. Players
    can come from any source.
    """

    def __init__(
        self,
        game_id: str,
        builder_config: "GraphBuilderConfig",
        world_config: "WorldConfig",
    ):
        self.world = None
        self.world_config = world_config
        self.builder_config = builder_config
        self.game_id = game_id
        self.players = []
        self.providers = []
        self.last_connection = time.time()

    @classmethod
    async def get(
        cls,
        game_id: str,
        builder_config: "GraphBuilderConfig",
        world_config: "WorldConfig",
    ) -> "GameInstance":
        instance = cls(
            game_id, builder_config=builder_config, world_config=world_config
        )
        await instance._init_world()
        return instance

    async def _init_world(self):
        # TODO pull appropriate builder from base GraphBuilder
        assert self.builder_config._builder == "MapJsonBuilder"
        world_builder = MapJsonBuilder(self.builder_config)
        _, self.world = await world_builder.get_graph(world_config=self.world_config)

    def fill_souls(self, model_pool: ModelPool):
        purgatory = self.world.purgatory
        if not model_pool.has_model(ModelTypeName.DIALOG):
            purgatory.register_filler_soul_provider("repeat", RepeatSoul, lambda: [])
        else:
            purgatory.register_filler_soul_provider(
                "model",
                GenerativeHeuristicModelSoul,
                lambda: [],
            )
        for empty_agent in self.world.oo_graph.agents.values():
            purgatory.fill_soul(empty_agent)

    def register_provider(self, provider):
        self.providers.append(provider)

    async def run_graph_step(self):
        world = self.world

        # Clear disconnected players
        left_players = [p for p in self.players if not p.is_alive()]
        for player in left_players:
            if player.player_soul is not None:
                node_to_clean = player.player_soul.target_node
                await self.world.purgatory.clear_soul(node_to_clean)
                self.world.purgatory.fill_soul(node_to_clean)
            self.players.remove(player)
            self.last_connection = time.time()

        # clear corpses and respawn
        ags = await self.world.clean_corpses_and_respawn()
        for ag in ags:
            self.world.purgatory.fill_soul(ag)


class TutorialInstance(GameInstance):
    """
    Version of the game meant to run tutorials, not for general play
    """

    def __init__(
        self,
        game_id,
        builder_config: "GraphBuilderConfig",
        world_config: "WorldConfig",
    ):
        self._created_time = time.time()
        super().__init__(
            game_id, builder_config=builder_config, world_config=world_config
        )
        self._should_shutdown = False
        self._did_complete = True

    async def _init_world(self):
        _, tutorial_world = await TutorialWorldBuilder(self.builder_config).get_graph(
            world_config=self.world_config
        )
        self.world = tutorial_world
        self._player_node = tutorial_world.oo_graph.find_nodes_by_name("You")[0]
        self._target_destination = tutorial_world.oo_graph.find_nodes_by_name(
            "Ethereal Mist"
        )[0]

    def fill_souls(self, model_pool: "ModelPool"):
        """Tutorials directly register the tutorial to the DM"""
        self.world.purgatory.register_filler_soul_provider(
            "tutorial",
            TutorialModelSoul,
            lambda: [],
        )
        dm_agent = list(self.world.oo_graph.agents.values())[1]
        assert dm_agent.name == "Dungeon Master", "Did not find DM!"
        self.world.purgatory.fill_soul(dm_agent, "tutorial")

    async def run_graph_step(self):
        await super().run_graph_step()
        self._did_complete = self._player_node.get_room() == self._target_destination
        self._should_shutdown = (
            len(self.players) == 0 and time.time() - self._created_time > 60
        )
