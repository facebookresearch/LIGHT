#!/usr/bin/env python3


# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.graph.events.graph_events import (
    GoEvent,
    HitEvent,
)
from light.world.souls.model_soul import ModelSoul
import random

from typing import TYPE_CHECKING


class BattleRoyaleSoul(ModelSoul):
    """
    Test soul that moves around and attacks. Useful for testing death
    and various death transitions
    """

    HAS_MAIN_LOOP = True
    MAIN_LOOP_TIMEOUT = 0.05

    def execute_valid_action(self):
        our_actions = self.world.get_possible_events(
            self.target_node.node_id, ["go", "hit"]
        )
        if len(our_actions) == 0:
            return
        action = random.choice(our_actions)
        action.execute(self.world)

    async def observe_event(self, event: "GraphEvent"):
        """
        BattleRoyaleSouls will hit whenever they can.
        """
        if event.actor == self.target_node:
            return
        if self.target_node.is_dying():
            return
        self.execute_valid_action()

    async def _take_timestep(self):
        if random.random() > 0.7:
            self.execute_valid_action()
