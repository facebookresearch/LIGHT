#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.world.souls.soul import Soul

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.graph.world.world import World
    from light.graph.events.base import GraphEvent

class PlayerSoul(Soul):
    """
    A PlayerSoul is responsible for interfacing with the players in the
    game via a PlayerProvider, and will handle incoming messages
    from there and forward observations out.
    """
    
    def __init__(self, target_node: "GraphAgent", world: "World", player_id: str, provider=None):
        """
        PlayerSouls register to a GraphAgent in a World, but also keep track of the
        current player. They interface with the human through the provider
        """
        super().__init__(target_node, world)
        target_node.is_player = True
        self.player_id = player_id
        self.provider = provider # TODO link with real provider
        provider.register_soul(self)

    def handle_act(self, act_text):
        """
        PlayerSouls must process act text sent from players and enact them on the world.
        This method is called by the player provider when an action is taken.
        """
        # self.world.parse_exec(act_text)
        # send error event to player if necessary?
        pass

    def observe_event(self, event: "GraphEvent"):
        """
        PlayerSouls pass their observation along to the provider, who will handle getting the
        correct format to send to the view.
        """
        # provider.observe_event(self, event)
        pass
        

    def reap(self):
        """
        PlayerSouls must remove the player flag from their target GraphAgent when removed.
        """
        self.target_node.is_player = False
        self.provider.on_reap_soul(self)