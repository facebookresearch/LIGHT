#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""
    This file is responsible for extracting the episodes from a event log
    This involves:
        1. Finding the start/stop of conversations (off loading to task maybe?)
        2. Capture relevant metadata
            - setting names and descriptions
            - agent names and personas
            - object names and descriptions
        3. Take events and parse out the convo
            - say can be SayEvent certainly, maybe TellEvent, WhisperEvent(?)
            - emotes are actions
            - all other are act events
        4. Return a list of the episodes
"""
from light.graph.events.graph_events import (
    ArriveEvent,
    DeathEvent,
    ErrorEvent,
    GoEvent,
    LeaveEvent,
    LookEvent,
    SayEvent,
    SoulSpawnEvent,
    SystemMessageEvent,
    TellEvent,
    TriggerFollowEvent,
    WhisperEvent,
)
from light.graph.events.base import TriggeredEvent
from json import JSONEncoder

START_EVENTS = [ArriveEvent, SoulSpawnEvent]
SPEECH_EVENTS = [SayEvent, TellEvent, WhisperEvent]
END_EVENTS = [DeathEvent, LeaveEvent]
DEFAULT_PERSONA = "I am a player in the LIGHT world."


def extract_episodes(uuid_to_world, event_buffer, agent_pov=True):
    """
    Given the uuid to world json, and a buffer of events which occured in the logs,
    1. Delimit the training episodes
    2. Gather the metadata for training episodes
    3. Parse the episode from the data
    4. Return the episodes!
    """
    episodes = []
    curr_episode = None
    if agent_pov:
        for i in range(len(event_buffer)):
            (
                uuid,
                _,
                _,
                event,
            ) = event_buffer[i]
            world = uuid_to_world[uuid]
            if curr_episode is None:
                curr_episode = initialize_episode(event)

            if i == 0:
                add_event_trigger(curr_episode, world, event)
            else:
                _, _, _, prev_event = event_buffer[i - 1]
                prev_type = type(prev_event)
                add_event_trigger(curr_episode, world, event, prev_type)
        if curr_episode is not None:
            # Preprocess - no longer need the node here, just the actor name
            curr_episode.actor = curr_episode.actor.name
            episodes.append(curr_episode)
    else:
        # Triggered by soul spawn event or arrive event!
        for i in range(len(event_buffer)):
            (
                _,
                _,
                _,
                event,
            ) = event_buffer[i]
            # Get the human entered on this event, record episode until leave or die.
            if should_start_episode(event):
                # Should start with SoulSpawnEvent/ArriveEvent from agent POV
                curr_episode = initialize_episode(event)
                record_episode(uuid_to_world, curr_episode, event_buffer, i)
                curr_episode.actor = curr_episode.actor.name
                episodes.append(curr_episode)

    return episodes


def should_start_episode(event):
    """
    Returns true if the event signals the start of a new conversation
    1. There is not an episode currently in place
    2. The event starts a conversation (so is a speech event)
    3. More than one agent in the room
    """
    return type(event) in START_EVENTS and event.actor.is_player


def record_episode(uuid_to_world, curr_episode, event_buffer, i):
    """
    Records an episode from the POV of an agent in a room
    """
    while i < len(event_buffer):
        (
            uuid,
            _,
            _,
            event,
        ) = event_buffer[i]
        world = uuid_to_world[uuid]
        if i == 0:
            add_event_trigger(curr_episode, world, event)
        else:
            _, _, _, prev_event = event_buffer[i - 1]
            prev_type = type(prev_event)
            add_event_trigger(curr_episode, world, event, prev_type)
        if should_end_episode(curr_episode, event):
            return
        i += 1


def add_event_trigger(curr_episode, world, event, prev_type=None):
    """
    Determines if the event should be added with triggered or not, then
     adds it to the utterances for the episode
    """
    if type(event) == LookEvent:
        triggered = prev_type == ArriveEvent or prev_type == SoulSpawnEvent
        curr_episode.add_utterance(world, event, triggered=triggered)
    elif type(event) == GoEvent:
        triggered = prev_type == TriggerFollowEvent
        curr_episode.add_utterance(world, event, triggered=triggered)
    else:
        curr_episode.add_utterance(world, event)


def should_end_episode(episode, event):
    """
    Returns true if the event signals the end of a new conversation
    1. DeathEvent
    2. Leave Event (if agents continue talking, just make it a new convo
    """
    return type(event) in END_EVENTS and event.actor.node_id == episode.actor.node_id


def initialize_episode(event):
    """
    Given an event which should_start_episode, initialize the episode class
    with the room name, description, and present agents and objects and their
    descriptions
    """
    settings = {event.room.name: event.room.desc}
    contained = event.room.get_contents()
    agents = {}
    for x in contained:
        if x.agent:
            # Required for old format (conversion script)
            if x.persona != DEFAULT_PERSONA:
                agents[x.name] = x.persona
            else:
                agents[x.name] = x.desc
    objects = {x.name: x.desc for x in contained if x.object}
    curr_episode = Episode(settings, agents, objects, event.actor)
    return curr_episode


class Episode:
    """
    This class models the necessary information for a training episode.  Training
    episodes consist of:
        1. Metadata about the episode setting (room, name, description, etc)
        2. Utterances: Id of who is saying/acting, text/action, and target
        3. Present player id's (perhaps(?)) - may come in use for banning
    """

    def __init__(self, settings, agents, objects, actor):
        # Dictionary from setting name to description
        self.settings = settings
        # Dictionaries from IDs to descriptions
        self.agents = agents
        self.objects = objects
        # The agent whose POV this episode is from
        self.actor = actor

        self.utterances = []

    def add_utterance(self, world, event, triggered=False):
        """
        Converts the event to an utterance then appends it to the utterance
        buffer
        """
        # TODO: Decide if there are other skippable events which should not be
        # part of an episode
        if type(event) is ErrorEvent or type(event) is SystemMessageEvent:
            return
        elif type(event) is ArriveEvent:
            # Need to add a new setting - and any agents or objects
            self.settings[event.room.name] = event.room.desc
            contained = event.room.get_contents()
            agents = {}
            for x in contained:
                if x.agent:
                    # Required for old format (conversion script)
                    if x.persona != DEFAULT_PERSONA:
                        agents[x.name] = x.persona
                    else:
                        agents[x.name] = x.desc
            objects = {x.name: x.desc for x in contained if x.object}
            self.agents.update(agents)
            self.objects.update(objects)
        utter = Utterance.convert_to_utterance(event, self.actor, triggered)
        # Add possible actions before executing!
        if self.actor.node_id == event.actor.node_id and not utter.triggered:
            utter.possible_actions = world.get_possible_actions(event.actor.node_id)
        event.executed = False
        event.execute(world)
        self.utterances.append(utter)


class Utterance:
    """
    An utterance is a class which is a single "turn"/timestep in a conversation
    Utterances include:
    1. The name of the actor
    2. What was said (the text of the action)
    3. What action (if any) was performed
    4. The recipient of the action
    """

    def __init__(self, actor_id, text, action, target_ids, triggered):
        self.actor_id = actor_id
        self.text = text
        self.action = action
        self.target_ids = target_ids
        self.triggered = triggered

    @staticmethod
    def convert_to_utterance(event, main_agent, certain_triggered=False):
        """
        This method is responsible for converting an event to an utterance from the
        episode's POV.

        Special cases:

            - If there are no target nodes, then we pass None, and if there are
            multiple we record them all

            - If it is a speech event, do not record the action form.

        """
        target_ids = (
            [x.name for x in event.target_nodes]
            if len(event.target_nodes) > 0
            else None
        )
        triggered = certain_triggered
        if issubclass(type(event), TriggeredEvent):
            class_name = event.__class__.__name__
            # Chop off the "event" part of the name, make that action
            # else it is an error (bc no canonical form)
            action = class_name[: len(class_name) - 5].lower()
            triggered = True
        else:
            action = event.to_canonical_form()

        if type(event) in SPEECH_EVENTS:
            text = event.text_content
        elif main_agent.node_id == event.actor.node_id:
            # This hack is because the nodes will not always be equal
            # for some specific __eq__ semantics, so need to use
            # the actual reference otherwise you get 3rd person pov
            text = event.view_as(event.actor)
        else:
            text = event.view_as(main_agent)

        utterance = Utterance(event.actor.name, text, action, target_ids, triggered)
        if type(event) is LookEvent and main_agent.node_id == event.actor.node_id:
            # Record what is present for pov look events only
            contained = event.room.get_contents()
            utterance.setting = event.room.name
            utterance.present_agents = [x.name for x in contained if x.agent]
            utterance.present_objects = [x.name for x in contained if x.object]
        return utterance


class EpisodeEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return sorted(list(o))
        if isinstance(o, list):
            return sorted(o)
        else:
            return {k: v for k, v in o.__dict__.copy().items()}
