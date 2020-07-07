#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.abs

import unittest
import time

from light.graph.elements.graph_nodes import GraphAgent
from light.graph.structured_graph import OOGraph
from light.world.world import World
from light.graph.events.graph_events import EmoteEvent, SayEvent
from light.world.souls.test_soul import TestSoul
from light.world.souls.repeat_soul import RepeatSoul


class TestSouls(unittest.TestCase):
    """Unit tests for simple souls"""

    def test_init_soul(self):
        """Ensure that souls can be created"""
        test_graph = OOGraph()
        agent_node = test_graph.add_agent("My test agent", {})
        room_node = test_graph.add_room("test room", {})
        agent_node.force_move_to(room_node)
        test_world = World({}, None, True)
        test_world.oo_graph = test_graph
        test_soul = TestSoul(agent_node, test_world)
        self.assertEqual(agent_node, test_soul.target_node)
        self.assertEqual(test_world, test_soul.world)

        test_event = EmoteEvent.construct_from_args(
            agent_node, targets=[], text="smile"
        )
        test_soul.do_act(test_event)

        test_soul.reap()

    def test_message_sending(self):
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

        test_world = World({}, None, True)
        test_world.oo_graph = test_graph

        purgatory = test_world.purgatory
        purgatory.register_filler_soul_provider("test", TestSoul, lambda: [])
        purgatory.register_filler_soul_provider("repeat", RepeatSoul, lambda: [])

        purgatory.fill_soul(test_node, "test")
        self.assertIn(test_node.node_id, purgatory.node_id_to_soul)
        purgatory.fill_soul(repeat_node, "repeat")
        self.assertIn(repeat_node.node_id, purgatory.node_id_to_soul)

        test_soul: "TestSoul" = purgatory.node_id_to_soul[test_node.node_id]
        repeat_soul = purgatory.node_id_to_soul[repeat_node.node_id]

        # Make the test soul act, and observe what follows
        test_event = EmoteEvent.construct_from_args(test_node, targets=[], text="smile")
        test_soul.do_act(test_event)

        observations = test_soul.observations
        start_time = time.time()
        OBSERVATION_WAIT_TIMEOUT = 0.3
        while len(observations) < 3:
            self.assertTrue(
                time.time() - start_time < OBSERVATION_WAIT_TIMEOUT,
                f"Exceeded expected duration {OBSERVATION_WAIT_TIMEOUT} waiting for parrot events",
            )
            observations = test_soul.observations
            time.sleep(0.01)

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
            "I just saw the following: The testagent smiles",
        )

        other_emote_observe = observations[2]
        self.assertEqual(type(other_emote_observe), EmoteEvent)
        self.assertEqual(other_emote_observe.actor, repeat_node)
        self.assertEqual(other_emote_observe.text_content, "smile")

        observations = test_soul.observations
        # Extra observation may have slipped in?
        self.assertEqual(len(observations), 3, "Unexpected amount of observations")
        self.assertEqual(len(test_soul._observe_threads), 0, "All obs threads should have deleted")

if __name__ == "__main__":
    unittest.main()
