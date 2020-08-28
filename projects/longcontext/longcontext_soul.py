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


class LongcontextSoul(Soul):
    """
    The simplest of Souls, it responds to all events by saying what it saw
    """

    def __init__(self, target_node: "GraphAgent", world: "World"):
        """
        LongcontextSouls (currently) just initialize normally on a node and world
        """
        super().__init__(target_node, world)
        print("longinit")
        
    def match_event(self, event, cause):
        event_name = event.__class__.__name__
        if cause[0] == event_name:
            if event_name == "SayEvent":
                if cause[1] in event.text_content and event.safe:
                    return True
        return False

    def execute_event(self, effect):
        if effect[0] == "SayEvent":
            do_text = effect[1]
            do_event = SayEvent.construct_from_args(
                self.target_node, targets=[], text=do_text
            )
            do_event.execute(self.world)
        if effect[0] == "EmoteEvent":
            do_event = EmoteEvent.construct_from_args(
                self.target_node, targets=[], text=effect[1]
            )
            do_event.execute(self.world)

    def on_events(self, event):
        if not hasattr(self.target_node, "on_events"):
            # No on_events for this agent.
            return
        event_name = event.__class__.__name__
        on_events = self.target_node.on_events
        for on_event in on_events:
            cause = on_event[0]
            effect = on_event[1]
            if self.match_event(event, cause):
                self.execute_event(effect)

    def handle_act(self, act_text):
        self.world.parse_exec(self.target_node.node_id, act_text)        
        view = event.view_as(soul.target_node)
        
    async def observe_event(self, event: "GraphEvent"):
        """
        LongcontextSouls check for specific events, that trigger specific actions.
        """
        print("ho!")
        if event.actor == self.target_node:
            return
        self.on_events(event)
