#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.graph.events.base import (
    GraphEvent,
    ErrorEvent,
    TriggeredEvent,
    NoArgumentEvent,
    ProcessedArguments,
)

# Used for typehinting
from typing import Union, List, Optional, Tuple, Any, Type, TYPE_CHECKING
import emoji
import random
from light.graph.elements.graph_nodes import (
    GraphNode,
    GraphAgent,
    GraphObject,
    GraphRoom,
    LockEdge,
)

if TYPE_CHECKING:
    from light.world.world import World
    from light.graph.structured_graph import OOGraph


# TODO remove ability to take actions with yourself


class SystemMessageEvent(TriggeredEvent):
    """Event to send text messages to specified agents outside of other events"""

    def execute(self, world: "World") -> List[GraphEvent]:
        """Message to the target agent"""
        world.broadcast_to_agents(self, agents=[self.actor])
        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Only the target actor should be able to see this message"""
        if viewer == self.actor:
            return self.text_content
        else:
            return None


class SayEvent(GraphEvent):
    """Handles saying something out loud to the room."""

    NAMES = ["say"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """On execution, store the expected views, then broadcast"""
        assert not self.executed
        actor_name = self.actor.get_prefix_view()
        self.__in_room_view = f'{actor_name} said "{self.text_content}"'.capitalize()
        world.broadcast_to_room(self, exclude_agents=[self.actor])
        self.executed = True
        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return None  # One should not observe themself saying things
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
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
    ) -> Union["SayEvent", "ErrorEvent"]:
        """Say events are valid as long as there is text, otherwise fail."""
        if text is None or len(text.strip()) == 0:
            return ErrorEvent(cls, actor, "Say what? You have to say something!")
        text = text.strip()
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        return cls(actor, text_content=text)


class ShoutEvent(GraphEvent):
    """Handles saying something out loud to all agents."""

    NAMES = ["shout"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """On execution, store the view for the event"""
        assert not self.executed
        actor_name = self.actor.get_prefix_view()
        self.__in_room_view = f'{actor_name} said "{self.text_content}"'.capitalize()
        world.broadcast_to_all_agents(self, exclude_agents=[self.actor])
        self.executed = True
        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return None  # One should not observe themself saying things
        else:
            return self.__in_room_view

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
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
    ) -> Union["ShoutEvent", "ErrorEvent"]:
        """Shout events are valid as long as there is text, otherwise fail."""
        if text is None or len(text) == 0:
            return ErrorEvent(cls, actor, "Shout what? You have to shout something!")
        text = text.strip()
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        return cls(actor, text_content=text)


class WhisperEvent(GraphEvent):
    """Handles saying something to a specific agent without others hearing."""

    NAMES = ["whisper"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """On execution, store the views for the event, then broadcast"""
        assert not self.executed
        actor_name = self.actor.get_prefix_view()
        target_name = self.target_nodes[0].get_prefix_view()
        self.__target_view = (
            f'{actor_name} whispered "{self.text_content}" to you'.capitalize()
        )
        self.__in_room_view = (
            f"{actor_name} whispered something to {target_name}".capitalize()
        )

        # broadcast
        world.broadcast_to_room(self, exclude_agents=[self.actor])
        self.executed = True
        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return None  # One should not observe themself saying things
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
        """Format is whisper <target> "words being whispered". """
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
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
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

        return cls(actor, target_nodes=[targets[0]], text_content=text)


class TellEvent(GraphEvent):
    """Handles saying something to a specific agent aloud."""

    NAMES = ["tell"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """On execution, store the view for the actors involved"""
        assert not self.executed
        actor_name = self.actor.get_prefix_view()
        target_name = self.target_nodes[0].get_prefix_view()
        self.__target_view = f'{actor_name} told you "{self.text_content}"'.capitalize()
        self.__in_room_view = (
            f'{actor_name} told {target_name} "{self.text_content}"'.capitalize()
        )

        world.broadcast_to_room(self, exclude_agents=[self.actor])
        self.executed = True
        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return None  # One should not observe themself saying things
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
        """Format is tell <target> "words being told". """
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
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
    ) -> Union["TellEvent", ErrorEvent]:
        """Tell events are valid as long as there is text, otherwise fail."""
        assert len(targets) == 1, "Can only construct Tell event to exactly one target"
        target = targets[0]
        if text is None or len(text) == 0:
            return ErrorEvent(cls, actor, "Tell what? You have to tell something!")
        text = text.strip()
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]

        return cls(actor, target_nodes=[target], text_content=text)


class LeaveEvent(TriggeredEvent):
    """Event to note that someone has left a room"""

    def execute(self, world: "World") -> List[GraphEvent]:
        """Save expected views, then message everyone"""
        actor_name = self.actor.get_prefix_view()
        target_name = self.target_nodes[0].get_prefix_view_from(self.room)
        self.__in_room_view = f'{actor_name} left towards "{target_name}"'
        world.broadcast_to_room(self, exclude_agents=[self.actor])
        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return None  # One should not observe themself leaving
        else:
            return self.__in_room_view


class ArriveEvent(TriggeredEvent):
    """
    Event to note that someone has arrived in a room.

    It takes as text_content the name of the place the person arrived from.
    """

    def execute(self, world: "World") -> List[GraphEvent]:
        """Save expected views, then message everyone"""
        actor_name = self.actor.get_prefix_view()
        self.__in_room_view = (
            f"{actor_name} arrived from {self.text_content}".capitalize()
        )
        world.broadcast_to_room(self, exclude_agents=[self.actor])
        return []

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

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            if self.__successful_follow:
                return "You follow. "
            else:
                return "You try to follow, but cannot as there is no more room there! "
        else:
            return None  # One should not observe others follows


class GoEvent(GraphEvent):
    """Handles moving as an individual from one room to another"""

    NAMES = ["go"]

    def __init__(
        self,
        actor: GraphAgent,
        target_nodes: Optional[List[GraphNode]] = None,
        text_content: Optional[str] = None,
    ):
        super().__init__(actor, target_nodes, text_content)
        # Must store room views because getting views from other rooms is odd
        new_room = self.target_nodes[0]
        old_room = self.actor.get_room()
        old_room_view = self.room.get_prefix_view_from(new_room)
        self.__canonical_room_view = new_room.get_view_from(old_room).replace("a path to the", "")

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, trigger leaving, move the agent, and trigger arriving
        Return GoFollow events and Look events as needed
        """
        assert not self.executed
        # Populate for views
        old_room = self.actor.get_room()
        new_room = self.target_nodes[0]
        old_room_view = old_room.get_prefix_view_from(new_room)

        self.__canonical_room_view = new_room.get_view_from(old_room)

        # Trigger the leave event, must be before the move to get correct room
        LeaveEvent(self.actor, [self.target_nodes[0]]).execute(world)
        self.actor.move_to(new_room)
        ArriveEvent(self.actor, text_content=old_room_view).execute(world)
        LookEvent(self.actor).execute(world)

        # trigger the follows
        followers = self.actor.get_followers()
        for follower in followers:
            TriggerFollowEvent(follower, target_nodes=self.target_nodes).execute(world)

        self.executed = True
        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        return None  # Go events are viewed through Leave and Arrive events

    def to_canonical_form(self) -> str:
        """
        Provide the text that this event's actor would use to invoke this event
        """
        return f"go {self.__canonical_room_view}"

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
        """Format is go <place>. """
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
        if current_room.get_edge_to(target_room).path_is_locked():
            return ErrorEvent(cls, actor, f"The path there is locked!")
        if not target_room.would_fit(actor):
            return ErrorEvent(cls, actor, f"There's not enough room to fit in there!")

        return ProcessedArguments(targets=[target_room])

    @classmethod
    def construct_from_args(
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
    ) -> Union["GoEvent", ErrorEvent]:
        """Go events are valid if properly parsed and thus target is a room."""
        assert len(targets) == 1, f"GoEvents take one target, the room. Got {targets}"
        target = targets[0]
        assert target.room, "Can only go to rooms"
        return cls(actor, target_nodes=[target])

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """Can create a go event to any unlocked path that fits"""
        valid_actions: List[GraphEvent] = []
        room = actor.get_room()
        for neighbor in room.get_neighbors():
            if not room.get_edge_to(neighbor).path_is_locked():
                if neighbor.would_fit(actor):
                    valid_actions.append(cls(actor, target_nodes=[neighbor]))
        return valid_actions


