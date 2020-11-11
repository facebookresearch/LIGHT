#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# To run on a devfair, use:
# python scripts/examples/play_random_map.py
# To run on Jack's laptop, run:
# python scripts/examples/play_random_map.py --light-model-root ~/Desktop/LIGHT/LIGHT_models/ --light-db-file ~/ParlAI/data/light/environment/db/database3.db

import sys

import parlai.utils.misc as parlai_utils

from light.graph.builders.map_json_builder import MapJsonBuilder
from light.graph.builders.starspace_all import StarspaceBuilder
from light.data_model.light_database import LIGHTDatabase
from light.world.utils.terminal_player_provider import TerminalPlayerProvider
from parlai.core.params import ParlaiParser
from light.world.world import World
from light.world.souls.repeat_soul import RepeatSoul
from light.world.souls.on_event_soul import OnEventSoul
from light.world.souls.models.partner_heuristic_model_soul import (
    PartnerHeuristicModelSoul,
)
import os
import random
import numpy
import asyncio
import json
random.seed(6)
numpy.random.seed(6)
shared_model_content = None


parser = ParlaiParser()
parser.add_argument(
    "--load-map", type=str, default="none"
)
opt, _unknown = parser.parse_and_process_known_args()

if opt["load_map"] != "none":
    Builder = MapJsonBuilder
    ldb = ""
    world_builder = Builder(ldb, debug=False, opt=opt)
else:
    StarspaceBuilder.add_parser_arguments(parser)
    opt, _unknown = parser.parse_and_process_known_args()
    print("[loading db...]")
    ldb = LIGHTDatabase(opt["light_db_file"], read_only=True)
    print("[loading builder model...]")
    world_builder = StarspaceBuilder(ldb, debug=False, opt=opt)

print("[building...]")
g, world = world_builder.get_graph() 
data = g.to_json()
print(data)
fw = open('/tmp/map.json', 'w')
fw.write(data)
fw.close()


# NOTE: To load back again:
# g2 = g.from_json(data) 
