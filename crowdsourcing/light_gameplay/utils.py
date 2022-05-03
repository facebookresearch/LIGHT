#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import re

"""
Contains various utilities that make it easier to parse through the data
and prepare it for processing.
"""


def get_spawns(dialogue_data):
    spawns = []

    for turn in dialogue_data:
        text = turn["text"].strip()
        if turn["caller"] == "SoulSpawnEvent":
            spawns.append(text)
    
    return spawns


def was_tutorial(dialogue_data):
    spawns = get_spawns(dialogue_data)
    return (
        "You are, well, yourself... a wandering soul who has yet to become someone in the full LIGHT "
        "world. Perhaps you may be granted admission by the dungeon master?"
    ) in "\n".join(spawns)


def had_full_game(dialogue_data):
    spawns = get_spawns(dialogue_data)
    spawn_string = "\n".join(spawns)
    NON_TUTORIAL_INIT_REGEX = '(?!.*  You\.)Your soul possesses (.*?). Roleplay well, my friend, and earn experience points!'
    for line in spawn_string.split('\n'):
        if bool(re.match(NON_TUTORIAL_INIT_REGEX, line)):
            return True
    return False