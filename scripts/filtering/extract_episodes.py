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


# TODO: Treat this file as a "utils", maybe even include an episode class?
def extract_episodes(uuid_to_world, event_buffer):
    """
        Given the uuid to world json, and a buffer of events which occured in the logs,
        1. Delimit the training episodes
        2. Gather the metadata for training episodes
        3. Parse the episode from the data
        4. Return the episodes!
    """
    pass


class Episode:
    """
        This class models the necessary information for a training episode.  Training
        episodes consist of:
            1. Metadata about the episode setting (room, name, description, etc)
            2. Utterances: Id of who is saying/acting, text/action, and target
            3. Present player id's (perhaps(?)) - may come in use for banning
    """

    def __init__(self, settings, agents, objects):
        # Dictionary from setting name to description
        self.settings = settings
        # Dictionaries from IDs to descriptions
        self.agents = agents
        self.objects = objects
        # Conversation, a list of utterances
        self.convo = []
        pass


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
