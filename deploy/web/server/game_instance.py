#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from light.graph.builders.starspace_all import StarspaceBuilder
from light.graph.builders.map_json_builder import MapJsonBuilder
from light.graph.builders.tutorial_builder import TutorialWorldBuilder
from light.world.souls.repeat_soul import RepeatSoul
from light.world.souls.models.generative_heuristic_model_soul import (
    GenerativeHeuristicModelSoul,
)
from light.world.souls.models.tutorial_model_soul import (
    TutorialModelSoul,
)

import os.path
import time
import asyncio

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from light.data_model.db.environment import EpisodeDB
    from light.world.world import WorldConfig

# TODO specify the models to be using
USE_MODELS = True


class Player:
    """
    A player in an instance of the light game. Maintains any required
    connections and IO such that the game doesn't need to worry about
    that stuff
    """

    def __init__(self, graph, player_id):
        self.g = graph
        self.id = player_id
        self.init_observe()

    def get_player_id(self):
        return self.id

    def get_agent_id(self):
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

    def __init__(self, graphs):
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
        game_id,
        ldb,  # TODO remove this DB
        g=None,
        opt=None,
        world_config: Optional["WorldConfig"] = None,  # TODO make this required
    ):
        self.world = None
        if g is not None:
            self.world = g

        self.world_config = world_config
        self.opt = opt
        self.db = ldb
        self.game_id = game_id
        self.players = []
        self.providers = []
        self.last_connection = time.time()

    @classmethod
    async def get(
        cls,
        game_id,
        ldb,  # TODO remove this DB
        g=None,
        opt=None,
        world_config: Optional["WorldConfig"] = None,  # TODO make this required
    ) -> "GameInstance":
        instance = cls(game_id, ldb, g=g, opt=opt, world_config=world_config)
        await instance._init_world()
        return instance

    async def _init_world(self):
        if self.opt["builder_model"] is not None:
            _, self.world = await StarspaceBuilder(
                self.ldb,
                debug=False,
                opt=self.world_config.opt,
            ).get_graph()  # TODO: what are the args that are needed
        else:
            self.world_config.opt["load_map"] = os.path.expanduser(
                "~/LIGHT/scripts/examples/complex_world.json"
            )
            world_builder = MapJsonBuilder(
                episode_db=self.world_config.episode_db, opt=self.world_config.opt
            )
            _, self.world = await world_builder.get_graph(
                world_config=self.world_config
            )

    def fill_souls(self, FLAGS, model_resources):
        purgatory = self.world.purgatory
        if len(FLAGS.dialog_model_opt_file) <= 3:
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
        ldb,
        g=None,
        opt=None,
        world_config: Optional["WorldConfig"] = None,
    ):
        self.db = ldb
        self._created_time = time.time()
        super().__init__(game_id, ldb, opt=opt, world_config=world_config)
        self._should_shutdown = False
        self._did_complete = True

    async def _init_world(self):
        _, tutorial_world = await TutorialWorldBuilder(
            self.db,
            opt=self.world_config.opt,
        ).get_graph(world_config=self.world_config)
        self.world = tutorial_world
        self._player_node = tutorial_world.oo_graph.find_nodes_by_name("You")[0]
        self._target_destination = tutorial_world.oo_graph.find_nodes_by_name(
            "Ethereal Mist"
        )[0]

    async def _init_world():
        _, self.world = await TutorialWorldBuilder(self.db, self.opt).get_graph()

    def fill_souls(self, _FLAGS, model_resources):
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
