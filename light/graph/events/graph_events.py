#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.graph.events.base import (
    GraphEvent,
    ErrorEvent,
    TriggeredEvent,
    NoArgumentEvent,
    ProcessedArguments,
    proper_caps,
    proper_caps_wrapper,
)

from light.world.utils.json_utils import (
    create_agent_tree,
    GraphEncoder,
)

import emoji
import random
import time
import math
import json

# Used for typehinting
from typing import Union, Dict, List, Optional, Tuple, Any, Type, TYPE_CHECKING
from light.graph.elements.graph_nodes import (
    GraphNode,
    GraphAgent,
    GraphObject,
    GraphRoom,
    LockEdge,
)

if TYPE_CHECKING:
    from light.registry.model_pool import ModelPool
    from light.world.world import World
    from light.graph.structured_graph import OOGraph


def split_in_list(text_list: List[str]) -> List[str]:
    """Return all of the individual words used in the text list"""
    vocab = set()
    for elem in text_list:
        vocab.update(elem.split())
    return list(vocab)


# TODO remove ability to take actions with yourself


class SystemMessageEvent(TriggeredEvent):
    """Event to send text messages to specified agents outside of other events"""

    def __init__(
        self,
        actor: GraphAgent,
        target_nodes: Optional[List[GraphNode]] = None,
        text_content: Optional[str] = None,
        event_id: Optional[str] = None,
        event_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            actor,
            target_nodes=target_nodes,
            text_content=text_content,
            event_id=event_id,
        )
        self.event_data = event_data

    def execute(self, world: "World") -> List[GraphEvent]:
        """Message to the target agent"""
        world.broadcast_to_agents(self, agents=[self.actor])
        return []

    def to_frontend_form(self, viewer: "GraphAgent") -> Dict[str, Any]:
        frontend_form = super().to_frontend_form(viewer)
        frontend_form["event_data"] = self.event_data
        return frontend_form

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Only the target actor should be able to see this message"""
        if viewer == self.actor:
            return self.text_content
        else:
            return None


class SpeechEvent(GraphEvent):
    """Base speaking class mostly to handle dialogue safety."""

    def __init__(
        self,
        actor: GraphAgent,
        target_nodes: Optional[List[GraphNode]] = None,
        text_content: Optional[str] = None,
        event_id: Optional[str] = None,
        safe: Optional[bool] = True,
    ):
        super().__init__(
            actor,
            target_nodes=target_nodes,
            text_content=text_content,
            event_id=event_id,
        )
        # Give opportunity to skip the safety after initialization
        # for debug reasons
        self.skip_safety = False
        self.safe = safe

    def is_dialogue_safe(self, text):
        return self.safe


class SayEvent(SpeechEvent):
    """Handles saying something out loud to the room."""

    NAMES = ["say"]
    TEMPLATES = ['say "<SOMETHING>"']

    def execute(self, world: "World") -> List[GraphEvent]:
        """On execution, store the expected views, then broadcast"""
        assert not self.executed
        actor_name = self.actor.get_prefix_view()
        if self.skip_safety or self.is_dialogue_safe(self.text_content):
            self.__in_room_view = f'{actor_name} said "{self.text_content}"'
            self.__self_view = None
        else:
            self.__in_room_view = f"{actor_name} mumbled something incomprehensible."
            self.__self_view = "You mumble something incomprehensible."
        world.broadcast_to_room(self, exclude_agents=[self.actor])
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__self_view
        else:
            return self.__in_room_view

    def to_canonical_form(self) -> str:
        """
        Provide the text that this event's actor would use to invoke this event
        """
        return f'say "{self.text_content}"'

    @classmethod
    def split_text_args(cls, actor: GraphAgent, text: str) -> List[List[str]]:
        """Anything after the "say" would be what is being said"""
        base_text = text.strip()
        if base_text.startswith('"') and base_text.endswith('"'):
            base_text = base_text[1:-1]
        return [[base_text]]

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["SayEvent", "ErrorEvent"]:
        """Say events are valid as long as there is text, otherwise fail."""
        if text is None or len(text.strip()) == 0:
            return ErrorEvent(cls, actor, "Say what? You have to say something!")
        text = text.strip()
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        return cls(actor, text_content=text, event_id=event_id)

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "mumble", "mumbled", "something", "incomprehensible", "said"]


def distance_and_direction(node1, node2):
    node1_loc = node1.get_room().grid_location
    node2_loc = node2.get_room().grid_location
    dist = 0
    for i in range(0, 3):
        dist += math.pow(node2_loc[i] - node1_loc[i], 2)
        dist = math.sqrt(dist)
    direction_string = ""
    if node1_loc[1] > node2_loc[1]:
        direction_string = "north"
    if node1_loc[1] < node2_loc[1]:
        direction_string = "south"
    if node1_loc[0] > node2_loc[0]:
        direction_string += "west"
    if node1_loc[0] < node2_loc[0]:
        direction_string += "east"
    return dist, direction_string


class ShoutEvent(SpeechEvent):
    """Handles saying something out loud to all agents."""

    NAMES = ["shout"]
    TEMPLATES = ['shout "<SOMETHING>"']

    def execute(self, world: "World") -> List[GraphEvent]:
        """On execution, store the view for the event"""
        assert not self.executed
        self.actor_name = self.actor.get_prefix_view()
        if self.is_dialogue_safe(self.text_content):
            self.__in_room_view = f'{self.actor_name} shouted "{self.text_content}"'
            self.__self_view = None
        else:
            self.__in_room_view = (
                f"{self.actor_name} shouted something incomprehensible."
            )
            self.__self_view = "You shout something incomprehensible."
        self.__in_room_view = f'{self.actor_name} shouted "{self.text_content}"'
        world.broadcast_to_all_agents(self)  # , exclude_agents=[self.actor])
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__self_view
        else:
            dist, direction = distance_and_direction(viewer, self.actor)
            if dist > 4:
                # Further than max shout distance.
                return None
            if dist == 0:
                return self.__in_room_view
            else:
                return f'"You hear {self.actor_name} shout from the {direction}: "{self.text_content}"'

    def to_canonical_form(self) -> str:
        """
        Provide the text that this event's actor would use to invoke this event
        """
        return f'shout "{self.text_content}"'

    @classmethod
    def split_text_args(cls, actor: GraphAgent, text: str) -> List[List[str]]:
        """Anything after the "shout" would be what is being said"""
        base_text = text.strip()
        if base_text.startswith('"') and base_text.endswith('"'):
            base_text = base_text[1:-1]
        return [[base_text]]

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["ShoutEvent", "ErrorEvent"]:
        """Shout events are valid as long as there is text, otherwise fail."""
        if text is None or len(text) == 0:
            return ErrorEvent(cls, actor, "Shout what? You have to shout something!")
        text = text.strip()
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        return cls(actor, text_content=text, event_id=event_id)

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return [
            "you",
            "shout",
            "something",
            "incomprehensible",
            "shouted",
            "hear",
            "from",
            "the",
            "north",
            "south",
            "east",
            "west",
        ]


class WhisperEvent(SpeechEvent):
    """Handles saying something to a specific agent without others hearing."""

    NAMES = ["whisper"]
    TEMPLATES = ['whisper "<SOMETHING>" to <agent>']

    def execute(self, world: "World") -> List[GraphEvent]:
        """On execution, store the views for the event, then broadcast"""
        assert not self.executed
        actor_name = self.actor.get_prefix_view()
        target_name = self.target_nodes[0].get_prefix_view()
        self.__in_room_view = f"{actor_name} whispered something to {target_name}"
        if self.is_dialogue_safe(self.text_content):
            self.__target_view = f'{actor_name} whispered "{self.text_content}" to you'
            self.__self_view = None
        else:
            self.__target_view = (
                f"{actor_name} whispered something incomprehensible to you"
            )
            self.__self_view = (
                f"You mumble something incomprehensible to {target_name}."
            )

        # broadcast
        world.broadcast_to_room(self, exclude_agents=[self.actor])
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__self_view
        elif viewer == self.target_nodes[0]:
            return self.__target_view
        else:
            return self.__in_room_view

    def to_canonical_form(self) -> str:
        """
        Provide the text that this event's actor would use to invoke this event
        """
        return f'whisper {self._canonical_targets[0]} "{self.text_content}"'

    @classmethod
    def split_text_args(
        cls, actor: GraphAgent, text: str
    ) -> Union[List[List[str]], ErrorEvent]:
        """Format is whisper <target> "words being whispered"."""
        if '"' not in text:
            return ErrorEvent(
                cls,
                actor,
                "If you're trying to speak to someone, you must use quotes around what you're saying.",
            )
        text_split = text.split('"')
        target_name = text_split[0]
        spoken_text = '"'.join(text_split[1:-1])
        return [[target_name.strip(), spoken_text]]

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - the node for
        target_name should be an agent
        """
        assert len(text_args) == 2, f"Incorrect number of arguments for WhisperEvent"
        target_name, text_content = text_args
        target_nodes = graph.desc_to_nodes(target_name, actor, "sameloc+players")
        applicable_nodes = [x for x in target_nodes if x.agent]
        if len(applicable_nodes) > 0:
            return ProcessedArguments(targets=[applicable_nodes[0]], text=text_content)
        elif len(target_nodes) > 0:
            guess_target = target_nodes[0]
            return ErrorEvent(
                cls,
                actor,
                f"{guess_target.get_prefix_view()} isn't something you can whisper to.",
                [guess_target],
            )
        else:
            return ErrorEvent(
                cls, actor, f"You can't find '{target_name}' here that you can talk to."
            )

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["WhisperEvent", ErrorEvent]:
        """Whisper events are valid as long as there is text, otherwise fail."""
        assert text is not None, "Cannot construct WhisperEvent without text"
        text = text.strip()
        if len(text) == 0:
            return ErrorEvent(
                cls, actor, "Whisper what? You have to whisper something!"
            )
        text = text.strip()
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]

        return cls(
            actor, target_nodes=[targets[0]], text_content=text, event_id=event_id
        )

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """
        Return any valid actions that can be taken by the given actor
        over the current graph. Default returns no events.
        """
        valid_actions: List[GraphEvent] = []
        room = actor.get_room()
        room_agents = [x for x in room.get_contents() if x.agent]
        for agent in room_agents:
            if agent != actor:
                valid_actions.append(
                    cls(actor, target_nodes=[agent], text_content="<SOMETHING>")
                )
        return valid_actions

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "whipser", "something", "incomprehensible", "whispered", "to"]


