#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.graph.events.graph_events import (
    EmoteEvent,
    SayEvent,
    DropObjectEvent,
    HitEvent,
    BlockEvent,
)
from light.world.souls.soul import Soul
from light.world.souls.model_soul import ModelSoul
from typing import TYPE_CHECKING

import math
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
        if cause[0] == event_name or (
            cause[0] == "SayEvent" and event_name == "TellEvent"
        ):
            if cause[0] == "SayEvent":
                if cause[1] in event.text_content and event.safe:
                    return True
        return False

    def execute_event(self, effect):
        agent = self.target_node
        if effect[0] == "BlockEvent":
            do_event = BlockEvent.construct_from_args(agent, targets=[effect[1]])
            if do_event.__class__.__name__ != "ErrorEvent":
                do_event.execute(self.world)
        if effect[0] == "HitEvent":
            do_event = HitEvent.construct_from_args(agent, targets=[effect[1]])
            if do_event.__class__.__name__ != "ErrorEvent":
                do_event.execute(self.world)
        if effect[0] == "SayEvent":
            do_text = effect[1]
            do_event = SayEvent.construct_from_args(agent, targets=[], text=do_text)
            if do_event.__class__.__name__ != "ErrorEvent":
                do_event.execute(self.world)
        if effect[0] == "EmoteEvent":
            do_event = EmoteEvent.construct_from_args(agent, targets=[], text=effect[1])
            if do_event.__class__.__name__ != "ErrorEvent":
                do_event.execute(self.world)
        if effect[0] == "DropEvent":
            do_event = DropObjectEvent.construct_from_args(agent, effect[1])
            if do_event.__class__.name != "ErrorEvent":
                do_event.execute(self.world)

    def on_events_heuristics(self, event):
        agent = self.target_node
        event_name = event.__class__.__name__

        # HitEvent
        if (
            event_name == "HitEvent"
            and event.target_nodes[0] == agent
            and agent.aggression >= -1
        ):
            other_agent = event.actor
            self.execute_event(["BlockEvent", other_agent])  # block!
            self.execute_event(["HitEvent", other_agent])  # hit back!
            agent.aggression_target = other_agent.node_id

        # StealEvent
        if (
            event_name == "StealObjectEvent"
            and event.target_nodes[1] == agent
            and agent.aggression >= 0
        ):
            other_agent = event.actor
            self.execute_event(["BlockEvent", other_agent])  # block!
            self.execute_event(["HitEvent", other_agent])  # hit back!
            agent.aggression_target = other_agent.node_id

        # GiveObjectEvent
        if event_name == "GiveObjectEvent" and event.target_nodes[1] == agent:
            if agent.dont_accept_gifts:
                obj = event.target_nodes[0]
                self.execute_event(["DropEvent", obj])
                say_text = "I don't want that."
            else:
                say_text = "Err.. thanks."
            self.execute_event(["SayEvent", say_text])

    def on_events(self, event):
        self.on_events_heuristics(event)

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
        # if event.actor ! and !== self.target_node:
        #    return
        self.on_events(event)

    def is_too_far(self, agent, room):
        # Check if it's too far from agent's starting room
        if not hasattr(agent, "start_loc"):
            agent.start_loc = agent.get_room().grid_location
        target_loc = room.grid_location
        dist = 0
        for i in range(0, 3):
            dist += math.pow(target_loc[i] - agent.start_loc[i], 2)
        dist = math.sqrt(dist)
        if dist < agent.max_distance_from_start_location:
            return False
        else:
            return True

    def aggressive_towards(self, other_agent):
        agro_tags = self.target_node.attack_tagged_agents
        target_tags = other_agent.tags
        for agro_tag in agro_tags:
            if agro_tag.startswith("!"):
                agro_tag = agro_tag[1:]
                agro = True
                for target_tag in target_tags:
                    if target_tag == agro_tag:
                        agro = False
                if agro:
                    return True
            else:
                for target_tag in target_tags:
                    if target_tag == agro_tag:
                        return True
        return False

    async def _take_timestep(self) -> None:
        """
        Attempt to take some actions based on any observations in the pending list
        """
        graph = self.world.oo_graph
        agent = self.target_node
        agent_id = agent.node_id

        # Attack if we have an aggression target
        if hasattr(agent, "aggression_target"):
            target_id = agent.aggression_target
            target_agent = graph.get_node(target_id)
            if target_agent is not None:
                target_room = target_agent.get_room()
                if agent.get_room() == target_room:
                    self.execute_event(["HitEvent", target_agent])
                    return

        # Search room for aggression targets.
        hit_tags = agent.attack_tagged_agents
        if len(hit_tags) > 0:
            hit_events = self.world.get_possible_events(agent_id, use_actions=["hit"])
            if len(hit_events) > 0:
                for event in hit_events:
                    other_agent = event.target_nodes[0]
                    if self.aggressive_towards(other_agent):
                        self.execute_event(["EmoteEvent", "scream"])
                        self.execute_event(["BlockEvent", other_agent])
                        self.execute_event(["HitEvent", other_agent])
                        agent.aggression_target = other_agent.node_id
                        return

        # Random movement for NPCs..
        if random.randint(0, 100) < agent.speed:
            go_events = self.world.get_possible_events(agent_id, use_actions=["go"])
            room = go_events[0].target_nodes[0].get_room()
            if len(go_events) > 0 and not self.is_too_far(agent, room):
                go_event = random.choice(go_events)
                go_event.execute(self.world)
        return
