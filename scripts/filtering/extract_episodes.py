#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
    This file is responsible for extracting the episodes from a meta episode log
    This involves:
        1. Finding the start/stop of conversations
        2. Capture relevant metadata
            - task (?)
            - _setting_name
            - _setting_desc
            - _partner(s)_name (? - multiple)
            - _self_name
            - _self_persona
            - _object_desc
            - _self_say
            - _partner_say
            - _self_emote
            - _partner_emote
            - _self_act
            - _partner_act
        3. Take events and parse out the convo
            - say can be SayEvent, TellEvent, WhisperEvent(?)
            - emotes are emotes
            - all other are act events
        4. Return a list of the episodes
"""