class TellEvent(SpeechEvent):
    """Handles saying something to a specific agent aloud."""

    NAMES = ["tell"]
    TEMPLATES = ['tell "<SOMETHING>" to <agent>']

    def execute(self, world: "World") -> List[GraphEvent]:
        """On execution, store the view for the actors involved"""
        assert not self.executed
        actor_name = self.actor.get_prefix_view()
        target_name = self.target_nodes[0].get_prefix_view()
        if self.is_dialogue_safe(self.text_content):
            self.__target_view = f'{actor_name} told you "{self.text_content}"'
            self.__in_room_view = (
                f'{actor_name} told {target_name} "{self.text_content}"'
            )
            self.__self_view = None
        else:
            self.__target_view = (
                f"{actor_name} mumbled something incomprehensible to you."
            )
            self.__in_room_view = f"{actor_name} mumbled something incomprehensible."
            self.__self_view = (
                f"You mumble something incomprehensible to {target_name}."
            )

        world.broadcast_to_room(self, exclude_agents=[self.actor])
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__self_view
        elif viewer == self.target_nodes[0]:
            return self.__target_view
        else:
            return self.__in_room_view

    def to_canonical_form(self) -> str:
        """
        Provide the text that this event's actor would use to invoke this event
        """
        return f'tell {self._canonical_targets[0]} "{self.text_content}"'

    @classmethod
    def split_text_args(
        cls, actor: GraphAgent, text: str
    ) -> Union[List[List[str]], ErrorEvent]:
        """Format is tell <target> "words being told"."""
        if '"' not in text:
            return ErrorEvent(
                cls,
                actor,
                "If you're trying to speak to someone, you must use quotes around what you're saying.",
            )
        text_split = text.split('"')
        target_name = text_split[0]
        spoken_text = '"'.join(text_split[1:-1]).strip()
        return [[target_name.strip(), spoken_text]]

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - the node for
        target_name should be an agent
        """
        assert len(text_args) == 2, "TellEvents require 2 arguments"
        target_name, text_content = text_args
        target_nodes = graph.desc_to_nodes(target_name, actor, "sameloc+players")
        applicable_nodes = [x for x in target_nodes if x.agent]
        if len(applicable_nodes) > 0:
            return ProcessedArguments(targets=[applicable_nodes[0]], text=text_content)
        elif len(target_nodes) > 0:
            guess_target = target_nodes[0]
            return ErrorEvent(
                cls,
                actor,
                f"You could talk to {guess_target.get_prefix_view()}, but it probably won't listen.",
                [guess_target],
            )
        else:
            return ErrorEvent(
                cls, actor, f"You can't find '{target_name}' here that you can talk to."
            )

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["TellEvent", ErrorEvent]:
        """Tell events are valid as long as there is text, otherwise fail."""
        assert len(targets) == 1, "Can only construct Tell event to exactly one target"
        target = targets[0]
        if text is None or len(text) == 0:
            return ErrorEvent(cls, actor, "Tell what? You have to tell something!")
        text = text.strip()
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]

        return cls(actor, target_nodes=[target], text_content=text, event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """
        Return any valid actions that can be taken by the given actor
        over the current graph. Default returns no events.
        """
        valid_actions: List[GraphEvent] = []
        room = actor.get_room()
        room_agents = [x for x in room.get_contents() if x.agent]
        for agent in room_agents:
            if agent != actor:
                valid_actions.append(
                    cls(actor, target_nodes=[agent], text_content="<SOMETHING>")
                )
        return valid_actions

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return [
            "you",
            "mumble",
            "mumbled",
            "something",
            "incomprehensible",
            "told",
            "to",
        ]


class LeaveEvent(TriggeredEvent):
    """Event to note that someone has left a room"""

    _SELF_VIEW_FROM_VOID = "You chant the words and feel yourself appearing and disappearing in a puff of smoke!"
    _ROOM_VIEW_FROM_VOID = "{} disappears in a puff of smoke!"

    def execute(self, world: "World") -> List[GraphEvent]:
        """Save expected views, then message everyone"""
        actor_name = self.actor.get_prefix_view()
        self.__self_view = None
        if self.target_nodes[0] == world.oo_graph.void:
            self.__self_view = self._SELF_VIEW_FROM_VOID
            self.__in_room_view = self._ROOM_VIEW_FROM_VOID.format(actor_name)
        else:
            target_name = self.target_nodes[0].get_prefix_view_from(self.room)
            self.__in_room_view = f"{actor_name} left towards {target_name}."
        world.broadcast_to_room(self, exclude_agents=[self.actor])
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__self_view
        else:
            return self.__in_room_view

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return (
            ["left", "towards"]
            + cls._SELF_VIEW_FROM_VOID.split()
            + cls._ROOM_VIEW_FROM_VOID[3:].split()
        )


class ArriveEvent(TriggeredEvent):
    """
    Event to note that someone has arrived in a room.

    It takes as text_content the name of the place the person arrived from.
    """

    def execute(self, world: "World") -> List[GraphEvent]:
        """Save expected views, then message everyone"""
        actor_name = self.actor.get_prefix_view()
        self.__in_room_view = f"{actor_name} {self.text_content}"
        world.broadcast_to_room(self, exclude_agents=[self.actor])
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return None  # One should not observe themself leaving
        else:
            return self.__in_room_view


class TriggerFollowEvent(TriggeredEvent):
    """
    Event to trigger a follow from, to tell that a follow happened

    it takes as target_nodes the possible destination
    """

    def execute(self, world: "World") -> List[GraphEvent]:
        """Determine if the actor will be able to follow, then execute if possible"""
        self.__successful_follow = self.target_nodes[0].would_fit(self.actor)
        world.broadcast_to_agents(self, [self.actor])
        if self.__successful_follow:
            GoEvent(self.actor, target_nodes=self.target_nodes).execute(world)
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            if self.__successful_follow:
                return "You follow."
            else:
                return "You try to follow, but cannot as there is no more room there!"
        else:
            return None  # One should not observe others follows

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return [
            "you",
            "follow",
            "try",
            "to",
            "but",
            "cannot",
            "as",
            "there",
            "is",
            "no",
            "more",
            "room",
            "there",
        ]


class GoEvent(GraphEvent):
    """Handles moving as an individual from one room to another"""

    NAMES = ["go"]
    TEMPLATES = ["go <room|path>"]

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
        # Must store room views because getting views from other rooms is odd
        new_room = self.target_nodes[0]
        old_room = self.actor.get_room()
        self.__canonical_room_view = new_room.get_view_from(old_room)

    def is_not_blocked(self, world):
        blockers = self.actor.get_blockers()
        if len(blockers) == 0:
            return True
        blocked = False
        blocker_name = ""
        for blocker in blockers:
            # Check if still in same room
            if blocker.get_room() != self.actor.get_room():
                # unblock, if not in same room.
                blocker.unblock()
                continue
            # Calculate if can block  using dexterity actor vs victim.
            victim_dex = self.actor.dexterity
            blocker_dex = blocker.dexterity
            chance = max(1, 1 + blocker_dex - victim_dex)
            if random.randint(0, 20) > chance:
                blocked = True
                self.blocker = blocker
                blocker_name = blocker.get_prefix_view()
                break
        if not blocked:
            return True
        self.__self_view = f"You were blocked from moving by {blocker_name}!"
        actor_name = self.actor.get_prefix_view()
        self.__blocker_view = f"You blocked {actor_name} from moving!"
        self.__in_room_view = f"{actor_name} was blocked from moving by {blocker_name}!"
        world.broadcast_to_room(self)
        self.executed = True
        return False

    def is_not_too_tired(self, world):
        eps = self.actor.movement_energy_cost
        health = self.actor.health
        if health > eps:
            return True
        self.__self_view = "You are too exhausted to move!"
        actor_name = self.actor.get_prefix_view()
        self.__in_room_view = f"{actor_name} tries to leave but is too exhausted!"
        world.broadcast_to_agents(self, [self.actor])
        self.executed = True
        return False

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, trigger leaving, move the agent, and trigger arriving
        Return GoFollow events and Look events as needed
        """
        assert not self.executed
        # Populate for views
        self.__self_view = None
        self.__in_room_view = None
        self.blocker = None
        old_room = self.actor.get_room()
        new_room = self.target_nodes[0]
        old_room_view = old_room.get_prefix_view_from(new_room)

        # Send event to loggers - this event does not get broadcasted, so need record
        if old_room.node_id in world.oo_graph.room_id_to_loggers:
            world.oo_graph.room_id_to_loggers[old_room.node_id].observe_event(self)
        if self.actor.node_id in world.purgatory.node_id_to_soul:
            agent = world.purgatory.node_id_to_soul[self.actor.node_id]
            if hasattr(agent, "agent_logger"):
                agent.agent_logger.observe_event(self)

        self.__successful_leave = self.is_not_too_tired(world)
        if not self.__successful_leave:
            return []

        self.__successful_leave = self.is_not_blocked(world)
        if not self.__successful_leave:
            return []

        # Trigger the leave event, must be before the move to get correct room
        LeaveEvent(self.actor, [self.target_nodes[0]]).execute(world)
        self.actor.move_to(new_room)
        ArriveEvent(self.actor, text_content="arrived from " + old_room_view).execute(
            world
        )
        LookEvent(self.actor).execute(world)

        # Lose a little bit of energy from moving.
        health = self.actor.health
        eps = self.actor.movement_energy_cost
        if health > eps:
            health_text = world.view.get_health_text_for(self.actor.node_id)
            self.actor.health = max(0, health - eps)
            new_health_text = world.view.get_health_text_for(self.actor.node_id)
            if health_text != new_health_text:
                HealthEvent(self.actor, text_content="HealthOnMoveEvent").execute(world)

        # trigger the follows
        followers = self.actor.get_followers()
        for follower in followers:
            TriggerFollowEvent(follower, target_nodes=self.target_nodes).execute(world)

        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        # Go events are mostly viewed through Leave and Arrive events.
        # These variables over other cases, such as being blocked.
        if viewer == self.blocker:
            return self.__blocker_view
        elif viewer == self.actor:
            return self.__self_view
        else:
            return self.__in_room_view

    def to_canonical_form(self) -> str:
        """
        Provide the text that this event's actor would use to invoke this event
        """
        return f"go {self.__canonical_room_view}".replace(
            "a path to the a path to the", "a path to the"
        )

    REPLACEMENTS = {
        "e": "east",
        "w": "west",
        "n": "north",
        "s": "south",
        "u": "up",
        "d": "down",
    }

    @classmethod
    def split_text_args(cls, actor: GraphAgent, text: str) -> List[List[str]]:
        """Format is go <place>."""
        text = text.strip()
        if text in cls.REPLACEMENTS:
            text = cls.REPLACEMENTS[text]
        return [[text]]

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for a path. The path must not be locked and there must be room to
        fit inside
        """
        assert len(text_args) == 1, "GoEvents take one additional argument"
        target_name = text_args[0]

        target_nodes = graph.desc_to_nodes(target_name, actor, "path")
        room_nodes = [x for x in target_nodes if x.room]
        current_room = actor.get_room()
        if len(room_nodes) == 0:
            return ErrorEvent(cls, actor, f"You can't find a path to '{target_name}'!")
        elif room_nodes[0] == current_room:
            return ErrorEvent(
                cls,
                actor,
                f"You're already here in {actor.get_room().get_prefix_view()}!",
            )

        target_room = room_nodes[0]
        path_edge = current_room.get_edge_to(target_room)
        if path_edge is not None and path_edge.path_is_locked():
            return ErrorEvent(cls, actor, f"The path there is locked!")
        if not target_room.would_fit(actor):
            return ErrorEvent(cls, actor, f"There's not enough room to fit in there!")

        return ProcessedArguments(targets=[target_room])

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["GoEvent", ErrorEvent]:
        """Go events are valid if properly parsed and thus target is a room."""
        assert len(targets) == 1, f"GoEvents take one target, the room. Got {targets}"
        target = targets[0]
        assert target.room, "Can only go to rooms"
        return cls(actor, target_nodes=[target], event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """Can create a go event to any unlocked path that fits"""
        valid_actions: List[GraphEvent] = []
        room = actor.get_room()
        for neighbor in room.get_neighbors():
            path_edge = room.get_edge_to(neighbor)
            if path_edge is not None and not path_edge.path_is_locked():
                if neighbor.would_fit(actor):
                    valid_actions.append(cls(actor, target_nodes=[neighbor]))
        return valid_actions

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        BLOCK_TEXT = "you blocked from moving was by".split()
        EXHAUSTED_TEXT = "you are too exhausted to move tries to leave but is".split()
        return ["arrived", "from"] + BLOCK_TEXT + EXHAUSTED_TEXT

    def to_json(
        self,
        viewer: Optional[GraphAgent] = None,
        indent: Optional[int] = None,
        compressed: Optional[bool] = False,
    ) -> str:
        """
        Convert the content of this action into a json format that can be
        imported back to the original with from_json.

        Arrive events may come from other graphs, and nodes will have additional contents
        that are not always in the existing graph.
        """
        base_json = super(GoEvent, self).to_json(
            viewer=viewer, indent=indent, compressed=compressed
        )
        as_dict = json.loads(base_json)
        as_dict["_actor_tree"] = create_agent_tree(self.actor)
        res = json.dumps(as_dict, cls=GraphEncoder, sort_keys=True, indent=indent)
        return res


class UnfollowEvent(NoArgumentEvent):
    """Handles removing a follow"""

    NAMES = ["unfollow"]
    TEMPLATES = ["unfollow"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, prepare  views and clear the follow
        """
        assert not self.executed
        actor_name = self.actor.get_prefix_view()
        follow_node = self.actor.get_following()
        assert follow_node is not None, "Must be following to unfollow!"
        follow_name = follow_node.get_prefix_view()
        self.__unfollow_view = f"You stopped following {follow_name}"
        self.__unfollowed_view = f"{actor_name} stopped following you"

        self.__follow_target = self.actor.get_following()
        self.actor.unfollow()
        world.broadcast_to_agents(self, [self.actor, self.__follow_target])
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__unfollow_view
        elif viewer == self.__follow_target:
            return self.__unfollowed_view
        else:
            return None

    def to_canonical_form(self) -> str:
        return f"unfollow"

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["UnfollowEvent", ErrorEvent]:
        """Unfollow events are valid as long as you are following something."""
        assert (
            len(targets) == 0
        ), f"UnfollowEvents should get no args, but got {targets}"
        if actor.get_following() is None:
            return ErrorEvent(cls, actor, "You already aren't following anyone")
        return cls(actor, event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """Can construct a valid unfollow if currently following"""
        if actor.get_following() is not None:
            return [cls(actor)]
        else:
            return []

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "stopped", "following"]


