#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.abs

import unittest
import os
import asyncio
import time
from light import LIGHT_DIR
from light.graph.builders.map_json_builder import MapJsonBuilder, MapJsonBuilderConfig
from light.world.souls.tests.battle_royale_soul import BattleRoyaleSoul
from light.world.world import WorldConfig
from light.graph.elements.graph_nodes import TICKS_TO_CLEAN_CORPSE

# Magic number to ensure we wait more than the expected ticks to clean a corpse
ENOUGH_EXTRA_TICKS_TO_ENSURE_CORPSE_CLEANUP = 20


def async_test(f):
    def wrapper(*args, **kwargs):
        coro = f
        try:
            loop = asyncio.get_event_loop()
            future = coro(*args, **kwargs)
            loop.run_until_complete(future)
        except RuntimeError:
            try:
                loop = asyncio.get_running_loop()
                future = coro(*args, **kwargs)
                loop.run_until_complete(future)
            except RuntimeError:
                asyncio.run(coro(*args, **kwargs))

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
        world_builder = MapJsonBuilder(
            MapJsonBuilderConfig(
                load_map=os.path.join(LIGHT_DIR, "scripts/examples/complex_world.json")
            )
        )
        g, world = await world_builder.get_graph(WorldConfig())
        purgatory = world.purgatory
        purgatory.register_filler_soul_provider(
            "battle",
            BattleRoyaleSoul,
            lambda: [],
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

        self.assertTrue(len(g.agents) == current_agents + 20)
        current_agents += 20

        # run some steps
        await run_some_time(2)

        # some agents definitely should have died
        self.assertLess(len(g.agents), current_agents)

        current_agents = len(g.agents)
        current_objects = len(g.objects)
        current_dead = len(g.dead_nodes)

        # try respawning
        use_ticks = TICKS_TO_CLEAN_CORPSE + ENOUGH_EXTRA_TICKS_TO_ENSURE_CORPSE_CLEANUP
        for _x in range(use_ticks):
            ags = await world.clean_corpses_and_respawn()
            for ag in ags:
                purgatory.fill_soul(ag)

        # some agents definitely should have respawned
        self.assertGreater(len(g.agents), current_agents)
        self.assertLess(len(g.objects), current_objects)
        self.assertLess(len(g.dead_nodes), current_dead)


if __name__ == "__main__":
    unittest.main()
