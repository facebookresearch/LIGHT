#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.graph.events.graph_events import EmoteEvent, SayEvent
from light.world.souls.soul import Soul
from light.world.souls.model_soul import ModelSoul
from typing import TYPE_CHECKING

import random

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.graph.world.world import World
    from light.graph.events.base import GraphEvent


class OnEventSoul(ModelSoul):
    """
    The simplest of Souls, it responds to all events by saying what it saw
    """

    HAS_MAIN_LOOP = True
    MAIN_LOOP_STEP_TIMEOUT = 1
    
    def match_event(self, event, cause):
        event_name = event.__class__.__name__
        if cause[0] == event_name  or (cause[0] == "SayEvent" and event_name == "TellEvent"):
            if cause[0] == "SayEvent":
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

    async def observe_event(self, event: "GraphEvent"):
        """
        OnEventSouls check for specific events, that trigger specific actions.
        """
        if event.actor == self.target_node:
            return
        self.on_events(event)


    async def _take_timestep(self) -> None:
        """
        Attempt to take some actions based on any observations in the pending list
        """
        graph = self.world.oo_graph
        agent = self.target_node
        agent_id = agent.node_id
        
        # random movement for npcs..
        if True: #random.randint(0, 10) < agent.speed:
            go_events = self.world.get_possible_events(agent_id, use_actions=["go"])
            if len(go_events) > 0:
                go_event = random.choice(go_events)
                go_event.execute(self.world)
        return
