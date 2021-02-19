#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.graph.events.base import (
    GraphEvent,
    TriggeredEvent,
    proper_caps,
)

from light.graph.events.graph_events import DeathEvent
from light.graph.elements.graph_nodes import GraphAgent, GraphNode
from typing import List, Optional


class UseTriggeredEvent(TriggeredEvent):
    """Handles using an object"""

    def __init__(
        self,
        event_params,
        actor: GraphAgent,
        target_nodes: Optional[List[GraphNode]] = None,
        text_content: Optional[str] = None,
    ):
        super().__init__(actor, target_nodes, text_content)
        self.event_params = event_params

    @proper_caps
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__msg_txt
        else:
            return None


class BroadcastMessageEvent(UseTriggeredEvent):
    def execute(self, world: "World") -> List[GraphEvent]:
        self.messages = self.event_params
        self._UseTriggeredEvent__msg_txt = self.messages["self_view"]
        world.broadcast_to_room(self)


class CreateEntityEvent(UseTriggeredEvent):
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


class ModifyAttributeEvent(UseTriggeredEvent):
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
