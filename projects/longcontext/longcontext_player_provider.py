#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.world.player_provider import PlayerProvider

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from light.world.souls.player_soul import PlayerSoul
    from light.world.purgatory import Purgatory


class LongcontextPlayerProvider(PlayerProvider):
    """
    LongcontextPlayerProviders exist to create a single player to interact
    with a local graph via a longcontext script.
    """

    def __init__(self, purgatory: "Purgatory"):
        """
        LongcontextPlayerProviders only keep track of one player at most.
        """
        self.player_soul: Optional["PlayerSoul"] = None
        self.purgatory = purgatory
        self.obs_cnt = 0
        
    def process_longcontext_act(self, text: str):
        if self.obs_cnt <= 0:
            self.obs_cnt += 1
            #print("act", str(self.obs_cnt), text)
        if text != "":
            print("action> " + text)
        if self.player_soul is not None and self.player_soul.is_reaped:
            print("Your soul detaches from the world, lost...")
            self.player_soul = None
        if self.player_soul is None:
            print("Your soul searches for a character to inhabit")
            self.purgatory.get_soul_for_player(self)
            if self.player_soul is None:
                print("No soul could be found for you :(")
            else:
                self.player_soul.handle_act("look")
            return
        player_agent = self.player_soul.handle_act(text)

    def register_soul(self, soul: "PlayerSoul"):
        """Save the soul as a local player soul"""
        self.player_soul = soul

    def player_observe_event(self, soul: "PlayerSoul", event: "GraphEvent"):
        """
        Send observation forward to the player in whatever format the player
        expects it to be.
        """
        view = event.view_as(soul.target_node)
        if view is not None:
            print(
                "\r" + event.view_as(soul.target_node).strip()
            )
            if self.obs_cnt > 0:
                self.obs_cnt -= 1
                #print("observe", str(self.obs_cnt), str(event))
                
            