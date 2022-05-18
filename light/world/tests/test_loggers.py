#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.abs

import unittest
import shutil, tempfile
import os
import json

from light.graph.elements.graph_nodes import GraphAgent
from light.graph.structured_graph import OOGraph
from light.world.world import World
from light.graph.events.graph_events import ArriveEvent, LeaveEvent, GoEvent, LookEvent
from light.world.content_loggers import AgentInteractionLogger, RoomInteractionLogger
from light.world.utils.json_utils import read_event_logs
from parlai.core.params import ParlaiParser


class TestInteractionLoggers(unittest.TestCase):
    """Unit tests for Interaction Loggers"""

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        # TODO: Remove reliance on this, just use argparser
        self.parser = ParlaiParser(
            True, True, "Arguments for building a LIGHT world with Starspace"
        )
        self.parser.add_argument(
            "--is-logging",
            type="bool",
            default=True,
            help="Log events with interaction loggers",
        )
        self.parser.add_argument(
            "--log-path",
            type=str,
            default=self.data_dir,
            help="Write the events logged to this path",
        )

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def setUp_single_room_graph(self):
        # Set up the graph
        opt, _ = self.parser.parse_and_process_known_args()
        test_graph = OOGraph(opt)
        agent_node = test_graph.add_agent("My test agent", {})
        room_node = test_graph.add_room("test room", {})
        agent_node.force_move_to(room_node)
        test_world = World({}, None, True)
        test_world.oo_graph = test_graph
        return (test_graph, test_world, agent_node, room_node)

    def test_init_room_logger(self):
        """
        Test the initial state of room loggers from OOGraph() constructor matches expected values
        """
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial
        logger = test_graph.room_id_to_loggers[room_node.node_id]

        self.assertEqual(logger.graph, test_graph)
        self.assertEqual(logger.state_history, [])
        self.assertEqual(logger.event_buffer, [])
        self.assertEqual(logger.room_id, room_node.node_id)
        self.assertFalse(logger._is_logging())
        self.assertTrue(logger._is_players_afk())
        self.assertTrue(logger.is_active)

    def test_init_agent_logger(self):
        """
        Test the initial state of the agent logger from OOGraph
        """
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial
        logger = AgentInteractionLogger(test_graph, agent_node)

        self.assertEqual(logger.graph, test_graph)
        self.assertEqual(logger.state_history, [])
        self.assertEqual(logger.event_buffer, [])
        self.assertEqual(logger.agent, agent_node)
        self.assertFalse(logger._logging_intialized)
        self.assertFalse(logger._is_player_afk())
        self.assertTrue(logger.is_active)

    def test_begin_meta_episode_room_logger(self):
        """
        Test calling begin_meta_episode:
            - Clears all the buffers
            - adds the graph state from the room POV
            - counts as a turn of player action
            - initializes logger
        """
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial

        logger = test_graph.room_id_to_loggers[room_node.node_id]
        logger.event_buffer.append("Testing NOT!")
        logger.state_history.append("Testing")
        logger._begin_meta_episode()

        self.assertFalse(logger._is_players_afk())
        self.assertEqual(len(logger.state_history), 1, "Had extra in buffer")
        self.assertEqual(len(logger.event_buffer), 0, "Had extra in buffer")
        self.assertEqual(
            logger.state_history[-1], test_graph.to_json_rv(logger.room_id)
        )

    def test_begin_meta_episode_agent_logger(self):
        """
        Test calling begin_meta_episode:
            - Clears all the buffers
            - adds the graph state from the agent's room POV
            - counts as a turn of player action
            - initializes logger
        """
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial

        logger = AgentInteractionLogger(test_graph, agent_node)
        logger.event_buffer.append("Testing")
        logger.state_history.append("Testing")
        logger._begin_meta_episode()

        self.assertFalse(logger._is_player_afk())
        self.assertTrue(logger._logging_intialized)
        self.assertEqual(len(logger.event_buffer), 0)
        self.assertEqual(len(logger.state_history), 1)
        self.assertEqual(
            logger.state_history[-1],
            test_graph.to_json_rv(agent_node.get_room().node_id),
        )

    def test_end_meta_episode_room_logger(self):
        """
        Test calling end_meta_episode:
            ** Note, future test check that things are written properly
        """
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial

        logger = test_graph.room_id_to_loggers[room_node.node_id]
        logger._end_meta_episode()

    def test_end_meta_episode_agent_logger(self):
        """
        Test calling end_meta_episode:
            - Makes the logging intialized false again
            !! Note, will not have to worry about afk player ending (need the event)
            so we will not have to clear context buffer
        """
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial

        logger = AgentInteractionLogger(test_graph, agent_node)
        logger._end_meta_episode()

        self.assertFalse(logger._logging_intialized)

    def test_add_player_room_logger(self):
        """
        Test calling _add_player():
            - Starts logging and adds a player if there is none
            - just increments the count otherwise
        """
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial
        logger = test_graph.room_id_to_loggers[room_node.node_id]

        logger.event_buffer.append("Testing NOT!")
        logger.state_history.append("Testing")
        logger._add_player()

        self.assertTrue(logger._is_logging())
        self.assertFalse(logger._is_players_afk())
        self.assertEqual(len(logger.event_buffer), 0)
        self.assertEqual(len(logger.state_history), 1)
        self.assertEqual(
            logger.state_history[-1], test_graph.to_json_rv(logger.room_id)
        )
        self.assertEqual(logger.num_players_present, 1)

        # Another player just ups the count
        logger._add_player()
        self.assertEqual(len(logger.event_buffer), 0)
        self.assertEqual(len(logger.state_history), 1)
        self.assertEqual(
            logger.state_history[-1], test_graph.to_json_rv(logger.room_id)
        )
        self.assertEqual(logger.num_players_present, 2)

    def test_remove_player_room_logger(self):
        """
        Test calling _remove_player():
            - just decrements the count if multiple players
            - ends episode (meta_episode) otherwise
        """
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial
        logger = test_graph.room_id_to_loggers[room_node.node_id]
        logger._add_player()
        logger._add_player()

        logger._remove_player()
        self.assertTrue(logger._is_logging())
        self.assertFalse(logger._is_players_afk())
        self.assertEqual(logger.num_players_present, 1)

        # Another player is 0, end episode
        logger._remove_player()
        self.assertFalse(logger._is_logging())
        self.assertEqual(logger.num_players_present, 0)

    def test_observer_event_goes_context_room_logger(self):
        """
        Test calling observe_event under normal circumstances adds the
        necessary metadata to the event buffer
        """
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial
        logger = test_graph.room_id_to_loggers[room_node.node_id]

        test_event1 = ArriveEvent(agent_node, text_content="hello1")
        test_event2 = ArriveEvent(agent_node, text_content="hello2")
        test_event3 = ArriveEvent(agent_node, text_content="hello3")
        test_event4 = ArriveEvent(agent_node, text_content="hello4")
        test_event5 = ArriveEvent(agent_node, text_content="hello5")
        test_event6 = ArriveEvent(agent_node, text_content="hello6")

        # No player in room, so this should be skipped
        logger.observe_event(test_event1)
        self.assertFalse(logger._is_logging())
        self.assertEqual(len(logger.event_buffer), 0)
        logger.observe_event(test_event2)
        logger.observe_event(test_event3)
        logger.observe_event(test_event4)
        logger.observe_event(test_event5)
        logger.observe_event(test_event6)
        self.assertFalse(logger._is_logging())
        self.assertEqual(len(logger.event_buffer), 0)

    def test_observe_event_room_logger(self):
        """
        Test that calling observe_event with players present adds to the
        event, not the context buffer
        """

        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial
        logger = test_graph.room_id_to_loggers[room_node.node_id]

        logger._add_player()
        test_event1 = ArriveEvent(agent_node, text_content="hello1")
        logger.observe_event(test_event1)

        self.assertTrue(logger._is_logging())
        self.assertEqual(len(logger.event_buffer), 1)

    def test_observe_event_agent_logger(self):
        """
        Test calling observe_event under normal circumstances adds the
        necessary metadata to the event buffer
        """
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial
        logger = AgentInteractionLogger(test_graph, agent_node)

        logger._begin_meta_episode()
        test_event1 = ArriveEvent(agent_node, text_content="hello1")
        logger.observe_event(test_event1)

        self.assertEqual(len(logger.event_buffer), 1)

    def test_afk_observe_event_room_logger(self):
        """
        Test that after 30 turns with no player, clear when returns!
        """
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial
        logger = test_graph.room_id_to_loggers[room_node.node_id]
        logger._add_player()

        test_event1 = ArriveEvent(agent_node, text_content="hello1")
        for i in range(30):
            logger.observe_event(test_event1)

        # Only up to 5 in buffer, that is the limit
        self.assertTrue(logger._is_players_afk())
        self.assertEqual(len(logger.event_buffer), 30)

        # Now, player event - clear buffer!
        agent_node.is_player = True
        logger.observe_event(test_event1)
        self.assertFalse(logger._is_players_afk())
        self.assertEqual(len(logger.event_buffer), 0)

    def test_afk_observe_event_agent_logger(self):
        """
        Test that after 30 turns with no player, clear, then start new episode!
        """
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial
        agent_node2 = test_graph.add_agent("My test agent2", {})
        agent_node2.force_move_to(room_node)
        logger = AgentInteractionLogger(test_graph, agent_node)

        logger._begin_meta_episode()
        test_event1 = ArriveEvent(agent_node2, text_content="hello1")
        for i in range(35):
            logger.observe_event(test_event1)

        self.assertTrue(logger._is_player_afk())
        self.assertEqual(len(logger.event_buffer), 30)

        test_event2 = ArriveEvent(agent_node, text_content="hello2")
        logger.observe_event(test_event2)
        logger.observe_event(test_event2)
        self.assertFalse(logger._is_player_afk())
        self.assertEqual(len(logger.event_buffer), 1)


if __name__ == "__main__":
    unittest.main()
