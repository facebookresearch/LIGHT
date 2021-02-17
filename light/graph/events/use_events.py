from light.graph.events.base import (
    GraphEvent,
    ErrorEvent,
    TriggeredEvent,
    ProcessedArguments,
    proper_caps,
)

from light.graph.events.graph_events import DeathEvent

from light.graph.elements.graph_nodes import GraphAgent, GraphNode, GraphObject

from typing import Union, List, Optional


class PostconditionEvent(GraphEvent):
    """Handles using an object"""

    def __init__(
        self,
        post_condition,
        actor: GraphAgent,
        target_nodes: Optional[List[GraphNode]] = None,
        text_content: Optional[str] = None,
    ):
        super().__init__(actor, target_nodes, text_content)
        self.post_condition = post_condition


class BroadcastMessageEvent(PostconditionEvent):
    def execute(self, world: "World") -> List[GraphEvent]:
        self.messages = self.post_condition["params"]
        self.__msg_txt = self.messages["self_view"]
        world.broadcast_to_room(self)

    @proper_caps
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__msg_txt
        else:
            return None


class CreateEntityEvent(PostconditionEvent):
    def execute(self, world: "World") -> List[GraphEvent]:
        # creation location
        entity_event_type = self.post_condition["params"]["type"]

        if entity_event_type == "in_used_item":
            location = self.target_nodes[0]
        if entity_event_type == "in_used_target_item":
            location = self.target_nodes[1]
        if entity_event_type == "in_room":
            location = self.target_nodes[1].get_room()
        if entity_event_type == "in_actor":
            location = self.actor

        world_graph = world.oo_graph
        event_object = self.post_condition["params"]["object"]
        n = world_graph.add_object(event_object["name"], event_object)
        n.force_move_to(location)

    @proper_caps
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__msg_txt
        else:
            return None


class ModifyAttributeEvent(PostconditionEvent):
    def execute(self, world: "World") -> List[GraphEvent]:
        if self.post_condition["params"]["type"] == "in_used_target_item":
            target = self.target_nodes[1]

        key = self.post_condition["params"]["key"]
        value = self.post_condition["params"]["value"]

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

    @proper_caps
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__msg_txt
        else:
            return None


class UseEvent(GraphEvent):
    """Handles using an object"""

    NAMES = ["use"]

    def satisfy_constraint(self, constraint, world):
        if constraint[0] == "is_holding" and constraint[1] == "used_item":
            # Check if actor is holding the useable item.
            return self.target_nodes[0].get_container() == self.actor

        if constraint[0] == "used_with_item_name":
            # Check if the useable item is used with the given object.
            return constraint[1] == self.target_nodes[1].name

        if constraint[0] == "used_with_agent":
            # Check if the target is an agent
            return self.target_nodes[1].agent

        return True

    def satisfy_constraints(self, constraints, world):
        all_constraints_satisfied = True

        for constraint in constraints:
            if not self.satisfy_constraint(constraint, world):
                all_constraints_satisfied = False

        return all_constraints_satisfied

    def execute_events(self, events, world):
        for event in events:
            if event["type"] == "modify_attribute":
                ModifyAttributeEvent(
                    event,
                    self.actor,
                    target_nodes=self.target_nodes,
                    text_content="ModifyAttributeEvent",
                ).execute(world)

            if event["type"] == "create_entity":
                CreateEntityEvent(
                    event,
                    self.actor,
                    target_nodes=self.target_nodes,
                    text_content="CreateEntityEvent",
                ).execute(world)

            if event["type"] == "broadcast_message":
                BroadcastMessageEvent(
                    event,
                    self.actor,
                    target_nodes=self.target_nodes,
                    text_content="BroadcastMessageEvent",
                ).execute(world)

    def on_use(self, world):
        use_node = self.target_nodes[0]

        if not hasattr(use_node, "on_use") and use_node.on_use is not None:
            # No on_use for this agent.
            return

        self.found_use = False
        self.messages = {}
        on_uses = use_node.on_use

        for on_use in on_uses:
            constraints = on_use["constraints"]
            if self.satisfy_constraints(constraints, world):
                events = on_use["events"]
                self.found_use = True
                self.execute_events(events, world)
                break

        if not self.found_use:
            BroadcastMessageEvent(
                {
                    "type": "broadcast_message",
                    "params": {"self_view": "Nothing special seems to happen."},
                },
                self.actor,
                target_nodes=None,
                text_content="BroadcastMessageEvent",
            ).execute(world)

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

        # Move the object over and broadcast
        # put_target.move_to(self.target_nodes[1])
        # world.broadcast_to_room(self)
        self.executed = True
        return []

    def to_canonical_form(self) -> str:
        """return action text for use"""
        return f"use {self._canonical_targets[0]} with {self._canonical_targets[1]}"

    @proper_caps
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""

        if not self.found_use:
            if viewer == self.actor:
                return "Nothing special seems to happen."
            else:
                return

        actor_text = self.__actor_name
        recipient_text = self.__recipient_name

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
                and viewer == self.target_nodes[1]
            ):
                return str.format(self.messages["self_not_target_view"], **locals())
            elif "room_view" in self.messages:
                return str.format(self.messages["room_view"], **locals())

        # Default message.
        if viewer == self.target_nodes[1]:
            recipient_text = "you"
        return f"{actor_text} used {self.__given_name} with {recipient_text}."

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

    @classmethod
    def construct_from_args(
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
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
        return cls(actor, target_nodes=[use_object, use_with])

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
