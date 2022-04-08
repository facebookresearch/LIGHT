#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# To run, use:
# python scripts/examples/play_map.py --use-models GenerativeHeuristicModelSoul

import sys

import parlai.utils.misc as parlai_utils

from light.graph.builders.tutorial_builder import TutorialWorldBuilder
from light.data_model.light_database import LIGHTDatabase
from light.world.utils.terminal_player_provider import TerminalPlayerProvider
from light.world.world import World
from light.world.souls.tutorial_player_soul import TutorialPlayerSoul
from light.world.souls.models.tutorial_model_soul import TutorialModelSoul
from light.world.purgatory import TutorialPurgatory

import os
import random
import numpy
import asyncio

TUTORIAL_FILE = os.path.join(os.path.dirname(__file__), "tutorial_world.json")

random.seed(6)
numpy.random.seed(6)
shared_model_content = None


async def ainput(string: str) -> str:
    await asyncio.get_event_loop().run_in_executor(
        None, lambda s=string: sys.stdout.write(s + " ")
    )
    return await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)


def init_world():
    world_builder = TutorialWorldBuilder(None, opt={"load_map": TUTORIAL_FILE})
    g, world = world_builder.get_graph()
    # NOTE: I just took the act_model_path from elsewhere
    shared_resources = TutorialModelSoul.load_models(
        dialog_model_path="zoo:light_whoami/profile_expanded_attention_128/model",
        act_model_path="/checkpoint/light/models/game2021/act_model/model"
    )
    # shared_resources = {}
    purgatory = world.purgatory
    purgatory.register_filler_soul_provider(
        "tutorial",
        TutorialModelSoul,
        lambda: [shared_resources],
    )
    dm_agent = [a for a in list(g.agents.values()) if a.name == "Dungeon Master"][0]
    purgatory.fill_soul(dm_agent, "tutorial")

    provider = TerminalPlayerProvider(purgatory)
    return provider


async def run_tutorial():
    """
    Takes in a World object and its OOGraph and allows one to play with a random map
    """
    player_provider = init_world()
    player_provider.process_terminal_act("")  # get an agent
    await asyncio.sleep(0.01)
    while True:
        act = await ainput("\raction> ")
        if act == "":
            continue
        if act == "exit":
            print("Exiting graph run")
            return
        elif act in ["new", "reset"]:
            print("A mist fills the world and everything resets")
            player_provider = init_world()
            player_provider.process_terminal_act("")  # get an agent
            await asyncio.sleep(0.4)
        else:
            player_provider.process_terminal_act(act)
        await asyncio.sleep(0.4)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_tutorial())
