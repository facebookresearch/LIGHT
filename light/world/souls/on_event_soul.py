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


class OnEventSoul(Soul):
    """
    The simplest of Souls, it responds to all events by saying what it saw
    """

    def __init__(self, target_node: "GraphAgent", world: "World"):
        """
        OnEventSouls (currently) just initialize normally on a node and world
        """
        super().__init__(target_node, world)

    def on_events(self, event):
        if not hasattr(self.target_node, 'on_events'):
            # No on_events for this agent.
            return
        event_name = event.__class__.__name__
        on_events = self.target_node.on_events
        for on_event in on_events:
            cause = on_event[0]
            effect = on_event[1]
            if event_name == cause[0]:
                if event_name == 'SayEvent':
                    if cause[1] in event.text_content:
                        do_text = effect[1]
                        do_event = SayEvent.construct_from_args(
                            self.target_node, targets=[], text=do_text
                        )
                        do_event.execute(self.world)
        
        
    async def observe_event(self, event: "GraphEvent"):
        """
        OnEventSouls check for specific events, that trigger specific actions.
        """
        if event.actor == self.target_node:
            return
        self.on_events(event)
