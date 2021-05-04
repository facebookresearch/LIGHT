#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.graph.events.base import (
    GraphEvent,
    ErrorEvent,
    ProcessedArguments,
    proper_caps_wrapper,
)

from light.graph.events.graph_events import DeathEvent, HealthEvent
from light.graph.events.use_triggered_events import (
    UseTriggeredEvent,
    BroadcastMessageEvent,
    CreateEntityEvent,
    ModifyAttributeEvent,
)
from light.graph.events.constraint import (
    IsHoldingConstraint,
    UsedWithAgentConstraint,
    UsedWithItemConstraint,
    InRoomConstraint,
    AttributeCompareValueConstraint,
)
from light.graph.elements.graph_nodes import GraphAgent, GraphNode, GraphObject
from typing import Union, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from light.world.world import World


class UseEvent(GraphEvent):
    """Handles using an object"""

    NAMES = ["use"]

    def __init__(
        self,
        actor: GraphAgent,
        target_nodes: Optional[List[GraphNode]] = None,
        text_content: Optional[str] = None,
        event_id: Optional[str] = None,
    ):
        super().__init__(
            actor,
            target_nodes=target_nodes,
            text_content=text_content,
            event_id=event_id,
        )
        self.events: Optional[List["UseTriggeredEvent"]] = None

    def satisfy_constraint(self, constraint, world):
        constraint_params = constraint.get("params", {})
        constraint_params["actor"] = self.actor

        if constraint["type"] == "is_holding":
            constraint_class = IsHoldingConstraint

        if constraint["type"] == "used_with_item_name":
            constraint_class = UsedWithItemConstraint

        if constraint["type"] == "used_with_agent":
            constraint_class = UsedWithAgentConstraint

        if constraint["type"] == "in_room":
            constraint_class = InRoomConstraint

        if constraint["type"] == "attribute_compare_value":
            constraint_class = AttributeCompareValueConstraint

        return constraint_class(self.target_nodes, constraint_params).satisfy(world)

    def satisfy_constraints(self, constraints, world):
        all_constraints_satisfied = True

        for constraint in constraints:
            if not self.satisfy_constraint(constraint, world):
                all_constraints_satisfied = False

        return all_constraints_satisfied

    def construct_events(self, events):
        constructed_events = []
        for event in events:
            if event["type"] == "modify_attribute":
                event_class = ModifyAttributeEvent

            if event["type"] == "create_entity":
                event_class = CreateEntityEvent

            if event["type"] == "broadcast_message":
                event_class = BroadcastMessageEvent

            constructed_events.append(
                event_class(
                    event.get("params", {}), self.actor, target_nodes=self.target_nodes
                )
            )
        return constructed_events

    def execute_events(self, events, world):
        for event in events:
            event.execute(world)

    def send_no_interaction_message(self, world):
        return BroadcastMessageEvent(
            {"self_view": "Nothing special seems to happen."}, self.actor
        ).execute(world)

    def on_use(self, world):
        use_node = self.target_nodes[0]

        if not hasattr(use_node, "on_use") and use_node.on_use is not None:
            # No on_use for this agent.
            return

        if self.events is not None:
            # Replayed events, no need to search
            if len(self.events) == 0:
                self.exit_message(world)
                self.found_use = False
            else:
                self.execute_events(self.events, world)
                self.found_use = True
            return

        # Find a use event if available
        self.found_use = False
        self.messages = {}
        on_uses = use_node.on_use

        for i in range(len(on_uses)):
            on_use = on_uses[i]

            constraints = on_use["constraints"]
            if self.satisfy_constraints(constraints, world):
                if not ("remaining_uses" in on_use):
                    # add missing field
                    on_use["remaining_uses"] = "inf"
                remaining_uses = on_use["remaining_uses"]
                if remaining_uses == "inf":
                    pass
                elif remaining_uses > 0:
                    self.target_nodes[0].on_use[i]["remaining_uses"] = (
                        remaining_uses - 1
                    )
                else:
                    # No remaining uses for this event, but may
                    # be others
                    continue
                self.events = self.construct_events(on_use["events"])
                self.found_use = True
                self.execute_events(self.events, world)
                break

        if not self.found_use:
            self.exit_message(world)

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, move the item from the actor to the other agent
        """
        assert not self.executed
        # Populate for views
        self.__actor_name = self.actor.get_prefix_view()
        put_target = self.target_nodes[0]
        self.__given_name = put_target.get_prefix_view()
        self.__recipient_name = self.target_nodes[1].get_prefix_view()

        self.on_use(world)
        world.broadcast_to_room(self)

        # Move the object over and broadcast
        # put_target.move_to(self.target_nodes[1])
        self.executed = True
        return []

    def to_canonical_form(self) -> str:
        """return action text for use"""
        return f"use {self._canonical_targets[0]} with {self._canonical_targets[1]}"

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""

        if not self.found_use:
            if viewer == self.actor:
                return "Nothing special seems to happen."
            else:
                return None

        actor_text = "you" if viewer == self.actor else self.__actor_name
        recipient_text = (
            "you" if viewer == self.target_nodes[1] else self.__recipient_name
        )
        text = ""
        assert self.events is not None, "Cannot have found use with no events"
        for event in self.events:
            new_text = event.get_view_component(viewer, actor_text, recipient_text)
            if new_text is not None:
                text += new_text

        if len(text) == 0:
            # Default message.
            return f"{actor_text} used {self.__given_name} with {recipient_text}."
        else:
            return text

    @classmethod
    def split_text_args(
        cls, actor: GraphAgent, text: str
    ) -> Union[List[List[str]], "ErrorEvent"]:
        """
        Return all possible interpretations for "use x with y".

        Must consider multiple to situations
        """
        possibilities = []
        possible_to_splits = text.split(" with ")
        for split_ind in range(len(possible_to_splits)):
            before = " with ".join(possible_to_splits[:split_ind])
            after = " with ".join(possible_to_splits[split_ind:])
            if len(after) > 0 and len(before) > 0:
                possibilities.append([before, after])

        if len(possibilities) == 0:
            return ErrorEvent(cls, actor, "You must use that with something.")

        return possibilities

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for an object within the actor, and another entity in the room (or being held).
        """
        assert len(text_args) == 2, f"GiveObjectEvent takes two args, got {text_args}"
        object_name, target_name = text_args
        target_nodes = graph.desc_to_nodes(target_name, actor, "all+here")
        possible_targets = [x for x in target_nodes if isinstance(x, GraphNode)]
        possible_targets.append(actor)
        if len(possible_targets) == 0:
            # didn't find any nodes by this name
            return ErrorEvent(
                cls,
                actor,
                f"You can't find '{target_name}' here that you can use.",
            )

        # check actor to see if they have the node to use
        target_nodes = graph.desc_to_nodes(object_name, actor, "carrying")
        applicable_nodes = [x for x in target_nodes if isinstance(x, GraphObject)]
        if len(applicable_nodes) > 0:
            # we found the thing!
            return ProcessedArguments(
                targets=[applicable_nodes[0], possible_targets[0]]
            )
        elif len(target_nodes) > 0:
            # we found a node, but it isn't the right one.
            guess_target = target_nodes[0]
            guess_target_name = guess_target.get_prefix_view()
            return ErrorEvent(
                cls,
                actor,
                f"{guess_target_name}, isn't something you can use.",
                [guess_target],
            )
        return ErrorEvent(cls, actor, f"You don't have '{object_name}' to use.")

    def exit_message(self, world):
        event = {
            "type": "broadcast_message",
            "params": {"self_view": "Nothing special seems to happen."},
        }
        events = self.construct_events([event])
        self.execute_events(events, world)

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["UseObjectEvent", "ErrorEvent"]:
        """use object events are mostly valid"""
        assert len(targets) == 2, f"UseObjectEvent takes two args, got {targets}"
        use_object, use_with = targets
        if not hasattr(use_object, "on_use") or use_object.on_use is None:
            return ErrorEvent(
                cls,
                actor,
                "Nothing special seems to happen.",
            )
        return cls(actor, target_nodes=[use_object, use_with], event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """
        Find all objects that can be used
        """
        valid_actions: List[GraphEvent] = []
        # get all the useable objects
        useable_objects = [
            x
            for x in actor.get_contents()
            if isinstance(x, GraphObject)
            and hasattr(x, "on_use")
            and x.on_use is not None
        ]
        if len(useable_objects) == 0:
            return []

        possible_targets_in_room = [
            x for x in actor.get_room().get_contents() if isinstance(x, GraphNode)
        ]
        possible_targets_holding = [
            x for x in actor.get_contents() if isinstance(x, GraphNode)
        ]
        possible_targets = possible_targets_in_room + possible_targets_holding
        # Try to use all objects on all other objects
        for obj in useable_objects:
            for entity in possible_targets:
                valid_actions.append(cls(actor, target_nodes=[obj, entity]))

        return valid_actions

    def post_json_load(self, world: "World") -> None:
        """Do a json load on the processed event array"""
        self.events = [
            GraphEvent.from_json(json_event, world) for json_event in self.events
        ]
