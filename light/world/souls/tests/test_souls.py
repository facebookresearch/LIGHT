#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.abs

import unittest
import time
import asyncio

from light.graph.elements.graph_nodes import GraphAgent
from light.graph.structured_graph import OOGraph
from light.world.world import World, WorldConfig
from light.graph.events.graph_events import EmoteEvent, SayEvent
from light.world.souls.mock_soul import MockSoul
from light.world.souls.repeat_soul import RepeatSoul


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


class MockSouls(unittest.TestCase):
    """Unit tests for simple souls"""

    def test_init_soul(self):
        """Ensure that souls can be created"""
        test_graph = OOGraph()
        agent_node = test_graph.add_agent("My test agent", {})
        room_node = test_graph.add_room("test room", {})
        agent_node.force_move_to(room_node)
        test_world = World(WorldConfig(), True)
        test_world.oo_graph = test_graph
        mock_soul = MockSoul(agent_node, test_world)
        self.assertEqual(agent_node, mock_soul.target_node)
        self.assertEqual(test_world, mock_soul.world)

        test_event = EmoteEvent.construct_from_args(
            agent_node, targets=[], text="smile"
        )
        mock_soul.do_act(test_event)

        asyncio.run(mock_soul.reap())

    @async_test
    async def test_message_sending(self):
        """
        Ensure that messages can be sent to souls when acting in the world
        """
        # Set up scenario with two nodes in a room
        test_graph = OOGraph()
        test_node = test_graph.add_agent("TestAgent", {})
        repeat_node = test_graph.add_agent("RepeatAgent", {})
        room_node = test_graph.add_room("TestLab", {})
        test_node.force_move_to(room_node)
        repeat_node.force_move_to(room_node)

        test_world = World(WorldConfig(), True)
        test_world.oo_graph = test_graph

        purgatory = test_world.purgatory
        purgatory.register_filler_soul_provider("test", MockSoul, lambda: [])
        purgatory.register_filler_soul_provider("repeat", RepeatSoul, lambda: [])

        purgatory.fill_soul(test_node, "test")
        self.assertIn(test_node.node_id, purgatory.node_id_to_soul)
        test_node.is_player = True
        purgatory.fill_soul(repeat_node, "repeat")
        self.assertIn(repeat_node.node_id, purgatory.node_id_to_soul)

        mock_soul: "MockSoul" = purgatory.node_id_to_soul[test_node.node_id]
        repeat_soul = purgatory.node_id_to_soul[repeat_node.node_id]

        # Make the test soul act, and observe what follows
        test_event = EmoteEvent.construct_from_args(test_node, targets=[], text="smile")
        mock_soul.do_act(test_event)

        observations = mock_soul.observations
        start_time = time.time()
        OBSERVATION_WAIT_TIMEOUT = 3.3
        while len(observations) < 3:
            self.assertTrue(
                time.time() - start_time < OBSERVATION_WAIT_TIMEOUT,
                f"Exceeded expected duration {OBSERVATION_WAIT_TIMEOUT} waiting "
                f"for parrot events, found {mock_soul.observations}",
            )
            observations = mock_soul.observations
            await asyncio.sleep(0.01)

        # Observations should be the self smile event, then the repeat agent's say and smile
        self.assertEqual(len(observations), 3, "Unexpected amount of observations")

        self_emote_observe = observations[0]
        self.assertEqual(type(self_emote_observe), EmoteEvent)
        self.assertEqual(self_emote_observe.actor, test_node)
        self.assertEqual(self_emote_observe.text_content, "smile")

        other_say_observe = observations[1]
        self.assertEqual(type(other_say_observe), SayEvent)
        self.assertEqual(other_say_observe.actor, repeat_node)
        self.assertEqual(
            other_say_observe.text_content,
            "I just saw the following: The TestAgent smiles.",
        )

        other_emote_observe = observations[2]
        self.assertEqual(type(other_emote_observe), EmoteEvent)
        self.assertEqual(other_emote_observe.actor, repeat_node)
        self.assertEqual(other_emote_observe.text_content, "smile")

        observations = mock_soul.observations
        # Extra observation may have slipped in?
        self.assertEqual(len(observations), 3, "Unexpected amount of observations")
        self.assertEqual(
            len(mock_soul._observe_futures), 0, "All obs threads should have deleted"
        )


if __name__ == "__main__":
    unittest.main()
