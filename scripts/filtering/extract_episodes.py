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
    LeaveEvent,
    SayEvent,
    TellEvent,
    WhisperEvent,
)

SPEECH_EVENTS = [SayEvent, TellEvent, WhisperEvent]
END_EVENTS = [DeathEvent, LeaveEvent]


# TODO: Treat this file as a "utils", maybe even include an episode class?
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
        world, hash_, event, time_ = event_buffer[i]

        if should_start_episode(event):
            curr_episode = Episode(event)
            utterance = Utterance()
            curr_episode.add_utterance(utterance)
        elif curr_episode is not None:
            if should_end_episode(event):
                episodes.append(curr_episode)
                curr_episode = None
            else:
                utterance = Utterance()
                curr_episode.add_utterance(utterance)

    return episodes


def should_start_episode(event):
    return type(event) in SPEECH_EVENTS


def should_end_episode(event):
    return type(event) in END_EVENTS


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
        # Conversation, a list of utterances
        self.convo = []
        pass

    def add_utterance(self, utterance):
        self.convo.append(utterance)


class Utterance:
    """
        An utterance is a class which is a single "turn"/timeperiod in a conversation
    """

    def __init__(self, actor_id, text, action, target_id):
        self.actor_id = actor_id
        self.text = text
        self.action = action
        self.target_id = target_id
        pass
