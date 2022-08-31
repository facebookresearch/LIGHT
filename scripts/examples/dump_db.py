#!/usr/bin/env python3


# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# To run:
# python scripts/examples/dump_db.py
#
# It will save the data in a json file "/tmp/db.json"  by default

import sys

import parlai.utils.misc as parlai_utils

from light.graph.builders.map_json_builder import MapJsonBuilder
from light.graph.builders.starspace_assisted import StarspaceBuilder
from light.data_model.light_database import LIGHTDatabase
from light.world.utils.terminal_player_provider import TerminalPlayerProvider
from parlai.core.params import ParlaiParser
from light.world.world import World
from light.world.souls.repeat_soul import RepeatSoul
from light.world.souls.on_event_soul import OnEventSoul

import os
import random
import numpy
import asyncio
import json

random.seed(6)
numpy.random.seed(6)

parser = ParlaiParser()
parser.add_argument("--save-json", type=str, default="/tmp/db.json")
opt, _unknown = parser.parse_and_process_known_args()

StarspaceBuilder.add_parser_arguments(parser)
opt, _unknown = parser.parse_and_process_known_args()
print("[loading db...]")
ldb = LIGHTDatabase(opt["light_db_file"], read_only=True)
from light.graph.builders.base import DBGraphBuilder

ldbg = DBGraphBuilder(ldb)
rooms = ldbg.get_usable_rooms()
chars = ldbg.get_usable_chars()
objs = ldbg.get_usable_objects()
items = []
for ind in objs:
    item = ldb.get_object(ind)[0]
    item["is_object"] = True
    if item["is_plural"] != 1.0:
        items.append(item)
for ind in chars:
    item = ldb.get_character(ind)[0]
    item["is_character"] = True
    if item["is_plural"] != 1.0:
        items.append(item)
for ind in rooms:
    item = ldb.get_room(ind)[0]
    item["is_room"] = True
    items.append(item)

txt = json.dumps(items, sort_keys=True, indent=4)
fw = open(opt["save_json"], "w")
fw.write(txt)
fw.close()
