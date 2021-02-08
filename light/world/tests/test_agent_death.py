#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.abs

import unittest
import os
import asyncio
import time
from light.graph.builders.map_json_builder import MapJsonBuilder
from light.world.souls.tests.battle_royale_soul import BattleRoyaleSoul

def async_test(f):
    def wrapper(*args, **kwargs):
        coro = f
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)

    return wrapper


class TestInteractionLoggers(unittest.TestCase):
    """Unit tests for Interaction Loggers"""

    @async_test
    async def test_run(self):
        """
        Test running a world where agents will be dying.
        """
        # Populate a world
        await asyncio.sleep(0.1)
        loop = asyncio.get_running_loop()
        opt = {}
        opt["load_map"] = os.path.expanduser('~/LIGHT/scripts/examples/complex_world.json')
        world_builder = MapJsonBuilder("", debug=False, opt=opt)
        g, world = world_builder.get_graph()
        purgatory = world.purgatory
        purgatory.register_filler_soul_provider(
            "battle", BattleRoyaleSoul, lambda: [{}],
        )
        for empty_agent in world.oo_graph.agents.values():
            purgatory.fill_soul(empty_agent)

        # Ensure there are agents within
        starting_agents = len(g.agents)
        self.assertTrue(starting_agents >= 10)

        async def run_some_time(max_time):
            start_time = time.time()
            while time.time() - start_time < max_time:
                await asyncio.sleep(0.1)
        
        # run some steps
        await run_some_time(2)
        # some agents definitely should have died
        self.assertTrue(len(g.agents) < starting_agents)

        current_agents = len(g.agents)

        for _x in range(20):
            empty_agent = world_builder.force_add_agent(world)
            purgatory.fill_soul(empty_agent)

        
        self.assertTrue(len(g.agents) == current_agents + 10)
        current_agents += 10
        
        # run some steps
        await run_some_time(2)

        # some agents definitely should have died
        self.assertTrue(len(g.agents) < current_agents)


if __name__ == "__main__":
    unittest.main()
