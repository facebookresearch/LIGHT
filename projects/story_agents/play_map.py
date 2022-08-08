#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


"""
Simple example script that demonstrates initializing and using a world with Souls.

Given the world in --in-file (default map.json), initializes the base soul in any
available agents. As the base soul right now awaits human input, you get to control the character.

Derived from /scripts/play_map.py
"""

from example_base_soul import ExampleBaseSoul
from light import LIGHT_DIR
from light.graph.builders.map_json_builder import MapJsonBuilder
from light.data_model.light_database import LIGHTDatabase
from parlai.core.params import ParlaiParser
import asyncio


import os


BASE_DPATH = os.path.join(LIGHT_DIR, "data")
LIGHT_DB_FILE_LOC = os.path.join(LIGHT_DIR, "data", "env", "database3.db")
CURR_DIR = os.path.dirname(__file__)


if __name__ == "__main__":
    parser = ParlaiParser()
    parser.add_argument("--map-file", type=str, default="map.json")
    opt, _unknown = parser.parse_and_process_known_args()
    opt["load_map"] = os.path.join(CURR_DIR, "outputs", opt["map_file"])
    print("[loading db...]")
    ldb = LIGHTDatabase(LIGHT_DB_FILE_LOC)
    print("[loading map...]")
    world_builder = MapJsonBuilder(episode_db=None, opt=opt)
    graph, world = asyncio.run(world_builder.get_graph())

    # Set up the world
    purgatory = world.purgatory
    purgatory.register_filler_soul_provider("base", ExampleBaseSoul, lambda: [])
    for empty_agent in world.oo_graph.agents.values():
        purgatory.fill_soul(
            empty_agent
        )  # Associates an ExampleBaseSoul with every agent

    # Construct an event loop that runs forever
    while True:
        for empty_agent in world.oo_graph.agents.values():
            inst = input(f"{empty_agent} enter act> ")
            asyncio.run(
                world.parse_exec(empty_agent, inst=inst)
            )  # Triggers the event, and following `observe_event`s