class UnfollowEvent(NoArgumentEvent):
    """Handles removing a follow"""

    NAMES = ["unfollow"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, prepare  views and clear the follow
        """
        assert not self.executed
        actor_name = self.actor.get_prefix_view()
        follow_name = self.actor.get_following().get_prefix_view()
        self.__unfollow_view = f"You stopped following {follow_name}"
        self.__unfollowed_view = f"{actor_name} stopped following you".capitalize()

        self.__follow_target = self.actor.get_following()
        self.actor.unfollow()
        world.broadcast_to_agents(self, [self.actor, self.__follow_target])
        self.executed = True
        return []

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
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
    ) -> Union["UnfollowEvent", ErrorEvent]:
        """Unfollow events are valid as long as you are following something."""
        assert (
            len(targets) == 0
        ), f"UnfollowEvents should get no args, but got {targets}"
        if actor.get_following() is None:
            return ErrorEvent(cls, actor, "You already aren't following anyone")
        return cls(actor)

    @classmethod
    def get_valid_actions(cls, graph: "OOGraph", actor: GraphAgent) -> List[GraphEvent]:
        """Can construct a valid unfollow if currently following"""
        if actor.get_following() is not None:
            return [cls(actor)]
        else:
            return []


class FollowEvent(GraphEvent):
    """Handles having an agent follow another agent"""

    NAMES = ["follow"]

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
        self.__follow_view = f"You started following {follow_name}"
        self.__followed_view = f"{actor_name} started following you".capitalize()

        self.actor.follow(follow_target)
        world.broadcast_to_agents(self, [self.actor, self.target_nodes[0]])
        self.executed = True
        return []

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
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
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
        return cls(actor, target_nodes=[target])

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


# TODO examine more death processing. Do we need to update a player status?
# must check structured_graph and graph_nodes
class DeathEvent(TriggeredEvent):
    """Handles processing graph cleanup when an agent dies, and sending message"""

    def execute(self, world: "World") -> List[GraphEvent]:
        """Save expected views, then message everyone"""
        actor_name = self.actor.get_prefix_view()
        self.__in_room_view = f"{actor_name} died! "

        # You have to send to the room before death or the dying agent won't get the message
        world.broadcast_to_room(self)

        # Trigger the actual death
        world.oo_graph.agent_die(self.actor)
        # TODO any other world processing of a death event, perhaps to
        # update the player
        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return f"You died! "
        else:
            return self.__in_room_view


class SoulSpawnEvent(TriggeredEvent):
    """Handles processing the view for when a player is spawned, and passing their context"""

    def __init__(
        self,
        soul_id,
        actor: GraphAgent,
        target_nodes: Optional[List[GraphNode]] = None,
        text_content: Optional[str] = None,
    ):
        super().__init__(actor, target_nodes, text_content)
        # Must store this for important metadata
        self.soul_id = soul_id

    def execute(self, world: "World") -> List[GraphEvent]:
        # Add player id as an attribute
        """Construct intro text and broadcast to the player"""
        actor_name = self.actor.get_prefix_view()

        sun_txt = emoji.emojize(":star2:", use_aliases=True) * 31
        msg_txt = sun_txt + "\n"
        msg_txt += f"Your soul possesses {self.actor.get_view()}.\n"
        msg_txt += "Your character:\n"
        msg_txt += self.actor.persona + "\n"
        msg_txt += sun_txt + "\n"
        self.__msg_txt = msg_txt
        world.broadcast_to_agents(self, [self.actor])

        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__msg_txt
        else:
            return None


class SpawnEvent(TriggeredEvent):
    """Handles processing the view for when a player is spawned, and passing their context"""

    def execute(self, world: "World") -> List[GraphEvent]:
        """Construct intro text and broadcast to the player"""
        actor_name = self.actor.get_prefix_view()

        sun_txt = emoji.emojize(":star2:", use_aliases=True) * 31
        msg_txt = sun_txt + "\n"
        msg_txt += f"You are spawned into this world as {self.actor.get_view()}.\n"
        msg_txt += "Your character:\n"
        msg_txt += self.actor.persona + "\n"
        msg_txt += sun_txt + "\n"
        self.__msg_txt = msg_txt

        world.broadcast_to_agents(self, [self.actor])

        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__msg_txt
        else:
            return None


class HelpEvent(NoArgumentEvent):
    """Handles user asking for help"""

    NAMES = ["help", "h"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """Construct intro text and broadcast to the player"""
        actor_name = self.actor.get_prefix_view()
        self.__msg_txt = world.view.help_text()
        world.broadcast_to_agents(self, [self.actor])
        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__msg_txt
        else:
            return None


class HitEvent(GraphEvent):
    """Handles having one agent attack another"""

    NAMES = ["hit"]

    def __init__(
        self,
        actor: GraphAgent,
        target_nodes: Optional[List[GraphNode]] = None,
        text_content: Optional[str] = None,
    ):
        super().__init__(actor, target_nodes, text_content)
        # Must store these for replaying exact sequences
        self.attack = None
        self.defense = None

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, have one agent hit another, calculating
        the outcome depending on battle stats.

        If an agent died, trigger a death event.
        """
        assert not self.executed
        # Populate for views
        self.__actor_name = self.actor.get_prefix_view()
        attack_target = self.target_nodes[0]
        assert isinstance(attack_target, GraphAgent), "Must attack an agent"
        self.__attack_name = attack_target.get_prefix_view()
        damage = self.actor.get_prop("damage", 0)
        armor = attack_target.get_prop("defense", 0)
        if self.attack is None:
            # need to save randomized attacks for replaying
            self.attack = random.randint(max(0, damage - 10), damage + 1)
            self.defend = random.randint(max(0, armor - 10), armor)

        world.broadcast_to_room(self)

        if self.attack - self.defend > 1:
            # Calculate damage
            health = attack_target.health
            health = max(0, health - (self.attack - self.defend))
            attack_target.health = health
            if health == 0:
                DeathEvent(attack_target).execute(world)
            else:
                HealthEvent(attack_target).execute(world)

        self.executed = True
        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""

        if self.attack == 0:
            # The attack missed
            if viewer == self.actor:
                return f"You attacked {self.__attack_name}, but missed! "
            elif viewer == self.target_nodes[0]:
                return f"{self.__actor_name} attacked you, but missed. ".capitalize()
            else:
                return f"{self.__actor_name} attacked {self.__attack_name}, but missed. ".capitalize()
        elif self.attack - self.defend < 1:
            # The attack was blocked
            if viewer == self.actor:
                return f"You attacked {self.__attack_name}, but they blocked! "
            elif viewer == self.target_nodes[0]:
                return (
                    f"{self.__actor_name} attacked you, but you blocked. ".capitalize()
                )
            else:
                return f"{self.__actor_name} attacked {self.__attack_name}, but the attack was blocked. ".capitalize()
        else:
            # The attack happened
            if viewer == self.actor:
                return f"You attacked {self.__attack_name}! "
            elif viewer == self.target_nodes[0]:
                return f"{self.__actor_name} attacked you! ".capitalize()
            else:
                return (
                    f"{self.__actor_name} attacked {self.__attack_name}! ".capitalize()
                )

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
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
    ) -> Union["HitEvent", "ErrorEvent"]:
        """Hit events with a target agent will always be valid."""
        assert len(targets) == 1, f"HitEvent takes one arg, got {targets}"
        target = targets[0]
        assert target.agent, "Can only hit agents"
        return cls(actor, target_nodes=[target])

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


