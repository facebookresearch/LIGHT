# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.graph.events.graph_events import EmoteEvent, SayEvent
from light.world.souls.soul import Soul
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.graph.world.world import World
    from light.graph.events.base import GraphEvent


class RepeatSoul(Soul):
    """
    The simplest of Souls, it responds to all events by saying what it saw
    """

    def __init__(self, target_node: "GraphAgent", world: "World"):
        """
        RepeatSouls (currently) just initialize normally on a node and world
        """
        super().__init__(target_node, world)

    async def observe_event(self, event: "GraphEvent"):
        """
        RepeatSouls do very little beyond saying what they observed, and smiling
        for good measure.
        """
        if event.actor == self.target_node:
            return
        if not (event.actor.is_player):
            return
        if self.target_node.is_dying():
            return  # Going to die, can't do anything
        my_observation = event.view_as(self.target_node)
        repeat_text = f"I just saw the following: {my_observation}"
        repeat_event = SayEvent.construct_from_args(
            self.target_node, targets=[], text=repeat_text
        )
        repeat_event.execute(self.world)
        creepy_smile = EmoteEvent.construct_from_args(
            self.target_node, targets=[], text="smile"
        )
        creepy_smile.execute(self.world)
