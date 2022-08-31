#!/usr/bin/env python3


# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from light.world.souls.player_soul import PlayerSoul
    from light.world.world import World


class PlayerProvider:
    """
    A PlayerProvider defines the interface by which some external surface
    can provide a link between an actual human player and a PlayerSoul
    inside of the game. By defining the following methods, arbitrary
    providers can be written for different use cases.

    Any running game can then use `Purgatory.get_soul_for_player` to
    attach a player to a world.
    """

    @abstractmethod
    def register_soul(self, soul: "PlayerSoul"):
        """
        Do whatever bookkeeping is required to keep track of the given PlayerSoul
        such that other required methods operate properly, especially such that
        the player will be able to act in the world.
        """
        pass

    @abstractmethod
    def player_observe_event(self, soul: "PlayerSoul", event: "GraphEvent"):
        """
        Send observation forward to the player in whatever format the player
        expects it to be.
        """
        pass

    def get_objective(self, soul: "PlayerSoul", world: "World"):
        """
        Get an objective for the current sould to complete in the world
        """
        return None