class HugEvent(GraphEvent):
    """Handles having one agent give another a hug"""

    NAMES = ["hug"]

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

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return f"You hugged {self.__hugged_name}, but missed!"
        elif viewer == self.target_nodes[0]:
            return f"{self.__actor_name} hugged you.".capitalize()
        else:
            return f"{self.__actor_name} hugged {self.__hugged_name}.".capitalize()

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
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
    ) -> Union["HugEvent", "ErrorEvent"]:
        """Hug events with a target will always be valid."""
        assert len(targets) == 1, f"HitEvent takes one arg, got {targets}"
        target = targets[0]
        assert target.agent, "Can only hit agents"
        return cls(actor, target_nodes=[target])

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


# TODO handle locked objects
class GetObjectEvent(GraphEvent):
    """Handles getting an object from a container or a location"""

    NAMES = ["get", "take"]

    def __init__(
        self,
        actor: GraphAgent,
        target_nodes: Optional[List[GraphNode]] = None,
        text_content: Optional[str] = None,
    ):
        super().__init__(actor, target_nodes, text_content)
        self.__from_room = self.room == self.target_nodes[1]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, move the item from its location to the age
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

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""

        if viewer == self.actor:
            viewer_text = "You"
        else:
            viewer_text = self.__actor_name.capitalize()
        if self.__from_room:
            return f"{viewer_text} got {self.__gotten_name}"
        else:
            return (
                f"{viewer_text} got {self.__gotten_name} from {self.__container_name}"
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
                    guess_target_name = guess_target.get_prefix_view().capitalize()
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
                    guess_target_name = guess_target.get_prefix_view().capitalize()
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
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
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
        return cls(actor, target_nodes=[target, container])

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


# TODO handle locked objects
class PutObjectInEvent(GraphEvent):
    """Handles putting an object in or on another object"""

    NAMES = ["put"]

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

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""

        if viewer == self.actor:
            viewer_text = "You"
        else:
            viewer_text = self.__actor_name.capitalize()
        surface_type = self.target_nodes[1].get_prop("surface_type", "in")
        return f"{viewer_text} put {self.__put_name} {surface_type} {self.__container_name}"

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
                guess_target_name = guess_target.get_prefix_view().capitalize()
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
            guess_target_name = guess_target.get_prefix_view().capitalize()
            return ErrorEvent(
                cls,
                actor,
                f"You could put {guess_target_name}, but you'll have to remove it first.",
                [guess_target],
            )
        elif len(target_nodes) > 0:
            # we found a node, but it isn't the right one.
            guess_target = target_nodes[0]
            guess_target_name = guess_target.get_prefix_view().capitalize()
            return ErrorEvent(
                cls,
                actor,
                f"{guess_target_name}, isn't something you can put.",
                [guess_target],
            )
        return ErrorEvent(cls, actor, f"You don't have '{object_name}' here to put.")

    @classmethod
    def construct_from_args(
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
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
        return cls(actor, target_nodes=[target, container])

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


class DropObjectEvent(GraphEvent):
    """Handles dropping an object onto the floor"""

    NAMES = ["drop"]

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

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""

        if viewer == self.actor:
            viewer_text = "You"
        else:
            viewer_text = self.__actor_name.capitalize()
        return f"{viewer_text} got {self.__drop_name} "

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
            guess_target_name = guess_target.get_prefix_view().capitalize()
            return ErrorEvent(
                cls,
                actor,
                f"You could drop {guess_target_name}, but you'll have to remove it first.",
                [guess_target],
            )
        elif len(target_nodes) > 0:
            # we found a node, but it isn't the right one.
            guess_target = target_nodes[0]
            guess_target_name = guess_target.get_prefix_view().capitalize()
            return ErrorEvent(
                cls,
                actor,
                f"{guess_target_name}, isn't something you can drop.",
                [guess_target],
            )
        return ErrorEvent(cls, actor, f"You don't have '{object_name}' to drop.")

    @classmethod
    def construct_from_args(
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
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
        return cls(actor, target_nodes=[target])

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


class StealObjectEvent(GraphEvent):
    """Handles stealing an object from an actor"""

    NAMES = ["steal"]

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

        # Move the object over and broadcast
        gotten_target.move_to(self.actor)
        world.broadcast_to_room(self)
        self.executed = True
        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""

        if viewer == self.actor:
            actor_text = "You"
        else:
            actor_text = self.__actor_name.capitalize()
        victim_text = self.__victim_name
        if viewer == self.target_nodes[1]:
            victim_text = "you"
        return f"{actor_text} stole {self.__gotten_name} from {victim_text}"

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
                guess_target_name = guess_target.get_prefix_view().capitalize()
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
                    guess_target_name = guess_target.get_prefix_view().capitalize()
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
                    guess_target_name = guess_target.get_prefix_view().capitalize()
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
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
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
        return cls(actor, target_nodes=[target, victim])

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


class GiveObjectEvent(GraphEvent):
    """Handles giving an object to another agent"""

    NAMES = ["give"]

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

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""

        if viewer == self.actor:
            actor_text = "You"
        else:
            actor_text = self.__actor_name.capitalize()
        recipient_text = self.__recipient_name
        if viewer == self.target_nodes[1]:
            recipient_text = "you"
        return f"{actor_text} gave {self.__given_name} to {recipient_text}"

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
            guess_target_name = guess_target.get_prefix_view().capitalize()
            return ErrorEvent(
                cls,
                actor,
                f"You could give {guess_target_name}, but you'll have to remove it first.",
                [guess_target],
            )
        elif len(target_nodes) > 0:
            # we found a node, but it isn't the right one.
            guess_target = target_nodes[0]
            guess_target_name = guess_target.get_prefix_view().capitalize()
            return ErrorEvent(
                cls,
                actor,
                f"{guess_target_name}, isn't something you can give.",
                [guess_target],
            )
        return ErrorEvent(cls, actor, f"You don't have '{object_name}' to give.")

    @classmethod
    def construct_from_args(
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
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
        return cls(actor, target_nodes=[target, recipient])

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


class EquipObjectEvent(GraphEvent):
    """Handles equipping a held object"""

    NAMES = ["equip"]

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
        equip_target.equipped = True
        for n, s in equip_target.get_prop("stats", {"defense": 1}).items():
            self.actor.set_prop(n, self.actor.get_prop(n) + s)
        world.broadcast_to_room(self)
        self.executed = True
        return []

    @classmethod
    def can_equip(cls, object_node: GraphObject) -> bool:
        return object_node.wearable or object_node.wieldable

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            actor_text = "You"
        else:
            actor_text = self._actor_name.capitalize()
        return f"{actor_text} {self.action_name} {self._equip_name} "

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
            guess_target_name = guess_target.get_prefix_view().capitalize()
            return ErrorEvent(
                cls,
                actor,
                f"{guess_target_name}, isn't something you can {cls.NAMES[0]}.",
                [guess_target],
            )
        return ErrorEvent(
            cls, actor, f"You don't have '{object_name}' to {cls.NAMES[0]}."
        )

    @classmethod
    def construct_from_args(
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
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
        if target.equipped is not None:
            return ErrorEvent(
                cls,
                actor,
                f"You already have {target.get_prefix_view()} equipped!",
                [target],
            )
        return cls(actor, target_nodes=[target])

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

    action_name = "wore"
    past_tense_action_name = "worn"

    @classmethod
    def can_equip(cls, object_node: GraphObject) -> bool:
        return object_node.wearable


class WieldEvent(EquipObjectEvent):
    """Handles wielding a held object"""

    NAMES = ["wield"]

    action_name = "wielded"
    past_tense_action_name = "wielded"

    @classmethod
    def can_equip(cls, object_node: GraphObject) -> bool:
        return object_node.wieldable


class RemoveObjectEvent(GraphEvent):
    """Handles removing an equipped object"""

    NAMES = ["remove", "unwield"]

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
        for n, s in equip_target.get_prop("stats", {"defense": 1}).items():
            self.actor.set_prop(n, self.actor.get_prop(n) - s)
        world.broadcast_to_room(self)
        self.executed = True
        return []

    @classmethod
    def can_equip(cls, object_node: GraphObject) -> bool:
        return object_node.wearable or object_node.wieldable

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            actor_text = "You"
        else:
            actor_text = self._actor_name.capitalize()
        return f"{actor_text} removed {self._equip_name} "

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
            guess_target_name = guess_target.get_prefix_view().capitalize()
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
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
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
            guess_target_name = target.get_prefix_view().capitalize()
            return ErrorEvent(
                cls,
                actor,
                f"{guess_target_name}, isn't something you have equipped.",
                [target],
            )
        return cls(actor, target_nodes=[target])

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


class IngestEvent(GraphEvent):
    """Handles equipping a held object"""

    NAMES = ["ingest"]

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
        world.oo_graph.mark_node_for_deletion(ingest_target.node_id)

        world.broadcast_to_room(self)

        health_text = world.health(self.actor.node_id)
        self.actor.health = max(self.actor.health + fe, 0)
        new_health_text = world.health(self.actor.node_id)
        if self.actor.health <= 0:
            DeathEvent(self.actor).execute(world)
        elif health_text != new_health_text:
            HealthEvent(self.actor).execute(world)

        self.executed = True
        return []

    @classmethod
    def can_ingest(cls, object_node: GraphObject) -> bool:
        return object_node.drink or object_node.food

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return f"You {self.past_tense_action_name} {self._ingest_name}. {self._outcome} "
        else:
            return f"{self._actor_name.capitalize()} {self.past_tense_action_name} {self._ingest_name}. "

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
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
    ) -> Union["IngestEvent", "ErrorEvent"]:
        """Equip object events are valid as long as an equippable object was found"""
        assert len(targets) == 1, f"IngestEvent takes one arg, got {targets}"
        target = targets[0]
        assert (
            target in actor.get_contents()
        ), "Target node is not in the given container"
        assert isinstance(target, GraphObject), f"Must ingest an object, not {target}"
        if not cls.can_ingest(target):
            guess_target_name = target.get_prefix_view().capitalize()
            return ErrorEvent(
                cls,
                actor,
                f"{guess_target_name}, isn't something you can {cls.NAMES[0]}.",
                [target],
            )
        return cls(actor, target_nodes=[target])

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

    past_tense_action_name = "ate"

    @classmethod
    def can_ingest(cls, object_node: GraphObject) -> bool:
        return object_node.food


class DrinkEvent(IngestEvent):
    """Handles eating a held object"""

    NAMES = ["drink"]

    past_tense_action_name = "drank"

    @classmethod
    def can_ingest(cls, object_node: GraphObject) -> bool:
        return object_node.drink


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
            lock_edge = neighbor_to_lock.locked_edge
        elif lock_target.object and lock_target.container:
            lock_edge = lock_target.locked_edge
        else:
            raise AssertionError("Cannot lock a non-lockable thing")

        self.process_locking(lock_edge)

        world.broadcast_to_room(self)
        self.executed = True
        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            viewer_text = "You"
        else:
            viewer_text = self._actor_name.capitalize()
        return (
            f"{viewer_text} {self.NAMES[0]}ed {self._locked_name} with {self._key_name}"
        )

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
            if edge.locked_edge is not None
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
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
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
        return cls(actor, target_nodes=[target_node, key_node])

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


# TODO handle locked objects
class ExamineEvent(GraphEvent):
    """Handles displaying examine/extra text for a graph node"""

    NAMES = ["examine", "ex"]

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
        self.__target_name = self.target_nodes[0].get_prefix_view()
        self.__examine_text = self._get_target_description(world)

        # Move the object over and broadcast
        world.broadcast_to_room(self)
        self.executed = True
        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__examine_text
        elif self.target_nodes[0] == viewer:
            return f"{self.__actor_name.capitalize()} examined you "
        else:
            return f"{self.__actor_name.capitalize()} examined {self.__target_name} "

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
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
    ) -> "ExamineEvent":
        """Examine events are always valid if constructed"""
        return cls(actor, target_nodes=targets)

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

    def execute(self, world: "World") -> List[GraphEvent]:
        """On execution, store the expected views, then broadcast"""
        assert not self.executed
        assert self.text_content is not None, "Cannot emote without text_context"
        actor_name = self.actor.get_prefix_view()
        self.__display_action = self.DESC_MAP[self.text_content]
        self.__in_room_view = f"{actor_name} {self.__display_action}".capitalize()
        world.broadcast_to_room(self, exclude_agents=[self.actor])
        self.executed = True
        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return None  # One should not observe themself emoting
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
        cls, actor: GraphAgent, targets: List["GraphNode"], text: Optional[str] = None
    ) -> Union["EmoteEvent", "ErrorEvent"]:
        """Emote events are valid if the emote is valid."""
        if text is None or text not in cls.DESC_MAP:
            all_emotes = ", ".join(cls.DESC_MAP.keys()) + "."
            return ErrorEvent(
                cls,
                actor,
                f"What emotion is that? At the moment light denizens can only show the following gestures:\n{all_emotes}",
            )
        return cls(actor, text_content=text)

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


class WaitEvent(NoArgumentEvent):
    """Wait events just allow a player to do nothing in a timestep"""

    NAMES = ["wait"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, broadcast the nothing happening
        """
        assert not self.executed
        self.__actor_name = self.actor.get_prefix_view()
        world.broadcast_to_room(self)
        self.executed = True
        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return "You waited. "
        else:
            return f"{self.__actor_name.capitalize()} waited. "


class InventoryEvent(NoArgumentEvent):
    """Inventory events just allow a player to do nothing in a timestep"""

    NAMES = ["inventory", "inv", "i"]

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

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return (
                f"You check yourself. You are {self.__actor_name}!\n"
                f"You are {self.__inv_text}"
            )
        else:
            return f"{self.__actor_name.capitalize()} checked their inventory. "


class HealthEvent(NoArgumentEvent):
    """Inventory events just allow a player to do nothing in a timestep"""

    NAMES = ["health", "status"]

    def execute(self, world: "World") -> List[GraphEvent]:
        """
        On execution, get the actor name and their current health
        """
        assert not self.executed
        self.__actor_name = self.actor.get_prefix_view()
        self.__health_text = world.health(self.actor.node_id)
        world.broadcast_to_agents(self, [self.actor])
        self.executed = True
        return []

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return f"You are feeling {self.__health_text}. "
        else:
            return f"{self.__actor_name.capitalize()} checked their health. "


class LookEvent(NoArgumentEvent):
    """Look events show the contents of the room as well as the description"""

    NAMES = ["look", "l"]

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

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given viewer should view this event"""
        if viewer == self.actor:
            return self.__current_view
        else:
            return f"{self.__actor_name.capitalize()} looked around. "


# TODO implement use


ALL_EVENTS_LIST: List[Type[GraphEvent]] = [
    SayEvent,
    ShoutEvent,
    WhisperEvent,
    TellEvent,
    GoEvent,
    UnfollowEvent,
    FollowEvent,
    HelpEvent,
    HitEvent,
    HugEvent,
    GetObjectEvent,
    PutObjectInEvent,
    DropObjectEvent,
    StealObjectEvent,
    GiveObjectEvent,
    EquipObjectEvent,
    WearEvent,
    WieldEvent,
    RemoveObjectEvent,
    IngestEvent,
    EatEvent,
    DrinkEvent,
    SoulSpawnEvent,
    # LockEvent,
    # UnlockEvent,
    ExamineEvent,
    EmoteEvent,
    WaitEvent,
    InventoryEvent,
    HealthEvent,
    LookEvent,
]

ALL_EVENTS = {name: e for e in ALL_EVENTS_LIST for name in e.NAMES}
