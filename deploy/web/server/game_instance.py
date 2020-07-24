#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
import asyncio
from light.graph.builders.starspace_all import (
    StarspaceBuilder,
)
from parlai.utils.misc import Timer
from light.world.world import World
from tornado.ioloop import IOLoop
from light.world.souls.repeat_soul import RepeatSoul
import time

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

    def __init__(self, game_id, ldb, g=None,):
        if g is None:
            _, world = StarspaceBuilder(ldb,
                debug=False
            ).get_graph()  # TODO: what are the args that are needed
            self.g = world
        else:
            self.g = g
        self.g.web = True
        purgatory = self.g.purgatory
        purgatory.register_filler_soul_provider("repeat", RepeatSoul, lambda: [])
        for empty_agent in self.g.oo_graph.agents.values():
            purgatory.fill_soul(empty_agent)
        self.game_id = game_id
        self.players = []
        self.providers = []
        self.last_connection = time.time()

    def register_provider(self, provider):
        self.providers.append(provider)

    def run_graph_step(self):
        g = self.g
        
        # Clear disconnected players
        left_players = [p for p in self.players if not p.is_alive()]
        for player in left_players:
            if player.player_soul is not None:
                self.g.purgatory.clear_soul(player.player_soul.target_node)
            self.players.remove(player)
            self.last_connection = time.time()

        # run npcs
        g.update_world()
