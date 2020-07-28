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


class TestSoul(Soul):
    """
    A Soul for use in testing
    """

    def __init__(self, target_node: "GraphAgent", world: "World"):
        """
        TestSouls are created for test cases to take actions
        and report observations
        """
        super().__init__(target_node, world)
        self.observations = []

    def do_act(self, event):
        """
        Handle executing an act on the given world
        """
        event.execute(self.world)

    async def observe_event(self, event: "GraphEvent"):
        """
        TestSouls do very little beyond saying what they observed, and smiling
        for good measure.
        """
        self.observations.append(event)

    def reap(self):
        """
        TestSouls don't have any extra resources, and thus don't need to clean up.
        """
        super().reap()