class FollowEvent(GraphEvent):
    """Handles having an agent follow another agent"""

    NAMES = ["follow"]
    TEMPLATES = ["follow <agent>"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        Register an agent as following another agent.
        """
        assert not self.executed
        # Populate for views
        if self.actor.get_following() is not None:
            UnfollowEvent(self.actor).execute(world)

        follow_target = self.target_nodes[0]
        actor_name = self.actor.get_prefix_view()
        follow_name = follow_target.get_prefix_view()
        self.__follow_view = f"You started following {follow_name}."
        self.__followed_view = f"{actor_name} started following you."

        self.actor.follow(follow_target)
        world.broadcast_to_agents(self, [self.actor, self.target_nodes[0]])
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__follow_view
        elif viewer == self.target_nodes[0]:
            return self.__followed_view
        else:
            return None

    def to_canonical_form(self) -> str:
        """
        Provide the text that this event's actor would use to invoke this event
        """
        return f"follow {self._canonical_targets[0]}"

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for an agent in the same room.
        """
        assert len(text_args) == 1, f"FollowEvent takes one arg, got {text_args}"
        target_name = text_args[0]
        target_nodes = graph.desc_to_nodes(target_name, actor, "sameloc")
        applicable_nodes = [x for x in target_nodes if x.agent]
        if len(applicable_nodes) > 0:
            return ProcessedArguments(targets=[applicable_nodes[0]])
        elif len(target_nodes) > 0:
            guess_target = target_nodes[0]
            return ErrorEvent(
                cls,
                actor,
                f"You could try and follow {guess_target.get_prefix_view()}, but it probably won't go anywhere.",
                [guess_target],
            )
        else:
            return ErrorEvent(
                cls, actor, f"You can't find '{target_name}' here that you can follow."
            )

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["FollowEvent", ErrorEvent]:
        """Follow events with a target agent will always be valid if it's not the already followed agent."""
        assert len(targets) == 1, f"FollowEvent takes one arg, got {targets}"
        target = targets[0]
        assert target.agent, "Can only follow agents"
        if target == actor.get_following():
            return ErrorEvent(
                cls,
                actor,
                f"You are already following {target.get_prefix_view()}!",
                [target],
            )
        return cls(actor, target_nodes=[target], event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """
        Return any valid actions that can be taken by the given actor
        over the current graph. Default returns no events.
        """
        valid_actions: List[GraphEvent] = []
        room = actor.get_room()
        room_nodes = room.get_contents()
        room_agents = [x for x in room_nodes if x.agent]
        for agent in room_agents:
            if agent != actor:
                valid_actions.append(cls(actor, target_nodes=[agent]))
        return valid_actions

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "started", "following"]


class UnblockEvent(NoArgumentEvent):
    """Handles removing a block"""

    NAMES = ["unblock"]
    TEMPLATES = ["unblock"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, prepare  views and clear the block
        """
        assert not self.executed
        if self.actor.dead:
            return []
        actor_name = self.actor.get_prefix_view()
        block_node = self.actor.get_blocking()
        assert block_node is not None, "Cannot unblock if not blocking"
        block_name = block_node.get_prefix_view()
        self.__unblock_view = f"You stopped blocking {block_name}"
        self.__unblocked_view = f"{actor_name} stopped blocking you"

        self.__block_target = self.actor.get_blocking()
        self.actor.unblock()
        world.broadcast_to_agents(self, [self.actor, self.__block_target])
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__unblock_view
        elif viewer == self.__block_target:
            return self.__unblocked_view
        else:
            return None

    def to_canonical_form(self) -> str:
        return f"unblock"

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["UnblockEvent", ErrorEvent]:
        """Unblock events are valid as long as you are blocking something."""
        assert len(targets) == 0, f"UnblockEvents should get no args, but got {targets}"
        if actor.get_blocking() is None:
            return ErrorEvent(cls, actor, "You already aren't blocking anyone")
        return cls(actor, event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """Can construct a valid unblock if currently blocking"""
        if actor.get_blocking() is not None:
            return [cls(actor)]
        else:
            return []

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "stopped", "blocking"]


class BlockEvent(GraphEvent):
    """Handles having an agent blocking another agent"""

    NAMES = ["block"]
    TEMPLATES = ["block <agent>"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        Register an agent as blocking another agent.
        """
        assert not self.executed
        # Populate for views
        if self.actor.get_blocking() is not None:
            UnblockEvent(self.actor).execute(world)

        block_target = self.target_nodes[0]
        actor_name = self.actor.get_prefix_view()
        block_name = block_target.get_prefix_view()
        self.__block_view = f"You started blocking {block_name}."
        self.__blocked_view = f"{actor_name} started blocking you."

        self.actor.block(block_target)

        world.broadcast_to_agents(self, [self.actor, self.target_nodes[0]])
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__block_view
        elif viewer == self.target_nodes[0]:
            return self.__blocked_view
        else:
            return None

    def to_canonical_form(self) -> str:
        """
        Provide the text that this event's actor would use to invoke this event
        """
        return f"block {self._canonical_targets[0]}"

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for an agent in the same room.
        """
        assert len(text_args) == 1, f"BlockEvent takes one arg, got {text_args}"
        target_name = text_args[0]
        target_nodes = graph.desc_to_nodes(target_name, actor, "sameloc")
        applicable_nodes = [x for x in target_nodes if x.agent]
        if len(applicable_nodes) > 0:
            return ProcessedArguments(targets=[applicable_nodes[0]])
        elif len(target_nodes) > 0:
            guess_target = target_nodes[0]
            return ErrorEvent(
                cls,
                actor,
                f"You could try and block {guess_target.get_prefix_view()}, but it probably won't go anywhere.",
                [guess_target],
            )
        else:
            return ErrorEvent(
                cls, actor, f"You can't find '{target_name}' here that you can block."
            )

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["BlockEvent", ErrorEvent]:
        """Block events with a target agent will always be valid if it's not the already blocked agent."""
        assert len(targets) == 1, f"BlockEvent takes one arg, got {targets}"
        target = targets[0]
        assert target.agent, "Can only block agents"
        if target == actor.get_blocking():
            return ErrorEvent(
                cls,
                actor,
                f"You are already blocking {target.get_prefix_view()}!",
                [target],
            )
        return cls(actor, target_nodes=[target], event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """
        Return any valid actions that can be taken by the given actor
        over the current graph. Default returns no events.
        """
        valid_actions: List[GraphEvent] = []
        room = actor.get_room()
        room_nodes = room.get_contents()
        room_agents = [x for x in room_nodes if x.agent]
        for agent in room_agents:
            if agent != actor:
                valid_actions.append(cls(actor, target_nodes=[agent]))
        return valid_actions

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "started", "blocking"]


# Note, this is the only event we have right now where the actor is
# an object... This may need cleanup
class DeleteObjectEvent(TriggeredEvent):
    """Handles deleting an object node from the graph"""

    def execute(self, world: "World") -> List[GraphEvent]:
        actor_name = self.actor.get_prefix_view()
        self.__in_room_view = f"{actor_name} {self.text_content}"
        g = world.oo_graph
        g.delete_nodes([self.actor])
        world.broadcast_to_room(self)
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        return self.__in_room_view


# TODO examine more death processing. Do we need to update a player status?
# must check structured_graph and graph_nodes
class DeathEvent(TriggeredEvent):
    """Handles processing graph cleanup when an agent dies, and sending message"""

    def execute(self, world: "World") -> List[GraphEvent]:
        """Save expected views, then message everyone"""
        actor_name = self.actor.get_prefix_view()
        self.__in_room_view = f"{actor_name} died! "
        self.actor.mark_dying()

        # You have to send to the room before death or the dying agent won't get the message
        world.broadcast_to_room(self)

        # Trigger the actual death
        world.oo_graph.agent_die(self.actor)
        # await world.purgatory.clear_soul(self.actor) todo - clear soul only after message queue consumed
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return f"You died! "
        else:
            return self.__in_room_view

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "died"]


class SoulSpawnEvent(TriggeredEvent):
    """Handles processing the view for when a player is spawned, and passing their context"""

    def __init__(
        self,
        soul_id,
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
        # Must store this for important metadata
        self.soul_id = soul_id

    def execute(self, world: "World") -> List[GraphEvent]:
        # Add player id as an attribute
        """Construct intro text and broadcast to the player"""
        actor_name = self.actor.get_prefix_view()

        sun_txt = emoji.emojize(":star2:") * 31
        msg_txt = sun_txt + "\n"
        msg_txt += f"Your soul possesses {actor_name}. Roleplay well, my friend, and earn experience points!\n"
        msg_txt += "Your character:\n"
        msg_txt += self.actor.persona + "\n"
        msg_txt += sun_txt + "\n"
        self.__msg_txt = msg_txt
        world.broadcast_to_agents(self, [self.actor])

        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__msg_txt
        else:
            return None

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return [
            "your",
            "soul",
            "possesses",
            "roleplay",
            "well",
            "my",
            "friend",
            "and",
            "earn",
            "experience",
            "points",
            "character",
        ]


class SpawnEvent(TriggeredEvent):
    """Handles processing the view for when a player is spawned, and passing their context"""

    def execute(self, world: "World") -> List[GraphEvent]:
        """Construct intro text and broadcast to the player"""
        actor_name = self.actor.get_prefix_view()

        sun_txt = emoji.emojize(":star2:") * 31
        msg_txt = sun_txt + "\n"
        msg_txt += f"You are spawned into this world as {self.actor.get_view()}.\n"
        msg_txt += "Your character:\n"
        msg_txt += self.actor.persona + "\n"
        msg_txt += sun_txt + "\n"
        self.__msg_txt = msg_txt

        world.broadcast_to_agents(self, [self.actor])

        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__msg_txt
        else:
            return None

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return [
            "you",
            "are",
            "spawned",
            "into",
            "this",
            "world",
            "as",
            "your",
            "character",
        ]


class HelpEvent(NoArgumentEvent):
    """Handles user asking for help"""

    NAMES = ["help", "h"]
    TEMPLATES = ["help"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """Construct intro text and broadcast to the player"""
        actor_name = self.actor.get_prefix_view()
        self.__msg_txt = world.view.help_text()
        world.broadcast_to_agents(self, [self.actor])
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__msg_txt
        else:
            return None


class HitEvent(GraphEvent):
    """Handles having one agent attack another"""

    NAMES = ["hit"]
    TEMPLATES = ["hit <agent>"]

    _PACIFIST_TEXT = "You couldn't do that, you are a pacifist!"
    _ATTACK_VERBS = ["attacked", "struck at", "charged at", "swiped at"]
    _BLOCK_VERBS = ["parried", "blocked", "repelled"]
    _HIT_DETAILS = [
        "making crunching contact",
        "hitting the target",
        "crunch",
        "smash",
        "crack, that hurts",
    ]

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
        # Must store these for replaying exact sequences
        self.attack = None
        self.defense = None

    def is_not_pacifist(self, world):
        self.pacifist = False
        if not self.actor.pacifist:
            return True
        self.pacifist = True
        self.__self_view = "You couldn't do that, you are a pacifist!"
        world.broadcast_to_agents(self, [self.actor])
        self.executed = True
        return False

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, have one agent hit another, calculating
        the outcome depending on battle stats.

        If an agent died, trigger a death event.
        """
        assert not self.executed

        if self.actor.dead:
            return []

        self.__successful_hit = self.is_not_pacifist(world)
        if not self.__successful_hit:
            return []

        # Populate for views
        self.__actor_name = self.actor.get_prefix_view()
        attack_target = self.target_nodes[0]
        assert isinstance(attack_target, GraphAgent), "Must attack an agent"
        self.__attack_name = attack_target.get_prefix_view()
        damage = self.actor.get_prop("damage", 0) + self.actor.strength
        armor = attack_target.get_prop("defense", 0) + self.actor.dexterity
        if self.attack is None:
            # need to save randomized attacks for replaying
            self.attack = random.randint(max(0, damage - 10), damage + 1)
            self.defend = random.randint(max(0, armor - 10), armor)

            # pick weapon that hit the opponent
            weapons = []
            for id, obj in self.actor.contained_nodes.items():
                n = obj._target_node
                assert isinstance(n, GraphObject)
                if n.wieldable and n.equipped:
                    weapons.append(n)
            if len(weapons) == 0:
                self.weapon = "none"
            else:
                self.weapon = random.choice(weapons).get_prefix_view()
            # fun text details
            self.attack_verb = random.choice(self._ATTACK_VERBS)
            self.block_verb = random.choice(self._BLOCK_VERBS)
            self.hit_details = random.choice(self._HIT_DETAILS)

        # Mark as a coming death if this is death, as no response can occur
        if attack_target.health <= self.attack - self.defend:
            attack_target.mark_dying()

        world.broadcast_to_room(self)

        if self.attack - self.defend > 1:
            # Calculate damage
            health = attack_target.health
            health = max(0, health - (self.attack - self.defend))
            attack_target.health = health

            if health == 0:
                DeathEvent(attack_target).execute(world)
            else:
                HealthEvent(
                    attack_target,
                    target_nodes=[self.actor],
                    text_content="HealthOnHitEvent",
                ).execute(world)

        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""

        if self.pacifist:
            if viewer == self.actor:
                return self.__self_view
            return ""

        if self.attack is None:
            self.attack = 0

        if self.attack == 0:
            # The attack missed
            if viewer == self.actor:
                return f"You {self.attack_verb} {self.__attack_name}, but missed!"
            elif viewer == self.target_nodes[0]:
                return f"{self.__actor_name} {self.attack_verb} you, but missed."
            else:
                return f"{self.__actor_name} {self.attack_verb} {self.__attack_name}, but missed."
        elif self.attack - self.defend <= 1:
            # The attack was blocked
            if viewer == self.actor:
                return f"You {self.attack_verb} {self.__attack_name}, but they {self.block_verb}! "
            elif viewer == self.target_nodes[0]:
                return f"{self.__actor_name} {self.attack_verb} you, but you {self.block_verb}. "
            else:
                return f"{self.__actor_name} {self.attack_verb} {self.__attack_name}, but the attack was {self.block_verb}. "
        else:
            # The attack happened
            txt = ""
            if viewer == self.actor:
                txt = f"You {self.attack_verb} {self.__attack_name}"
            elif viewer == self.target_nodes[0]:
                txt = f"{self.__actor_name} attacked you"
            else:
                txt = f"{self.__actor_name} {self.attack_verb} {self.__attack_name}"
            if self.weapon != "none":
                txt += " with " + self.weapon
            if self.hit_details != "none":
                txt += ", " + self.hit_details
            txt += "!"
            return txt

    def to_canonical_form(self) -> str:
        """
        Provide the text that this event's actor would use to invoke this event
        """
        return f"hit {self._canonical_targets[0]}"

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for an agent in the same room.
        """
        assert len(text_args) == 1, f"HitEvent takes one arg, got {text_args}"
        target_name = text_args[0]
        target_nodes = graph.desc_to_nodes(target_name, actor, "sameloc")
        applicable_nodes = [x for x in target_nodes if x.agent]
        if len(applicable_nodes) > 0:
            return ProcessedArguments(targets=[applicable_nodes[0]])
        elif len(target_nodes) > 0:
            guess_target = target_nodes[0]
            return ErrorEvent(
                cls,
                actor,
                f"You could try and hit {guess_target.get_prefix_view()}, but it won't do anything.",
                [guess_target],
            )
        else:
            return ErrorEvent(
                cls, actor, f"You can't find '{target_name}' here that you can hit."
            )

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["HitEvent", "ErrorEvent"]:
        """Hit events with a target agent will always be valid."""
        assert len(targets) == 1, f"HitEvent takes one arg, got {targets}"
        target = targets[0]
        assert target.agent, "Can only hit agents"
        return cls(actor, target_nodes=[target], event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """
        Return any valid actions that can be taken by the given actor
        over the current graph. Default returns no events.
        """
        valid_actions: List[GraphEvent] = []
        room = actor.get_room()
        room_nodes = room.get_contents()
        room_agents = [x for x in room_nodes if x.agent]
        for agent in room_agents:
            if agent != actor:
                valid_actions.append(cls(actor, target_nodes=[agent]))
        return valid_actions

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        vocab = []
        vocab += cls._PACIFIST_TEXT.split()
        vocab += split_in_list(cls._ATTACK_VERBS)
        vocab += split_in_list(cls._BLOCK_VERBS)
        vocab += split_in_list(cls._HIT_DETAILS)
        vocab += ["but", "missed", "they", "you", "the", "attack", "attacked", "with"]
        return vocab


class HugEvent(GraphEvent):
    """Handles having one agent give another a hug"""

    NAMES = ["hug"]
    TEMPLATES = ["hug <agent>"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, have one agent hug another. Store required view names
        and broadcast the event
        """
        assert not self.executed
        # Populate for views
        self.__actor_name = self.actor.get_prefix_view()
        self.__hugged_name = self.target_nodes[0].get_prefix_view()
        world.broadcast_to_room(self)
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return f"You hugged {self.__hugged_name}."
        elif viewer == self.target_nodes[0]:
            return f"{self.__actor_name} hugged you."
        else:
            return f"{self.__actor_name} hugged {self.__hugged_name}."

    def to_canonical_form(self) -> str:
        """
        Provide the text that this event's actor would use to invoke this event
        """
        return f"hug {self._canonical_targets[0]}"

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for an agent in the same room.
        """
        assert len(text_args) == 1, f"HugEvent takes one arg, got {text_args}"
        target_name = text_args[0]
        target_nodes = graph.desc_to_nodes(target_name, actor, "sameloc")
        applicable_nodes = [x for x in target_nodes if x.agent]
        if len(applicable_nodes) > 0:
            return ProcessedArguments(targets=[applicable_nodes[0]])
        elif len(target_nodes) > 0:
            guess_target = target_nodes[0]
            return ErrorEvent(
                cls,
                actor,
                f"You could try and hug {guess_target.get_prefix_view()}, but it won't do anything.",
                [guess_target],
            )
        else:
            return ErrorEvent(
                cls, actor, f"You can't find '{target_name}' here that you can hug."
            )

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["HugEvent", "ErrorEvent"]:
        """Hug events with a target will always be valid."""
        assert len(targets) == 1, f"HugEvent takes one arg, got {targets}"
        target = targets[0]
        assert target.agent, "Can only hug agents"
        return cls(actor, target_nodes=[target], event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """
        Return any valid actions that can be taken by the given actor
        over the current graph. Default returns no events.
        """
        valid_actions: List[GraphEvent] = []
        room = actor.get_room()
        room_nodes = room.get_contents()
        room_agents = [x for x in room_nodes if x.agent]
        for agent in room_agents:
            if agent != actor:
                valid_actions.append(cls(actor, target_nodes=[agent]))
        return valid_actions

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "hugged"]


# TODO handle locked objects
class GetObjectEvent(GraphEvent):
    """Handles getting an object from a container or a location"""

    NAMES = ["get", "take"]
    TEMPLATES = ["get <gettable> from <container|surface|room>", "get <gettable>"]

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
        self.__from_room = self.room == self.target_nodes[1]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, move the item from its location to the agent
        """
        assert not self.executed
        # Populate for views
        self.__actor_name = self.actor.get_prefix_view()
        gotten_target = self.target_nodes[0]
        self.__gotten_name = gotten_target.get_prefix_view()
        self.__container_name = self.target_nodes[1].get_prefix_view()

        # Move the object over and broadcast
        gotten_target.move_to(self.actor)
        world.broadcast_to_room(self)
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""

        if viewer == self.actor:
            viewer_text = "You"
        else:
            viewer_text = self.__actor_name
        if self.__from_room:
            return f"{viewer_text} got {self.__gotten_name}."
        else:
            return (
                f"{viewer_text} got {self.__gotten_name} from {self.__container_name}."
            )

    def to_canonical_form(self) -> str:
        """return action text for Get the canonical target, from the container if not the room"""
        if self.__from_room:
            return f"get {self._canonical_targets[0]}"
        return f"get {self._canonical_targets[0]} from {self._canonical_targets[1]}"

    @classmethod
    def split_text_args(
        cls, actor: GraphAgent, text: str
    ) -> Union[List[List[str]], "ErrorEvent"]:
        """
        Return all possible interpretations for "get x from y".

        Must consider that "get ornament from china from big chest" should properly
        be able to consider both [ornament from china, big chest] and [ornament, china from big chest]
        """
        possible_from_splits = text.split(" from ")
        possibilities = []
        for split_ind in range(len(possible_from_splits)):
            before = " from ".join(possible_from_splits[:split_ind])
            after = " from ".join(possible_from_splits[split_ind:])
            if len(after) > 0 and len(before) > 0:
                possibilities.append([before, after])
        possibilities.append([text])
        return possibilities

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for an object, within a container if given.
        """
        assert (
            len(text_args) == 1 or len(text_args) == 2
        ), f"GetObjectEvent takes one or two arguments, got {text_args}"
        object_name = text_args[0]
        container_name = None
        if len(text_args) == 2:
            container_name = text_args[1]
        possible_containers: List[GraphNode] = [actor.get_room()]
        if container_name is not None:
            # getting an item from the specified container
            target_nodes = graph.desc_to_nodes(container_name, actor, "all+here")
            applicable_nodes = [x for x in target_nodes if isinstance(x, GraphObject)]
            applicable_containers: List[GraphNode] = [
                x for x in applicable_nodes if x.container
            ]
            if len(applicable_containers) == 0:
                # didn't find a container to use
                if len(applicable_nodes) == 0:
                    # didn't find any nodes by this name
                    return ErrorEvent(
                        cls,
                        actor,
                        f"You can't find '{container_name}' here that you can get things from.",
                    )
                else:
                    guess_target = target_nodes[0]
                    guess_target_name = guess_target.get_prefix_view()
                    # nodes found were not a container
                    return ErrorEvent(
                        cls,
                        actor,
                        f"{guess_target_name} isn't something you can get things from.",
                        [guess_target],
                    )
            possible_containers = applicable_containers
        # check each container to see if the wanted object is within
        first_guess_error = None
        for container in possible_containers:
            target_nodes = graph.desc_to_nodes(object_name, container, "carrying")
            applicable_nodes = [x for x in target_nodes if isinstance(x, GraphObject)]
            applicable_nodes = [x for x in applicable_nodes if x.gettable]
            if len(applicable_nodes) > 0:
                # we found the thing!
                return ProcessedArguments(targets=[applicable_nodes[0], container])
            elif len(target_nodes) > 0:
                # we found a node, but it isn't the right one. if this is our first find, it'll be the error
                if first_guess_error is None:
                    guess_target = target_nodes[0]
                    guess_target_name = guess_target.get_prefix_view()
                    first_guess_error = ErrorEvent(
                        cls,
                        actor,
                        f"{guess_target_name}, isn't something you can get.",
                        [guess_target],
                    )
        # didn't end up finding the thing
        if first_guess_error is not None:
            return first_guess_error
        return ErrorEvent(
            cls, actor, f"You can't find '{object_name}' here that you can get."
        )

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["GetObjectEvent", "ErrorEvent"]:
        """Get object events are valid as long as the agent can hold the object"""
        assert len(targets) == 2, f"GetObjectEvent takes two arg, got {targets}"
        target, container = targets
        assert (
            target in container.get_contents()
        ), "Target node is not in the given container"
        if not actor.would_fit(target):
            return ErrorEvent(
                cls,
                actor,
                f"You can't get {target.get_prefix_view()} because you can't carry that much more.",
            )
        return cls(actor, target_nodes=[target, container], event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """
        Find all objects that are currently gettable in the given room for the given agent.
        """
        valid_actions: List[GraphEvent] = []
        # Add a possible get for any object in the room
        room = actor.get_room()
        room_objects = [x for x in room.get_contents() if isinstance(x, GraphObject)]
        for obj in room_objects:
            if actor.would_fit(obj):
                valid_actions.append(cls(actor, target_nodes=[obj, room]))

        # Add a possible get for any object in any accessible container
        actor_objects = [x for x in actor.get_contents() if isinstance(x, GraphObject)]
        possible_objects = room_objects + actor_objects
        container_nodes = [x for x in possible_objects if x.container]
        for container in container_nodes:
            for obj in container.get_contents():
                if actor.would_fit(obj):
                    valid_actions.append(cls(actor, target_nodes=[obj, container]))
        return valid_actions

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "got", "from"]


# TODO handle locked objects
class PutObjectInEvent(GraphEvent):
    """Handles putting an object in or on another object"""

    NAMES = ["put"]
    TEMPLATES = ["put <gettable> in <container>", "put <gettable> on <surface>"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, move the item from its location to the age
        """
        assert not self.executed
        # Populate for views
        self.__actor_name = self.actor.get_prefix_view()
        put_target = self.target_nodes[0]
        self.__put_name = put_target.get_prefix_view()
        self.__container_name = self.target_nodes[1].get_prefix_view()

        # Move the object over and broadcast
        put_target.move_to(self.target_nodes[1])
        world.broadcast_to_room(self)
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""

        if viewer == self.actor:
            viewer_text = "You"
        else:
            viewer_text = self.__actor_name
        surface_type = self.target_nodes[1].get_prop("surface_type", "in")
        return f"{viewer_text} put {self.__put_name} {surface_type} {self.__container_name}."

    def to_canonical_form(self) -> str:
        """return action text for putting the object in/on the container"""
        surface_type = self.target_nodes[1].get_prop("surface_type", "in")
        return f"put {self._canonical_targets[0]} {surface_type} {self._canonical_targets[1]}"

    @classmethod
    def split_text_args(
        cls, actor: GraphAgent, text: str
    ) -> Union[List[List[str]], "ErrorEvent"]:
        """
        Return all possible interpretations for "put x in/on y".

        Must consider multiple in/on situations
        """
        splitwords = ["in", "on", "into", "onto"]

        has_word = False
        for word in splitwords:
            if f" {word} " in text:
                has_word = True

        if not has_word:
            return ErrorEvent(
                cls, actor, "You must `put <something> <in/on> <something>`."
            )

        possibilities = []
        for word in splitwords:
            splitword = f" {word} "
            possible_splits = text.split(splitword)
            for split_ind in range(len(possible_splits)):
                before = splitword.join(possible_splits[:split_ind])
                after = splitword.join(possible_splits[split_ind:])
                if len(after) > 0 and len(before) > 0:
                    possibilities.append([before, after])

        return possibilities

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for an object, within the actor, and a container in the room.
        """
        assert len(text_args) == 2, f"PutObjectInEvent takes two args, got {text_args}"
        object_name, container_name = text_args
        # putting an item in the specified container
        target_nodes = graph.desc_to_nodes(container_name, actor, "all+here")
        applicable_nodes = [x for x in target_nodes if isinstance(x, GraphObject)]
        applicable_containers = [x for x in applicable_nodes if x.container]
        if len(applicable_containers) == 0:
            # didn't find a container to use
            if len(applicable_nodes) == 0:
                # didn't find any nodes by this name
                return ErrorEvent(
                    cls,
                    actor,
                    f"You can't find '{container_name}' here that you can put in/onto.",
                )
            else:
                guess_target = target_nodes[0]
                guess_target_name = guess_target.get_prefix_view()
                # nodes found were not a container
                return ErrorEvent(
                    cls,
                    actor,
                    f"{guess_target_name} isn't something you can get put things in/on.",
                    [guess_target],
                )
        container = applicable_containers[0]

        # check actor to see if the wanted object is within
        target_nodes = graph.desc_to_nodes(object_name, actor, "carrying")
        applicable_nodes = [x for x in target_nodes if isinstance(x, GraphObject)]
        unequipped_nodes = [x for x in applicable_nodes if not x.equipped]
        if len(unequipped_nodes) > 0:
            # we found the thing!
            return ProcessedArguments(targets=[unequipped_nodes[0], container])
        if len(applicable_nodes) > 0:
            # we found the thing, but it's equipped
            guess_target = applicable_nodes[0]
            guess_target_name = guess_target.get_prefix_view()
            return ErrorEvent(
                cls,
                actor,
                f"You could put {guess_target_name}, but you'll have to remove it first.",
                [guess_target],
            )
        elif len(target_nodes) > 0:
            # we found a node, but it isn't the right one.
            guess_target = target_nodes[0]
            guess_target_name = guess_target.get_prefix_view()
            return ErrorEvent(
                cls,
                actor,
                f"{guess_target_name}, isn't something you can put.",
                [guess_target],
            )
        return ErrorEvent(cls, actor, f"You don't have '{object_name}' here to put.")

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["PutObjectInEvent", "ErrorEvent"]:
        """Put object events are valid as long as the container can hold the object and is not the object"""
        assert len(targets) == 2, f"PutObjectInEvent takes two args, got {targets}"
        target, container = targets
        assert (
            target in actor.get_contents()
        ), "Target node is not in the given container"
        if container == target:
            return ErrorEvent(
                cls, actor, f"You can't put {target.get_prefix_view()} into itself!."
            )
        if not container.would_fit(target):
            return ErrorEvent(
                cls,
                actor,
                f"You can't put {target.get_prefix_view()} in {container.get_prefix_view()} because there's no room left for it.",
            )
        return cls(actor, target_nodes=[target, container], event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """
        Find all objects that are currently gettable in the given room for the given agent.
        """
        valid_actions: List[GraphEvent] = []
        # get all the put-able objects
        putable_objects = [
            x for x in actor.get_contents() if isinstance(x, GraphObject)
        ]
        if len(putable_objects) == 0:
            return []

        possible_objects = [
            x
            for x in actor.get_room().get_contents()
            if isinstance(x, GraphObject) and not x.equipped
        ]
        possible_containers = [x for x in possible_objects if x.container]
        # Try to put all objects into all containers
        for obj in putable_objects:
            for container in possible_containers:
                if container.would_fit(obj):
                    valid_actions.append(cls(actor, target_nodes=[obj, container]))

        return valid_actions

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "put", "in", "on"]


class DropObjectEvent(GraphEvent):
    """Handles dropping an object onto the floor"""

    NAMES = ["drop"]
    TEMPLATES = ["drop <gettable>"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, move the item from the actor to the room
        """
        assert not self.executed
        # Populate for views
        self.__actor_name = self.actor.get_prefix_view()
        drop_target = self.target_nodes[0]
        self.__drop_name = drop_target.get_prefix_view()

        # Move the object over and broadcast
        drop_target.move_to(self.room)
        world.broadcast_to_room(self)
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""

        if viewer == self.actor:
            viewer_text = "You"
        else:
            viewer_text = self.__actor_name
        return f"{viewer_text} dropped {self.__drop_name}."

    def to_canonical_form(self) -> str:
        """return action text for dropping the object"""
        return f"drop {self._canonical_targets[0]}"

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for an object within the actor.
        """
        assert len(text_args) == 1, f"DropObjectEvent takes one arg, got {text_args}"
        object_name = text_args[0]
        # check actor to see if the wanted object is within
        target_nodes = graph.desc_to_nodes(object_name, actor, "carrying")
        applicable_nodes = [x for x in target_nodes if isinstance(x, GraphObject)]
        unequipped_nodes = [x for x in applicable_nodes if not x.equipped]
        if len(unequipped_nodes) > 0:
            # we found the thing!
            return ProcessedArguments(targets=[unequipped_nodes[0]])
        if len(applicable_nodes) > 0:
            # we found the thing, but it's equipped
            guess_target = applicable_nodes[0]
            guess_target_name = guess_target.get_prefix_view()
            return ErrorEvent(
                cls,
                actor,
                f"You could drop {guess_target_name}, but you'll have to remove it first.",
                [guess_target],
            )
        elif len(target_nodes) > 0:
            # we found a node, but it isn't the right one.
            guess_target = target_nodes[0]
            guess_target_name = guess_target.get_prefix_view()
            return ErrorEvent(
                cls,
                actor,
                f"{guess_target_name}, isn't something you can drop.",
                [guess_target],
            )
        return ErrorEvent(cls, actor, f"You don't have '{object_name}' to drop.")

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["DropObjectEvent", "ErrorEvent"]:
        """Drop object events are valid as long as the container can hold the object"""
        assert len(targets) == 1, f"DropObjectEvent takes one arg, got {targets}"
        target = targets[0]
        assert (
            target in actor.get_contents()
        ), "Target node is not in the given container"
        if not actor.get_room().would_fit(target):
            return ErrorEvent(
                cls,
                actor,
                f"You can't drop {target.get_prefix_view()} because there's no room left for it.",
            )
        return cls(actor, target_nodes=[target], event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """
        Find all objects that are currently gettable in the given room for the given agent.
        """
        valid_actions: List[GraphEvent] = []
        # get all the drop-able objects
        dropable_objects = [
            x
            for x in actor.get_contents()
            if isinstance(x, GraphObject) and not x.equipped
        ]
        if len(dropable_objects) == 0:
            return []

        # Try to drop everything
        for obj in dropable_objects:
            if actor.get_room().would_fit(obj):
                valid_actions.append(cls(actor, target_nodes=[obj]))

        return valid_actions

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "dropped"]


class StealObjectEvent(GraphEvent):
    """Handles stealing an object from an actor"""

    NAMES = ["steal"]
    TEMPLATES = ["steal <gettable> from <agent>"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, move the item from its location to the actor
        """
        assert not self.executed

        # Populate for views
        self.__actor_name = self.actor.get_prefix_view()
        gotten_target = self.target_nodes[0]
        self.__gotten_name = gotten_target.get_prefix_view()
        self.__victim_name = self.target_nodes[1].get_prefix_view()

        # Calculate if can steal using dexterity actor vs victim.
        actor_dex = self.actor.dexterity
        victim = self.target_nodes[1]
        assert isinstance(victim, GraphAgent), "must steal from another agent"
        victim_dex = victim.dexterity
        chance = max(1, 1 + actor_dex - victim_dex)
        self.failed = False
        r = random.randint(0, 20)
        if r > chance:
            # failed steal operation
            self.failed = True
        else:
            # Move the object over and broadcast
            gotten_target.move_to(self.actor)

        world.broadcast_to_room(self)
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""

        if viewer == self.actor:
            actor_text = "You"
        else:
            actor_text = self.__actor_name
        victim_text = self.__victim_name
        if viewer == self.target_nodes[1]:
            victim_text = "you"
        if self.failed:
            return f"{actor_text} tried to steal {self.__gotten_name} from {victim_text}, but they were caught in the act!"
        else:
            return f"{actor_text} stole {self.__gotten_name} from {victim_text}."

    def to_canonical_form(self) -> str:
        """return action text for stealing from the target"""
        return f"steal {self._canonical_targets[0]} from {self._canonical_targets[1]}"

    @classmethod
    def split_text_args(
        cls, actor: GraphAgent, text: str
    ) -> Union[List[List[str]], "ErrorEvent"]:
        """
        Return all possible interpretations for "steal x from y".

        Must consider that "steal ornament from china from big chest" should properly
        be able to consider both [ornament from china, big chest] and [ornament, china from big chest]
        """
        if " from " not in text:
            return ErrorEvent(
                cls, actor, "You must `steal <something> from <someone>`."
            )
        possible_from_splits = text.split(" from ")
        possibilities = []
        for split_ind in range(len(possible_from_splits)):
            before = " from ".join(possible_from_splits[:split_ind])
            after = " from ".join(possible_from_splits[split_ind:])
            if len(after) > 0 and len(before) > 0:
                possibilities.append([before, after])
        return possibilities

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for an object, within an agent
        """
        assert len(text_args) == 2, f"StealObjectEvent takes two args, got {text_args}"
        object_name, victim_name = text_args
        possible_victims = []
        # getting an item from the specified container
        target_nodes = graph.desc_to_nodes(victim_name, actor, "sameloc")
        applicable_victims = [x for x in target_nodes if isinstance(x, GraphAgent)]
        if len(applicable_victims) == 0:
            if len(target_nodes) > 0:
                guess_target = target_nodes[0]
                guess_target_name = guess_target.get_prefix_view()
                # nodes found were not an agent
                return ErrorEvent(
                    cls,
                    actor,
                    f"{guess_target_name} isn't someone you can steal things from.",
                    [guess_target],
                )
            else:
                # didn't find a container to use
                return ErrorEvent(
                    cls,
                    actor,
                    f"You can't find '{victim_name}' here that you can steal things from.",
                )
        possible_victims = applicable_victims

        # check each victim to see if the wanted object is within
        first_guess_error = None
        for victim in possible_victims:
            target_nodes = graph.desc_to_nodes(object_name, victim, "carrying")
            applicable_nodes = [x for x in target_nodes if isinstance(x, GraphObject)]
            unequipped_nodes = [x for x in applicable_nodes if not x.equipped]
            if len(unequipped_nodes) > 0:
                # we found the thing!
                return ProcessedArguments(targets=[unequipped_nodes[0], victim])
            if len(applicable_nodes) > 0:
                # we found the thing, but it's equipped. If this is the first find, it'll be
                # the error
                if first_guess_error is None:
                    guess_target = applicable_nodes[0]
                    guess_target_name = guess_target.get_prefix_view()
                    first_guess_error = ErrorEvent(
                        cls,
                        actor,
                        f"You can't steal {guess_target_name}, because they have it equipped.",
                        [guess_target],
                    )
            elif len(target_nodes) > 0:
                # we found a node, but it isn't the right one. if this is our first find, it'll be the error
                if first_guess_error is None:
                    guess_target = target_nodes[0]
                    guess_target_name = guess_target.get_prefix_view()
                    first_guess_error = ErrorEvent(
                        cls,
                        actor,
                        f"{guess_target_name}, isn't something you can steal.",
                        [guess_target],
                    )
        # didn't end up finding the thing
        if first_guess_error is not None:
            return first_guess_error
        return ErrorEvent(
            cls, actor, f"You can't find '{object_name}' here that you can steal."
        )

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["StealObjectEvent", "ErrorEvent"]:
        """Steal object events are valid as long as the agent can hold the object"""
        assert len(targets) == 2, f"StealObjectEvent takes two args, got {targets}"
        target, victim = targets
        assert (
            target in victim.get_contents()
        ), "Target node is not held by the given victim"
        if not actor.would_fit(target):
            return ErrorEvent(
                cls,
                actor,
                f"You can't steal {target.get_prefix_view()} because you can't carry that much more.",
            )
        return cls(actor, target_nodes=[target, victim], event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """
        Find all objects that are currently stealable in the given room for the given agent.
        """
        valid_actions: List[GraphEvent] = []
        # Add a possible steal for any stealable object from every agent
        room = actor.get_room()
        room_agents = [
            x for x in room.get_contents() if isinstance(x, GraphAgent) and x != actor
        ]

        for agent in room_agents:
            stealable_objects = [
                x
                for x in agent.get_contents()
                if isinstance(x, GraphObject) and not x.equipped
            ]
            for obj in stealable_objects:
                if actor.would_fit(obj):
                    valid_actions.append(cls(actor, target_nodes=[obj, agent]))

        return valid_actions

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return [
            "you",
            "tried",
            "to",
            "steal",
            "from",
            "but",
            "they",
            "were",
            "caught",
            "in",
            "the",
            "act",
            "stole",
        ]


class GiveObjectEvent(GraphEvent):
    """Handles giving an object to another agent"""

    NAMES = ["give"]
    TEMPLATES = ["give <gettable> to <agent>"]

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

        # Move the object over and broadcast
        put_target.move_to(self.target_nodes[1])
        world.broadcast_to_room(self)
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""

        if viewer == self.actor:
            actor_text = "You"
        else:
            actor_text = self.__actor_name
        recipient_text = self.__recipient_name
        if viewer == self.target_nodes[1]:
            recipient_text = "you"
        return f"{actor_text} gave {self.__given_name} to {recipient_text}."

    def to_canonical_form(self) -> str:
        """return action text for giving the object to the agent"""
        return f"give {self._canonical_targets[0]} to {self._canonical_targets[1]}"

    @classmethod
    def split_text_args(
        cls, actor: GraphAgent, text: str
    ) -> Union[List[List[str]], "ErrorEvent"]:
        """
        Return all possible interpretations for "give x to y".

        Must consider multiple to situations

        Also considers that the person may have written "give y x" if there is no "to"
        """
        possibilities = []
        possible_to_splits = text.split(" to ")
        for split_ind in range(len(possible_to_splits)):
            before = " to ".join(possible_to_splits[:split_ind])
            after = " to ".join(possible_to_splits[split_ind:])
            if len(after) > 0 and len(before) > 0:
                possibilities.append([before, after])
        if len(possibilities) == 0:
            possible_splits = text.split(" ")
            for split_ind in range(len(possible_splits)):
                before = " ".join(possible_to_splits[:split_ind])
                after = " ".join(possible_to_splits[split_ind:])
                if len(after) > 0 and len(before) > 0:
                    possibilities.append([before, after])

        if len(possibilities) == 0:
            return ErrorEvent(cls, actor, "You must give that to someone.")

        return possibilities

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for an object within the actor, and an agent in the room.
        """
        assert len(text_args) == 2, f"GiveObjectEvent takes two args, got {text_args}"
        object_name, recipient_name = text_args
        target_nodes = graph.desc_to_nodes(recipient_name, actor, "all+here")
        possible_agents = [x for x in target_nodes if isinstance(x, GraphAgent)]
        if len(possible_agents) == 0:
            # didn't find any nodes by this name
            return ErrorEvent(
                cls,
                actor,
                f"You can't find '{recipient_name}' here that you can give to.",
            )

        # check actor to see if they have the node to give
        target_nodes = graph.desc_to_nodes(object_name, actor, "carrying")
        applicable_nodes = [x for x in target_nodes if isinstance(x, GraphObject)]
        unequipped_nodes = [x for x in applicable_nodes if not x.equipped]
        if len(unequipped_nodes) > 0:
            # we found the thing!
            return ProcessedArguments(targets=[unequipped_nodes[0], possible_agents[0]])
        if len(applicable_nodes) > 0:
            # we found the thing, but it's equipped
            guess_target = applicable_nodes[0]
            guess_target_name = guess_target.get_prefix_view()
            return ErrorEvent(
                cls,
                actor,
                f"You could give {guess_target_name}, but you'll have to remove it first.",
                [guess_target],
            )
        elif len(target_nodes) > 0:
            # we found a node, but it isn't the right one.
            guess_target = target_nodes[0]
            guess_target_name = guess_target.get_prefix_view()
            return ErrorEvent(
                cls,
                actor,
                f"{guess_target_name}, isn't something you can give.",
                [guess_target],
            )
        return ErrorEvent(cls, actor, f"You don't have '{object_name}' to give.")

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["GiveObjectEvent", "ErrorEvent"]:
        """give object events are valid as long as the recipient can hold the object"""
        assert len(targets) == 2, f"GiveObjectEvent takes two args, got {targets}"
        target, recipient = targets
        assert target in actor.get_contents(), "Target node is not held by actor"
        if not recipient.would_fit(target):
            return ErrorEvent(
                cls,
                actor,
                f"You can't give {target.get_prefix_view()} to {recipient.get_prefix_view()} because there's they don't have room for it.",
            )
        return cls(actor, target_nodes=[target, recipient], event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """
        Find all objects that can be given to all agents
        """
        valid_actions: List[GraphEvent] = []
        # get all the give-able objects
        giveable_objects = [
            x
            for x in actor.get_contents()
            if isinstance(x, GraphObject) and not x.equipped
        ]
        if len(giveable_objects) == 0:
            return []

        possible_agents = [
            x for x in actor.get_room().get_contents() if isinstance(x, GraphAgent)
        ]
        possible_agents = [x for x in possible_agents if x != actor]
        # Try to give all objects to all agents
        for obj in giveable_objects:
            for agent in possible_agents:
                if agent.would_fit(obj):
                    valid_actions.append(cls(actor, target_nodes=[obj, agent]))

        return valid_actions

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "gave", "to"]


class EquipObjectEvent(GraphEvent):
    """Handles equipping a held object"""

    NAMES = ["equip"]
    TEMPLATES = ["equip <wearable|wieldable>"]

    action_name = "equipped"
    past_tense_action_name = "equipped"

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, move the item from the actor to the room
        """
        assert not self.executed
        # Populate for views
        self._actor_name = self.actor.get_prefix_view()
        equip_target = self.target_nodes[0]
        self._equip_name = equip_target.get_prefix_view()

        # Move the object over and broadcast
        assert isinstance(
            equip_target, GraphObject
        ), f"Can only equip GraphObjects, not {equip_target}"
        # The current children of EquipObjectEvent have ONLY one name.
        # Joining for any future possibility that may have more than one.
        equip_target.equipped = ",".join(self.NAMES)
        for n, s in equip_target.get_prop("stats", {"defense": 1}).items():
            self.actor.set_prop(n, self.actor.get_prop(n) + s)
        if equip_target.wieldable:
            self.actor.num_wieldable_items += 1
        else:
            self.actor.num_wearable_items += 1
        world.broadcast_to_room(self)
        self.executed = True
        return []

    @classmethod
    def can_equip(cls, object_node: GraphObject) -> bool:
        return object_node.wearable or object_node.wieldable

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            actor_text = "You"
        else:
            actor_text = self._actor_name
        return f"{actor_text} {self.action_name} {self._equip_name}."

    def to_canonical_form(self) -> str:
        """return action text for equipping the object"""
        return f"{self.NAMES[0]} {self._canonical_targets[0]}"

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for an equippable object within the actor.
        """
        assert len(text_args) == 1, f"EquipObjectEvents takes one arg, got {text_args}"
        object_name = text_args[0]
        # check actor to see if the wanted object is within
        carrying_nodes = graph.desc_to_nodes(object_name, actor, "carrying")
        target_nodes = [x for x in carrying_nodes if isinstance(x, GraphObject)]
        applicable_nodes = [x for x in target_nodes if cls.can_equip(x)]
        if len(applicable_nodes) > 0:
            # we found the thing!
            return ProcessedArguments(targets=[applicable_nodes[0]])
        elif len(target_nodes) > 0:
            # we found a node, but it isn't the right one.
            guess_target = target_nodes[0]
            guess_target_name = guess_target.get_prefix_view()
            return ErrorEvent(
                cls,
                actor,
                f"{guess_target_name} isn't something you can {cls.NAMES[0]}.",
                [guess_target],
            )
        return ErrorEvent(
            cls, actor, f"You don't have '{object_name}' to {cls.NAMES[0]}."
        )

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["EquipObjectEvent", "ErrorEvent"]:
        """Equip object events are valid as long as an equippable object was found"""
        assert len(targets) == 1, f"EquipObjectEvent takes one arg, got {targets}"
        target = targets[0]
        assert (
            target in actor.get_contents()
        ), "Target node is not in the given container"
        assert isinstance(
            target, GraphObject
        ), f"Can only be equipping objects, not {target}"
        if target.wieldable and actor.num_wieldable_items >= actor.max_wieldable_items:
            return ErrorEvent(cls, actor, "You can't wield any more items!")
        if target.wearable and actor.num_wearable_items >= actor.max_wearable_items:
            return ErrorEvent(cls, actor, "You can't wear any more items!")
        if target.equipped is not None:
            return ErrorEvent(
                cls,
                actor,
                f"You already have {target.get_prefix_view()} equipped!",
                [target],
            )
        return cls(actor, target_nodes=[target], event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """Get all valid equip actions"""
        valid_actions: List[GraphEvent] = []
        # get all the give-able objects
        held_objects = [
            x
            for x in actor.get_contents()
            if isinstance(x, GraphObject) and not x.equipped
        ]
        if len(held_objects) == 0:
            return []

        for obj in held_objects:
            if cls.can_equip(obj):
                valid_actions.append(cls(actor, target_nodes=[obj]))

        return valid_actions


class WearEvent(EquipObjectEvent):
    """Handles wearing a held object"""

    NAMES = ["wear"]
    TEMPLATES = ["wear <wearable>"]

    action_name = "wore"
    past_tense_action_name = "worn"

    @classmethod
    def can_equip(cls, object_node: GraphObject) -> bool:
        return object_node.wearable

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "wore"]


class WieldEvent(EquipObjectEvent):
    """Handles wielding a held object"""

    NAMES = ["wield"]
    TEMPLATES = ["wield <wieldable>"]

    action_name = "wielded"
    past_tense_action_name = "wielded"

    @classmethod
    def can_equip(cls, object_node: GraphObject) -> bool:
        return object_node.wieldable

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "wielded"]


class RemoveObjectEvent(GraphEvent):
    """Handles removing an equipped object"""

    NAMES = ["remove", "unwield"]
    TEMPLATES = ["remove <wearable|wieldable>"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, move the item from the actor to the room
        """
        assert not self.executed
        # Populate for views
        self._actor_name = self.actor.get_prefix_view()
        equip_target = self.target_nodes[0]
        self._equip_name = equip_target.get_prefix_view()

        # Remove the object and broadcast
        assert isinstance(
            equip_target, GraphObject
        ), f"Can only remove GraphObjects, not {equip_target}"
        equip_target.equipped = None
        if equip_target.wieldable:
            self.actor.num_wieldable_items -= 1
        else:
            self.actor.num_wearable_items -= 1
        for n, s in equip_target.get_prop("stats", {"defense": 1}).items():
            self.actor.set_prop(n, self.actor.get_prop(n) - s)
        world.broadcast_to_room(self)
        self.executed = True
        return []

    @classmethod
    def can_equip(cls, object_node: GraphObject) -> bool:
        return object_node.wearable or object_node.wieldable

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            actor_text = "You"
        else:
            actor_text = self._actor_name
        return f"{actor_text} removed {self._equip_name}."

    def to_canonical_form(self) -> str:
        """return action text for equipping the object"""
        return f"{self.NAMES[0]} {self._canonical_targets[0]}"

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for an equippable object within the actor.
        """
        assert len(text_args) == 1, f"RemoveObjectEvent takes one arg, got {text_args}"
        object_name = text_args[0]
        # check actor to see if the wanted object is within
        carrying_nodes = graph.desc_to_nodes(object_name, actor, "carrying")
        target_nodes = [x for x in carrying_nodes if isinstance(x, GraphObject)]
        applicable_nodes = [
            x for x in target_nodes if x.get_prop("equipped") is not False
        ]
        if len(applicable_nodes) > 0:
            # we found the thing!
            return ProcessedArguments(targets=[applicable_nodes[0]])
        elif len(target_nodes) > 0:
            # we found a node, but it's not removable. Still return the event to fail later
            return ProcessedArguments(targets=[target_nodes[0]])
            guess_target = target_nodes[0]
            guess_target_name = guess_target.get_prefix_view()
            return ErrorEvent(
                cls,
                actor,
                f"{guess_target_name}, isn't something you have equipped.",
                [guess_target],
            )
        return ErrorEvent(
            cls, actor, f"You don't have '{object_name}' to {cls.NAMES[0]}."
        )

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["RemoveObjectEvent", "ErrorEvent"]:
        """Remove object events are valid as long as an equipped object was found"""
        assert len(targets) == 1, f"RemoveObjectEvent takes one arg, got {targets}"
        target = targets[0]
        assert (
            target in actor.get_contents()
        ), "Target node is not in the given container"
        assert isinstance(
            target, GraphObject
        ), f"Can only remove GraphObjects, not {target}"
        if not target.equipped:
            guess_target_name = target.get_prefix_view()
            return ErrorEvent(
                cls,
                actor,
                f"{guess_target_name}, isn't something you have equipped.",
                [target],
            )
        return cls(actor, target_nodes=[target], event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """Get all valid equip actions"""
        valid_actions: List[GraphEvent] = []
        # get all the give-able objects
        held_objects = [x for x in actor.get_contents() if isinstance(x, GraphObject)]
        if len(held_objects) == 0:
            return []

        for obj in held_objects:
            if obj.equipped:
                valid_actions.append(cls(actor, target_nodes=[obj]))

        return valid_actions

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "removed"]


class IngestEvent(GraphEvent):
    """Handles equipping a held object"""

    NAMES = ["ingest"]
    TEMPLATES = ["ingest <food|drink>"]

    past_tense_action_name = "ingested"

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, delete the item and confer its effects
        """
        assert not self.executed
        # Populate for views
        self._actor_name = self.actor.get_prefix_view()
        ingest_target = self.target_nodes[0]
        assert isinstance(
            ingest_target, GraphObject
        ), f"Must ingest an object, not {ingest_target}"
        self._ingest_name = ingest_target.get_prefix_view()

        # Move the object over and broadcast
        fe = ingest_target.food_energy
        self._outcome = "Yum. " if fe > 0 else "Gross! "
        if hasattr(world.oo_graph, "void"):
            ingest_target.move_to(world.oo_graph.void)
        world.oo_graph.mark_node_for_deletion(ingest_target.node_id)

        world.broadcast_to_room(self)

        health_text = world.view.get_health_text_for(self.actor.node_id)
        self.actor.health = max(self.actor.health + fe, 0)
        new_health_text = world.view.get_health_text_for(self.actor.node_id)
        if self.actor.health <= 0:
            DeathEvent(self.actor).execute(world)
        elif health_text != new_health_text:
            HealthEvent(self.actor, text_content="HealthOnIngestEvent").execute(world)

        self.executed = True
        return []

    @classmethod
    def can_ingest(cls, object_node: GraphObject) -> bool:
        return object_node.drink or object_node.food

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return f"You {self.past_tense_action_name} {self._ingest_name}. {self._outcome}"
        else:
            return (
                f"{self._actor_name} {self.past_tense_action_name} {self._ingest_name}."
            )

    def to_canonical_form(self) -> str:
        """return action text for equipping the object"""
        return f"{self.NAMES[0]} {self._canonical_targets[0]}"

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for an equippable object within the actor.
        """
        assert len(text_args) == 1, f"IngestEvent takes one arg, got {text_args}"
        object_name = text_args[0]
        # check actor to see if the wanted object is within
        carrying_nodes = graph.desc_to_nodes(object_name, actor, "carrying")
        target_nodes = [x for x in carrying_nodes if isinstance(x, GraphObject)]
        applicable_nodes = [x for x in target_nodes if cls.can_ingest(x)]
        if len(applicable_nodes) > 0:
            # we found the thing!
            return ProcessedArguments(targets=[applicable_nodes[0]])
        elif len(target_nodes) > 0:
            # we found a node, but it isn't the right one. Still return
            return ProcessedArguments(targets=[target_nodes[0]])
        return ErrorEvent(
            cls, actor, f"You don't have '{object_name}' to {cls.NAMES[0]}."
        )

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["IngestEvent", "ErrorEvent"]:
        """Equip object events are valid as long as an equippable object was found"""
        assert len(targets) == 1, f"IngestEvent takes one arg, got {targets}"
        target = targets[0]
        assert (
            target in actor.get_contents()
        ), "Target node is not in the given container"
        assert isinstance(target, GraphObject), f"Must ingest an object, not {target}"
        if not cls.can_ingest(target):
            guess_target_name = target.get_prefix_view()
            return ErrorEvent(
                cls,
                actor,
                f"{guess_target_name}, isn't something you can {cls.NAMES[0]}.",
                [target],
            )
        return cls(actor, target_nodes=[target], event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """Get all valid ingest actions"""
        valid_actions: List[GraphEvent] = []
        # get all the give-able objects
        held_objects = [x for x in actor.get_contents() if isinstance(x, GraphObject)]
        if len(held_objects) == 0:
            return []

        for obj in held_objects:
            if cls.can_ingest(obj):
                valid_actions.append(cls(actor, target_nodes=[obj]))

        return valid_actions


class EatEvent(IngestEvent):
    """Handles eating a held object"""

    NAMES = ["eat"]
    TEMPLATES = ["eat <food>"]

    past_tense_action_name = "ate"

    @classmethod
    def can_ingest(cls, object_node: GraphObject) -> bool:
        return object_node.food

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "ate", "yum", "gross"]


class DrinkEvent(IngestEvent):
    """Handles eating a held object"""

    NAMES = ["drink"]
    TEMPLATES = ["drink <drink>"]

    past_tense_action_name = "drank"

    @classmethod
    def can_ingest(cls, object_node: GraphObject) -> bool:
        return object_node.drink

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "drank", "yum", "gross"]


class LockableEvent(GraphEvent):
    """Handles locking and unlocking edges and containers with appropriate keys"""

    """Handles locking an edge/container with the appropriate key"""

    NAMES: List[str] = []  # must be overridden with locking and unlocking

    @classmethod
    def is_correct_lock_status(cls, lock_edge: "LockEdge") -> bool:
        raise NotImplementedError

    @classmethod
    def process_locking(cls, lock_edge: "LockEdge") -> None:
        raise NotImplementedError

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, lock the target node
        """
        assert not self.executed
        self._actor_name = self.actor.get_prefix_view()
        lock_target = self.target_nodes[0]
        assert isinstance(
            lock_target, GraphObject
        ), f"Must lock an object, not {lock_target}"
        self._locked_name = lock_target.get_prefix_view_from(self.room)
        self._key_name = self.target_nodes[1].get_prefix_view()

        lock_edge = None
        if lock_target.room:
            neighbor_to_lock = self.room.get_edge_to(lock_target)
            assert neighbor_to_lock is not None, "Target doesn't exist"
            lock_edge = neighbor_to_lock.locked_edge
        elif lock_target.object and lock_target.container:
            lock_edge = lock_target.locked_edge
        else:
            raise AssertionError("Cannot lock a non-lockable thing")
        assert lock_edge is not None, "Cannot lock a non-lockable thing"

        self.process_locking(lock_edge)

        world.broadcast_to_room(self)
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            viewer_text = "You"
        else:
            viewer_text = self._actor_name
        return f"{viewer_text} {self.NAMES[0]}ed {self._locked_name} with {self._key_name}."

    def to_canonical_form(self) -> str:
        """return action text for putting the object in/on the container"""
        return f"{self.NAMES[0]} {self._canonical_targets[0]} with {self._canonical_targets[1]}"

    @classmethod
    def split_text_args(
        cls, actor: GraphAgent, text: str
    ) -> Union[List[List[str]], "ErrorEvent"]:
        """
        Return all possible interpretations for "lock x with y".

        Must consider multiple with situations
        """
        if " with " not in text:
            return ErrorEvent(
                cls, actor, f"You must `{cls.NAMES[0]} <something> with <key>`."
            )
        possibilities = []
        possible_with_splits = text.split(" with ")
        for split_ind in range(len(possible_with_splits)):
            before = " with ".join(possible_with_splits[:split_ind])
            after = " with ".join(possible_with_splits[split_ind:])
            if len(after) > 0 and len(before) > 0:
                possibilities.append([before, after])
        return possibilities

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for a lockable thing in the room or carried by the actor, and a key within the actor.
        """
        assert len(text_args) == 2, f"LockableEvents take two arg, got {text_args}"
        lockable_name, key_name = text_args

        curr_room = actor.get_room()
        possible_keys = graph.desc_to_nodes(key_name, actor, "carrying")
        possible_key_objects = [x for x in possible_keys if x.object]

        if len(possible_keys) == 0:
            return ErrorEvent(
                cls,
                actor,
                f"You don't have `{key_name}` to use to {cls.NAMES[0]} anything",
            )

        possible_lockable_rooms = graph.desc_to_nodes(
            lockable_name, actor.get_room(), "path"
        )
        rooms_with_edges = [
            (x, curr_room.get_edge_to(x)) for x in possible_lockable_rooms
        ]
        definitely_lockable_rooms = [
            (room, edge)
            for (room, edge) in rooms_with_edges
            if edge is not None and edge.locked_edge is not None
        ]

        possible_lockable_objects = [
            x
            for x in graph.desc_to_nodes(lockable_name, actor, "carrying+sameloc")
            if x.object
        ]
        definitely_lockable_objects = [
            x for x in possible_lockable_objects if x.locked_edge is not None
        ]

        if len(definitely_lockable_objects) > 0:
            # Found a lockable object, see if it matches any key
            for lockable_object in definitely_lockable_objects:
                matching_key = lockable_object.locked_edge.get()
                for possible_key in possible_key_objects:
                    if matching_key == possible_key:
                        return ProcessedArguments(
                            targets=[lockable_object, possible_key]
                        )
            # no keys matched any object, so fail with the first ones
            return ErrorEvent(
                cls,
                actor,
                f"You can't use {possible_key_objects[0].get_prefix_view()} to {cls.NAMES[0]} {definitely_lockable_objects[0].get_prefix_view()}.",
            )
        elif len(definitely_lockable_rooms) > 0:
            # Found a lockable room, see if it matches any key
            for (lockable_room, edge) in definitely_lockable_rooms:
                matching_key = edge.locked_edge.get()
                for possible_key in possible_key_objects:
                    if matching_key == possible_key:
                        return ProcessedArguments(
                            targets=[lockable_object, possible_key]
                        )
            # no keys matched any object, so fail with the first ones
            return ErrorEvent(
                cls,
                actor,
                f"You can't use {possible_key_objects[0].get_prefix_view()} to {cls.NAMES[0]} {definitely_lockable_rooms[0][0].get_prefix_view_from(curr_room)}.",
            )
        elif len(possible_lockable_objects) > 0:
            # We found an object, but it's not lockable
            return ErrorEvent(
                cls,
                actor,
                f"You can't lock {possible_lockable_objects[0].get_prefix_view()} because it's not lockable",
            )
        elif len(definitely_lockable_rooms) > 0:
            # Found a matching room, but it's not lockable
            return ErrorEvent(
                cls,
                actor,
                f"You can't lock {possible_lockable_rooms[0].get_prefix_view_from(curr_room)} because it's not lockable",
            )

        return ErrorEvent(
            cls, actor, f"You can't find '{lockable_name}' here to {cls.NAMES[0]}."
        )

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["LockableEvent", "ErrorEvent"]:
        """Lock object events are valid as long as the target is unlocked"""
        assert len(targets) == 1, f"LockableEvent takes one arg, got {targets}"
        target_node, key_node = targets
        assert key_node in actor.get_contents(), "Actor not carrying key"
        assert isinstance(
            target_node, GraphObject
        ), f"Must lock an object, not {target_node}"
        edge = None
        if target_node.room:
            edge = actor.get_room().get_edge_to(target_node).locked_edge
        elif target_node.object:
            edge = target_node.locked_edge
        else:
            raise AssertionError("Node to lock is not a room or a container")

        if not cls.is_correct_lock_status(edge):
            # Found a lockable node, but it's not the correct status
            return ErrorEvent(
                cls,
                actor,
                f"You can't {cls.NAMES[0]} {target_node.get_prefix_view_from(actor.get_room())} because it's already {cls.NAMES[0]}ed",
            )
        return cls(actor, target_nodes=[target_node, key_node], event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """
        Find all lockable containers, and see if the agent has the key for it
        """
        curr_room = actor.get_room()
        possible_keys = actor.get_contents()
        if len(possible_keys) == 0:
            # early exit
            return []

        possible_lockable_rooms = curr_room.get_neighbors()
        rooms_with_edges = [
            (x, curr_room.get_edge_to(x)) for x in possible_lockable_rooms
        ]
        definitely_lockable_rooms = [
            (room, edge)
            for (room, edge) in rooms_with_edges
            if edge.locked_edge is not None
        ]
        correct_lockable_rooms = [
            (room, edge)
            for (room, edge) in definitely_lockable_rooms
            if cls.is_correct_lock_status(edge)
        ]
        correct_room_pairs = [
            (room, edge.get_path_locked_with())
            for (room, edge) in correct_lockable_rooms
        ]

        possible_lockable_objects = actor.get_contents() + [
            x for x in curr_room.get_contents() if x.object
        ]
        definitely_lockable_objects = [
            x for x in possible_lockable_objects if x.locked_edge is not None
        ]
        correct_lockable_objects = [
            x
            for x in possible_lockable_objects
            if not cls.is_correct_lock_status(x.locked_edge)
        ]
        correct_object_pairs = [
            (x, x.locked_edge.get()) for x in correct_lockable_objects
        ]

        all_correct_pairs = correct_room_pairs + correct_object_pairs

        valid_actions: List[GraphEvent] = []
        for (lockable, key) in all_correct_pairs:
            if key in possible_keys:
                valid_actions.append(cls(actor, target_nodes=[lockable, key]))

        return valid_actions


class LockEvent(LockableEvent):
    """Handles locking an edge/container with the appropriate key"""

    NAMES = ["lock"]

    @classmethod
    def is_correct_lock_status(cls, lock_edge: "LockEdge") -> bool:
        return lock_edge.get_is_locked() is False

    @classmethod
    def process_locking(cls, lock_edge: "LockEdge") -> None:
        lock_edge.lock()


class UnlockEvent(GraphEvent):
    """Handles unlocking an edge/container with the appropriate key"""

    NAMES = ["unlock"]

    @classmethod
    def is_correct_lock_status(cls, lock_edge: "LockEdge") -> bool:
        return lock_edge.get_is_locked() is True

    @classmethod
    def process_locking(cls, lock_edge: "LockEdge") -> None:
        lock_edge.unlock()


def actor_has_no_recent_action(last_time_acted, current_time):
    # After 2 minutes we consider an agent to be "dozing off".
    time_elapsed = current_time - last_time_acted
    return time_elapsed > 60 * 2


# TODO handle locked objects
class ExamineEvent(GraphEvent):
    """Handles displaying examine/extra text for a graph node"""

    NAMES = ["examine", "ex", "inspect"]
    TEMPLATES = ["examine <agent|room|object>"]

    def _get_target_description(self, world: "World") -> str:
        """Get the examine description for the given target"""
        target = self.target_nodes[0]
        room_id = self.room.node_id
        object_id = target.node_id
        actor_id = self.actor.node_id
        if isinstance(target, GraphRoom):
            return world.view.get_path_ex_desc(room_id, object_id, actor_id)
        base_desc = target.desc
        if isinstance(target, GraphAgent):
            inv_text = world.view.get_inventory_text_for(object_id, give_empty=False)
            if inv_text != "":
                base_desc += f"\n{self.__target_name} is {inv_text} "
            if (
                self.target_nodes[0].is_player
                and hasattr(self.target_nodes[0], "_last_action_time")
                and actor_has_no_recent_action(
                    self.target_nodes[0]._last_action_time, time.time()
                )
            ):
                base_desc += "\nThey appear to be dozing off right now."
        elif isinstance(target, GraphObject) and target.container:
            if len(target.get_contents()) > 0:
                base_desc += f"\n{world.display_node(object_id)} "
        return base_desc

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, move the item from the actor to the room
        """
        assert not self.executed
        # Populate for views
        self.__actor_name = self.actor.get_prefix_view()
        self.__target_name = proper_caps(self.target_nodes[0].get_prefix_view())
        self.__examine_text = self._get_target_description(world)

        # Move the object over and broadcast
        world.broadcast_to_room(self)
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__examine_text
        elif self.target_nodes[0] == viewer:
            return f"{self.__actor_name} examined you."
        else:
            return f"{self.__actor_name} examined {self.__target_name}."

    def to_canonical_form(self) -> str:
        """return action text for dropping the object"""
        return f"examine {self._canonical_targets[0]}"

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for an object within the actor.
        """
        assert len(text_args) == 1, f"ExamineEvent takes one arg, got {text_args}"
        object_name = text_args[0]

        all_nodes = graph.desc_to_nodes(object_name, actor, "all+here")
        rooms_too = graph.desc_to_nodes(object_name, actor, "path")
        applicable_nodes = all_nodes + rooms_too
        if len(applicable_nodes) > 0:
            return ProcessedArguments(targets=[applicable_nodes[0]])
        return ErrorEvent(cls, actor, f"You don't see '{object_name}' here to examine.")

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> "ExamineEvent":
        """Examine events are always valid if constructed"""
        return cls(actor, target_nodes=targets, event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """
        Find all objects that are currently examinable in the given room for the given agent.
        """
        room = actor.get_room()
        examineable_here = actor.get_contents() + room.get_contents() + [room]
        examinable_paths = room.get_neighbors()
        examinable_all = examineable_here + examinable_paths

        valid_actions: List[GraphEvent] = []
        # examine all of the things here
        if len(examinable_all) == 0:
            return []

        # Try to examine everything
        for obj in examinable_all:
            valid_actions.append(cls(actor, target_nodes=[obj]))

        return valid_actions

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return [
            "you",
            "examine",
            "they",
            "appear",
            "to",
            "be",
            "dozing",
            "off",
            "right",
            "now",
        ]


class EmoteEvent(GraphEvent):
    """Handles ending an emotion to the room."""

    NAMES = ["emote"]

    DESC_MAP = {
        "applaud": "applauds",
        "blush": "blushes",
        "cry": "cries",
        "dance": "dances",
        "frown": "frowns",
        "gasp": "gasps",
        "grin": "grins",
        "groan": "groans",
        "growl": "growls",
        "laugh": "laughs",
        "nod": "nods",
        "nudge": "nudges",
        "ponder": "ponders",
        "pout": "pouts",
        "scream": "screams",
        "shrug": "shrugs",
        "sigh": "sighs",
        "smile": "smiles",
        "stare": "stares",
        "wave": "waves",
        "wink": "winks",
        "yawn": "yawns",
    }

    TEMPLATES = [f"emote {e}" for e in DESC_MAP.keys()]

    def execute(self, world: "World") -> List[GraphEvent]:
        """On execution, store the expected views, then broadcast"""
        assert not self.executed
        assert self.text_content is not None, "Cannot emote without text_context"
        actor_name = self.actor.get_prefix_view()
        self.__display_action = self.DESC_MAP[self.text_content]
        self.__in_room_view = f"{actor_name} {self.__display_action}."
        self.__self_view = f"You {self.text_content}."
        world.broadcast_to_room(self, exclude_agents=[self.actor])
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__self_view
            # None  # One should not observe themself emoting
        else:
            return self.__in_room_view

    def to_canonical_form(self) -> str:
        """
        Provide the text that this event's actor would use to invoke this event
        """
        return f"emote {self.text_content}"

    @classmethod
    def split_text_args(cls, actor: GraphAgent, text: str) -> List[List[str]]:
        """Anything after the "emote" would be what is being emoted"""
        return [[text.strip()]]

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["EmoteEvent", "ErrorEvent"]:
        """Emote events are valid if the emote is valid."""
        if text is None or text not in cls.DESC_MAP:
            all_emotes = ", ".join(cls.DESC_MAP.keys()) + "."
            return ErrorEvent(
                cls,
                actor,
                f"What emotion is that? At the moment light denizens can only show the following gestures:\n{all_emotes}",
            )
        return cls(actor, text_content=text, event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """
        Return all currently possible emotes.
        """
        valid_actions: List[GraphEvent] = []

        # Try to examine everything
        for x in cls.DESC_MAP.keys():
            valid_actions.append(cls(actor, text_content=x))

        return valid_actions

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you"] + list(cls.DESC_MAP.values()) + list(cls.DESC_MAP.keys())


class WaitEvent(NoArgumentEvent):
    """Wait events just allow a player to do nothing in a timestep"""

    NAMES = ["wait"]
    TEMPLATES = ["wait"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, broadcast the nothing happening
        """
        assert not self.executed
        self.__actor_name = self.actor.get_prefix_view()
        world.broadcast_to_room(self)
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return "You waited."
        else:
            return f"{self.__actor_name} waited."

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "waited"]


class InventoryEvent(NoArgumentEvent):
    """Inventory events just allow a player see what they are carrying, etc."""

    NAMES = ["inventory", "inv", "i"]
    TEMPLATES = ["inventory"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, get the items the actor is carrying to display
        """
        assert not self.executed
        self.__actor_name = self.actor.get_prefix_view()
        self.__inv_text = world.view.get_inventory_text_for(self.actor.node_id)

        world.broadcast_to_agents(self, [self.actor])
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return (
                f"You check yourself. You are {self.__actor_name}!\n"
                f"You are {self.__inv_text}\n"
            )
        else:
            return f"{self.__actor_name} checked their inventory."

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "check", "yourself", "are", "checked", "their", "inventory"]


class QuestEvent(NoArgumentEvent):
    """Quest events just allow a player to see their assigned quests."""

    NAMES = ["quest", "quests", "mission", "missions", "goal", "goals", "q"]
    TEMPLATES = ["quests"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, show the quests
        """
        assert not self.executed
        self.__actor_name = self.actor.get_prefix_view() + "!"
        self.__quests_text = ""

        if hasattr(self.actor, "persona"):
            self.__actor_name += "\nYour Persona: " + self.actor.persona + "\n"

        if hasattr(self.actor, "quests"):
            quests = self.actor.quests
            if quests is None or len(quests) == 0:
                self.__quests_text += (
                    "You currently have no quests. Talk to people to get some!"
                )
            else:
                for q in quests:
                    if q["actor"] == self.actor.node_id:
                        self.__quests_text += "Your current quest: " + q["text"] + "\n"
                for q in quests:
                    if q["actor"] != self.actor.node_id:
                        self.__quests_text += (
                            "Quest to help "
                            + q["actor_str"]
                            + ': "'
                            + q["text"]
                            + '"\n'
                        )

        world.broadcast_to_agents(self, [self.actor])
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return (f"{self.__quests_text}\n").replace("\n\n", "\n")
        else:
            return None  # f"{self.__actor_name} looks deep in thought. "

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return [
            "you",
            "currently",
            "have",
            "no",
            "quests",
            "talk",
            "to",
            "people",
            "get",
            "some",
            "help",
            "quest",
            "current",
        ]


class RewardEvent(GraphEvent):
    """Reward events allow to give another agent XP."""

    NAMES = ["reward", "r"]
    TEMPLATES = ["reward <agent>"]

    def __init__(
        self,
        actor: GraphAgent,
        target_nodes: Optional[List[GraphNode]] = None,
        text_content: Optional[str] = None,
        event_id: Optional[str] = None,
        target_event_id: Optional[str] = None,
    ):
        super().__init__(
            actor,
            target_nodes=target_nodes,
            text_content=text_content,
            event_id=event_id,
        )
        # Must store the target event, if this was provided
        self.target_event_id = target_event_id

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, pass along the reward if possible
        """
        assert not self.executed
        self.__actor_name = self.actor.get_prefix_view()
        agent = self.target_nodes[0]
        self.recipient = agent
        self.__recipient_name = agent.get_prefix_view()
        if not hasattr(agent, "xp"):
            agent.xp = 0
            agent.reward_xp = 0
        if not hasattr(self.actor, "xp"):
            self.actor.xp = 10
            self.actor.reward_xp = 0
        if self.actor.reward_xp > 0:
            self.actor.reward_xp -= 1
            stars = 4
            agent.xp += stars
            agent.reward_xp += stars / 4.0
            rewards = math.floor(self.actor.reward_xp)
            if rewards == 1:
                self.__reward_xp = "1 reward"
            else:
                self.__reward_xp = str(math.floor(self.actor.reward_xp)) + " rewards"
            self.__gain_xp = str(stars)
            self.failed = False
        else:
            self.failed = True
        world.broadcast_to_agents(self, [self.actor])
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if self.failed:
            if viewer == self.actor:
                return f"You don't have any rewards to give. Earn some XP first!"
            else:
                return []

        if viewer == self.actor:
            return (
                f"You rewarded {self.__recipient_name}!\n"
                f"You have {self.__reward_xp} left to give.\n"
            )
        elif viewer == self.recipient:
            return (
                f"{self.__actor_name} rewarded you! (You gained {self.__gain_xp} XP!!)"
            )
        else:
            return []

    def to_canonical_form(self) -> str:
        """
        Provide the text that this event's actor would use to invoke this event
        """
        return f"reward {self._canonical_targets[0]}"

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for an agent in the same room.
        """
        assert len(text_args) == 1, f"RewardEvent takes one arg, got {text_args}"
        target_name = text_args[0]
        target_nodes = graph.desc_to_nodes(target_name, actor, "sameloc")
        applicable_nodes = [x for x in target_nodes if x.agent]
        if len(applicable_nodes) > 0:
            return ProcessedArguments(targets=[applicable_nodes[0]])
        elif len(target_nodes) > 0:
            guess_target = target_nodes[0]
            return ErrorEvent(
                cls,
                actor,
                f"You could try and reward {guess_target.get_prefix_view()}, but it won't do anything.",
                [guess_target],
            )
        else:
            return ErrorEvent(
                cls, actor, f"You can't find '{target_name}' here that you can reward."
            )

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["RewardEvent", "ErrorEvent"]:
        """Reward events with a target agent will always be valid."""
        assert len(targets) == 1, f"RewardEvent takes one arg, got {targets}"
        target = targets[0]
        assert target.agent, "Can only reward agents"
        return cls(actor, target_nodes=[target], event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """
        Return any valid actions that can be taken by the given actor
        over the current graph. Default returns no events.
        """
        valid_actions: List[GraphEvent] = []
        room = actor.get_room()
        room_nodes = room.get_contents()
        room_agents = [x for x in room_nodes if x.agent]
        for agent in room_agents:
            if agent != actor:
                valid_actions.append(cls(actor, target_nodes=[agent]))
        return valid_actions

    def to_frontend_form(self, viewer: "GraphAgent") -> Dict[str, Any]:
        frontend_form = super().to_frontend_form(viewer)
        frontend_form["target_event_id"] = self.target_event_id
        return frontend_form


class HealthEvent(NoArgumentEvent):
    """Inventory events just allow a player to do nothing in a timestep"""

    NAMES = ["health", "status", "stats"]
    TEMPLATES = ["health"]

    _SIZE_TEXTS = [
        "huge",
        "quite large",
        "average in size",
        "below average in size",
        "quite small",
        "absolutely tiny",
    ]
    _ATTRIBUTE_VALUE_STRINGS = [
        "extremely strong",
        "very strong",
        "strong",
        "well above average",
        "above average",
        "average",
        "below average",
        "well below average",
        "weak",
        "very weak",
        "extremely weak",
    ]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, get the actor name and their current health
        """
        assert not self.executed
        self.__actor_name = self.actor.get_prefix_view()
        self.__health_text = world.view.get_health_text_for(self.actor.node_id)
        to_agents = [self.actor]
        for t in self.target_nodes:
            to_agents.append(t)
        world.broadcast_to_agents(self, to_agents)
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        health_text, sentiment = self.__health_text
        if viewer == self.actor:
            s = ""
            if self.text_content is None:
                xp = 0
                rxp = 0
                if hasattr(self.actor, "xp"):
                    xp = self.actor.xp
                if hasattr(self.actor, "reward_xp"):
                    rxp = self.actor.reward_xp
                s += f"Experience Points: {xp}\n"
                s += f"Rewards left to give: {rxp}\n"
            elif self.text_content == "HealthOnMoveEvent":
                s += "You are getting tired from your travels. "
            s += f"You are currently feeling {health_text}."
        else:
            verb = "looks"
            if sentiment > 0:
                verb = "still looks"
            return f"{self.__actor_name} {verb} {health_text}."
        if viewer == self.actor and self.text_content is None:
            # actual self "health" call, show dexterity and strength options as well.
            size = self.actor.size
            size_txt = self._SIZE_TEXTS[2]
            if size > 30:
                size_txt = self._SIZE_TEXTS[0]
            if size > 20:
                size_txt = self._SIZE_TEXTS[1]
            if size < 10:
                size_txt = self._SIZE_TEXTS[3]
            if size < 5:
                size_txt = self._SIZE_TEXTS[4]
            if size <= 1:
                size_txt = self._SIZE_TEXTS[5]

            def txt2num(strength):
                strength_txt = self._ATTRIBUTE_VALUE_STRINGS[5]
                if strength > 0:
                    strength_txt = self._ATTRIBUTE_VALUE_STRINGS[4]
                if strength > 1:
                    strength_txt = self._ATTRIBUTE_VALUE_STRINGS[3]
                if strength > 3:
                    strength_txt = self._ATTRIBUTE_VALUE_STRINGS[2]
                if strength > 5:
                    strength_txt = self._ATTRIBUTE_VALUE_STRINGS[1]
                if strength > 8:
                    strength_txt = self._ATTRIBUTE_VALUE_STRINGS[0]
                if strength < 0:
                    strength_txt = self._ATTRIBUTE_VALUE_STRINGS[6]
                if strength < -1:
                    strength_txt = self._ATTRIBUTE_VALUE_STRINGS[7]
                if strength < -3:
                    strength_txt = self._ATTRIBUTE_VALUE_STRINGS[8]
                if strength < -5:
                    strength_txt = self._ATTRIBUTE_VALUE_STRINGS[9]
                if strength < -8:
                    strength_txt = self._ATTRIBUTE_VALUE_STRINGS[10]
                return strength_txt

            strength_txt = txt2num(self.actor.strength)
            dex_txt = txt2num(self.actor.dexterity)
            s += f"\nYou are {size_txt}"
            s += f"\nYou are {strength_txt} in physical toughness."
            s += f"\nYou are {dex_txt} in physical dexterity."
        return s

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        vocab = [
            "you",
            "are",
            "in",
            "physical",
            "toughness",
            "dexterity",
            "still",
            "looks",
        ]
        vocab += split_in_list(cls._SIZE_TEXTS)
        vocab += split_in_list(cls._ATTRIBUTE_VALUE_STRINGS)
        return [
            "you",
            "currently",
            "have",
            "no",
            "quests",
            "talk",
            "to",
            "people",
            "get",
            "some",
            "help",
            "quest",
            "current",
        ]


class LookEvent(NoArgumentEvent):
    """Look events show the contents of the room as well as the description"""

    NAMES = ["look", "l"]
    TEMPLATES = ["look"]

    def _construct_world_view(self, world) -> str:
        """Create the actual viewed string once all fields have been found"""
        base_string = f"You are in {self.room_name}.\n"
        if self.room_desc is not None:
            base_string += self.room_desc + "\n"
        if len(self.object_ids) > 0:
            ents = {
                self.object_names[i]: self.object_ids[i]
                for i in range(len(self.object_ids))
            }
            base_string += world.view.get_room_object_text(self.object_names, ents)
        if len(self.agent_names) > 0:
            base_string += world.view.get_room_agent_text(self.agent_names)
        if len(self.neighbor_descs) > 0:
            base_string += world.view.get_room_edge_text(self.neighbor_descs)
        return base_string

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, get all the contents of the current room and make a view
        """
        assert not self.executed
        is_return = self.room.node_id in self.actor._visited_rooms
        if is_return or not self.room.has_prop("first_desc"):
            self.room_desc: str = self.room.desc
        else:
            self.room_desc = self.room.get_prop("first_desc")

        self.actor._visited_rooms.add(self.room.node_id)

        present_contents = self.room.get_contents()
        present_agents = [x for x in present_contents if x.agent and x != self.actor]
        present_objects = [x for x in present_contents if x.object]
        neighbor_nodes = self.room.get_neighbors()

        self.agent_ids: List[str] = [x.node_id for x in present_agents]
        self.object_ids: List[str] = [x.node_id for x in present_objects]

        self.agent_names: List[str] = [x.get_prefix_view() for x in present_agents]
        self.object_names: List[str] = [x.get_prefix_view() for x in present_objects]
        self.neighbor_descs: List[str] = [
            x.get_view_from(self.room) for x in neighbor_nodes
        ]
        self.room_name: str = self.room.get_prefix_view()

        self.__actor_name = self.actor.get_prefix_view()
        self.__current_view = self._construct_world_view(world)
        world.broadcast_to_agents(self, [self.actor])
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__current_view
        else:
            return f"{self.__actor_name} looked around."

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return ["you", "are", "in", "looked", "around"]


class PointEvent(GraphEvent):
    """Handles agents pointing at graph nodes"""

    NAMES = ["point"]
    TEMPLATES = ["point <room|object|agent>"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, move the item from the actor to the room
        """
        assert not self.executed
        # Populate for views
        self.__actor_name = self.actor.get_prefix_view()
        self.__target_name = self.target_nodes[0].get_prefix_view()

        self.__target_container_node = None
        self.__target_container_desc = None
        if self.target_nodes[0].object:
            contained_by = self.target_nodes[0].get_container()
            if contained_by.agent:
                self.__target_container_node = contained_by
                self.__target_container_desc = contained_by.get_prefix_view()
                self.__target_container_type = "carried"
                if self.target_nodes[0].equipped and self.target_nodes[0].wearable:
                    self.__target_container_type = "worn"
                if self.target_nodes[0].equipped and self.target_nodes[0].wieldable:
                    self.__target_container_type = "wielded"

        # Move the object over and broadcast
        world.broadcast_to_room(self)
        self.executed = True
        return []

    @proper_caps_wrapper
    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        convert = {"carried": "carrying", "worn": "wearing", "wielded": "wielding"}
        if viewer == self.actor:
            if self.__target_container_node == None:
                return f"You pointed at {self.__target_name}."
            else:
                if self.__target_container_node == viewer:
                    return f"You pointed at {self.__target_name} you are {convert[self.__target_container_type]}."
                else:
                    return f"You pointed at {self.__target_name} {self.__target_container_type} by {self.__target_container_desc}."
        elif self.target_nodes[0] == viewer:
            return f"{self.__actor_name} pointed at you."
        else:
            if self.__target_container_node == None:
                return f"{self.__actor_name} pointed at {self.__target_name}."
            else:
                if self.__target_container_node == viewer:
                    convert = {
                        "carried": "carrying",
                        "worn": "wearing",
                        "wielded": "wielding",
                    }
                    return f"{self.__actor_name} pointed at {self.__target_name} you are {convert[self.__target_container_type]}."
                elif self.__target_container_node == self.actor:
                    return f"{self.__actor_name} pointed at {self.__target_name} they are {convert[self.__target_container_type]}."
                else:
                    return f"{self.__actor_name} pointed at {self.__target_name} {self.__target_container_type} by {self.__target_container_desc}."

    def to_canonical_form(self) -> str:
        """return action text for dropping the object"""
        return f"point {self._canonical_targets[0]}"

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """
        Try to find applicable nodes by the given names - here we're searching
        for an object within the actor.
        """
        assert len(text_args) == 1, f"PointEvent takes one arg, got {text_args}"
        object_name = text_args[0]

        all_nodes = graph.desc_to_nodes(object_name, actor, "all+here")
        rooms_too = graph.desc_to_nodes(object_name, actor, "path")
        others_too = graph.desc_to_nodes(object_name, actor, "other_agents")
        applicable_nodes = all_nodes + rooms_too + others_too
        if len(applicable_nodes) > 0:
            return ProcessedArguments(targets=[applicable_nodes[0]])
        return ErrorEvent(
            cls, actor, f"You don't see '{object_name}' here to point at."
        )

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> "PointEvent":
        """Point events are always valid if constructed"""
        return cls(actor, target_nodes=targets, event_id=event_id)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """
        Find all objects that are currently pointable in the given room for the given agent.
        """
        room = actor.get_room()
        pointable_here = actor.get_contents() + room.get_contents() + [room]

        pointable_others_objects = list()
        for n1 in room.get_contents():
            if n1.agent:
                pointable_others_objects += n1.get_contents()

        pointable_paths = room.get_neighbors()
        pointable_all = pointable_here + pointable_paths + pointable_others_objects

        valid_actions: List[GraphEvent] = []
        # point all of the things here
        if len(pointable_all) == 0:
            return []

        # Try to point everything
        for obj in pointable_all:
            valid_actions.append(cls(actor, target_nodes=[obj]))

        return valid_actions

    @classmethod
    def get_vocab(cls) -> List[str]:
        """
        Return the vocabulary this event uses
        """
        return [
            "carried",
            "worn",
            "wielded",
            "you",
            "pointed",
            "at",
            "by",
            "they",
            "are",
        ]
