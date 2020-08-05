#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""
    This file is responsible for extracting the episodes from a meta episode log
    This involves:
        1. Finding the start/stop of conversations
        2. Capture relevant metadata
            - _setting_name
            - _setting_desc
            - agent names and personas
            - object names and descriptions
        3. Take events and parse out the convo
            - say can be SayEvent certainly, maybe TellEvent, WhisperEvent(?)
            - emotes are actions
            - all other are act events
        4. Return a list of the episodes
"""
from light.graph.events.graph_events import (
    DeathEvent,
    ErrorEvent,
    LeaveEvent,
    SayEvent,
    TellEvent,
    WhisperEvent,
)

SPEECH_EVENTS = [SayEvent, TellEvent, WhisperEvent]
END_EVENTS = [DeathEvent, LeaveEvent]


def extract_episodes(uuid_to_world, event_buffer):
    """
        Given the uuid to world json, and a buffer of events which occured in the logs,
        1. Delimit the training episodes
        2. Gather the metadata for training episodes
        3. Parse the episode from the data
        4. Return the episodes!
    """
    episodes = []
    curr_episode = None
    for i in range(len(event_buffer)):
        _, _, event, = event_buffer[i]

        if should_start_episode(curr_episode, event):
            curr_episode = initialize_episode(event)
            curr_episode.add_utterance(event)
        elif curr_episode is not None:
            if should_end_episode(event):
                episodes.append(curr_episode)
                curr_episode = None
            else:
                curr_episode.add_utterance(event)

    if curr_episode is not None:
        episodes.append(curr_episode)

    return episodes


def should_start_episode(curr_episode, event):
    """
        Returns true if the event signals the start of a new conversation
        1. There is not an episode currently in place
        2. The event starts a conversation (so is a speech event)
        3. More than one agent in the room
    """
    return (
        curr_episode is None
        and type(event) in SPEECH_EVENTS
        and len(event.present_agent_ids) > 1
    )


def should_end_episode(event):
    """
        Returns true if the event signals the end of a new conversation
        1. DeathEvent
        2. Leave Event (if agents continue talking, just make it a new convo
    """
    return type(event) in END_EVENTS


def initialize_episode(event):
    """
        Given an event which should_start_episode, initialize the episode class
        with the room name, description, and present agents and objects and their
        descriptions
    """
    contained = event.room.get_contents()
    agents = {
        x.name: {"persona": x.desc, "human": x.is_player} for x in contained if x.agent
    }
    objects = {x.name: x.desc for x in contained if x.object}
    curr_episode = Episode(event.room.name, event.room.desc, agents, objects,)
    return curr_episode


class Episode:
    """
        This class models the necessary information for a training episode.  Training
        episodes consist of:
            1. Metadata about the episode setting (room, name, description, etc)
            2. Utterances: Id of who is saying/acting, text/action, and target
            3. Present player id's (perhaps(?)) - may come in use for banning
    """

    def __init__(self, setting_name, setting_desc, agents, objects):
        self._setting_name = setting_name
        self._setting_desc = setting_desc

        # Dictionaries from IDs to descriptions
        self.agents = agents
        self.objects = objects

        self.utterances = []

    def add_utterance(self, event):
        """
            Converts the event to an utterance then appends it to the utterance
            buffer
        """
        # TODO: Decide if there are other skippable events which should not be
        # part of an episode
        if type(event) is ErrorEvent:
            return
        utter = Utterance.convert_to_utterance(event)
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

    def __init__(self, actor_id, text, action, target_ids):
        self.actor_id = actor_id
        self.text = text
        self.action = action
        self.target_ids = target_ids

    @staticmethod
    def convert_to_utterance(event):
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
        action = event.to_canonical_form() if type(event) not in SPEECH_EVENTS else None
        utterance = Utterance(event.actor.name, event.text_content, action, target_ids,)
        return utterance