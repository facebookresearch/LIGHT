#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.graph.events.base import (
    GraphEvent,
    TriggeredEvent,
    proper_caps_wrapper,
)

from light.graph.events.graph_events import DeathEvent, HealthEvent
from light.graph.elements.graph_nodes import GraphAgent, GraphNode
from typing import List, Optional


class UseTriggeredEvent(TriggeredEvent):
    """Handles using an object"""

    def __init__(
        self,
        event_params,
        actor: GraphAgent,
        target_nodes: Optional[List[GraphNode]] = None,
    ):
        super().__init__(actor, target_nodes)
        self.event_params = event_params

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """UseTriggeredEvents should have text in the UseEvent"""
        return None

    def get_view_component(
        self, viewer: GraphAgent, actor_text: str, recipient_text: str
    ) -> Optional[str]:
        """UseTriggeredEvents can specify part of a view for a UseEvent"""
        return None


class BroadcastMessageEvent(UseTriggeredEvent):
    """Event to broadcast a message to the room the agent currently is inside"""

    def execute(self, world: "World") -> List[GraphEvent]:
        self.messages = self.event_params
        world.broadcast_to_room(self)

    @proper_caps_wrapper
    def get_view_component(
        self, viewer: GraphAgent, actor_text: str, recipient_text: str
    ) -> Optional[str]:
        """Parse out different view conditions"""
        if viewer == self.actor:
            s = ""
            if "self_view" in self.messages:
                s += self.messages["self_view"] + " "
            if (
                "self_as_target_view" in self.messages
                and viewer == self.target_nodes[1]
            ):
                s += str.format(self.messages["self_as_target_view"], **locals())
            if (
                "self_not_target_view" in self.messages
                and viewer != self.target_nodes[1]
            ):
                s += str.format(self.messages["self_not_target_view"], **locals())
            return s
        else:
            if (
                "self_not_target_view" in self.messages
                and viewer != self.target_nodes[1]
            ):
                return str.format(self.messages["self_not_target_view"], **locals())
            elif "room_view" in self.messages:
                return str.format(self.messages["room_view"], **locals())
        return None


class CreateEntityEvent(UseTriggeredEvent):
    """Event to create an entity in one of the objects involved on an use event"""

    def execute(self, world: "World") -> List[GraphEvent]:
        # creation location
        entity_event_type = self.event_params["type"]

        if entity_event_type == "in_used_item":
            location = self.target_nodes[0]
        if entity_event_type == "in_used_target_item":
            location = self.target_nodes[1]
        if entity_event_type == "in_room":
            location = self.target_nodes[1].get_room()
        if entity_event_type == "in_actor":
            location = self.actor

        world_graph = world.oo_graph
        n = world_graph.add_object(
            self.event_params["object"]["name"], self.event_params["object"]
        )
        n.force_move_to(location)

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        return None  # Broadcast messages cover the text here


class ModifyAttributeEvent(UseTriggeredEvent):
    """Event to modify the value of a certain attribute"""

    def execute(self, world: "World") -> List[GraphEvent]:
        if self.event_params["type"] == "in_used_target_item":
            target = self.target_nodes[1]

        key = self.event_params["key"]
        value = self.event_params["value"]

        if value.startswith("+"):
            value = float(value[1:])
            setattr(target, key, getattr(target, key) + value)
        elif value.startswith("-"):
            value = -float(value[1:])
            setattr(target, key, getattr(target, key) + value)
        elif value.startswith("="):
            value = float(value[1:])
            setattr(target, key, value)
        else:
            setattr(target, key, value)

        if key == "health":
            if target.health < 0:
                target.health = 0
            health = target.health
            if health == 0:
                DeathEvent(target).execute(world)
            else:
                HealthEvent(
                    target,
                    target_nodes=[self.actor, target],
                    text_content="HealthOnHitEvent",
                ).execute(world)

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        return None  # Broadcast messages cover the text here
