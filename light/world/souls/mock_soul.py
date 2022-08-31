#!/usr/bin/env python3

from light.world.souls.soul import Soul
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.world.world import World
    from light.graph.events.base import GraphEvent


class MockSoul(Soul):
    """
    A Soul for use in testing
    """

    def __init__(self, target_node: "GraphAgent", world: "World"):
        """
        MockSouls are created for test cases to take actions
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
        MockSouls do very little beyond saying what they observed, and smiling
        for good measure.
        """
        self.observations.append(event)

    async def reap(self):
        """
        MockSouls don't have any extra resources, and thus don't need to clean up.
        """
        await super().reap()
