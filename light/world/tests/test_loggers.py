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

        self.assertEqual(logger.data_path, self.data_dir)
        self.assertEqual(logger.graph, test_graph)
        self.assertEqual(logger.state_history, [])
        self.assertEqual(logger.event_buffer, [])
        self.assertEqual(logger.room_id, room_node.node_id)
        self.assertFalse(logger._is_logging())
        self.assertTrue(logger._is_players_afk())
        self.assertTrue(logger.is_active)
        self.assertEqual(len(logger.context_buffer), 0)

    def test_init_agent_logger(self):
        """
        Test the initial state of the agent logger from OOGraph
        """
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial
        logger = AgentInteractionLogger(test_graph, agent_node)

        self.assertEqual(logger.data_path, self.data_dir)
        self.assertEqual(logger.graph, test_graph)
        self.assertEqual(logger.state_history, [])
        self.assertEqual(logger.event_buffer, [])
        self.assertEqual(logger.agent, agent_node)
        self.assertFalse(logger._logging_intialized)
        self.assertFalse(logger._is_player_afk())
        self.assertTrue(logger.is_active)
        self.assertEqual(len(logger.context_buffer), 0)

    def test_begin_meta_episode_room_logger(self):
        """
        Test calling begin_meta_episode:
            - Clears all the buffers (context into event if nonempty)
            - adds the graph state from the room POV
            - counts as a turn of player action
            - initializes logger
        """
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial

        logger = test_graph.room_id_to_loggers[room_node.node_id]
        logger.event_buffer.append("Testing NOT!")
        logger.state_history.append("Testing")
        logger.context_buffer.append("Testing")
        logger._begin_meta_episode()

        self.assertFalse(logger._is_players_afk())
        self.assertEqual(len(logger.context_buffer), 0)
        self.assertEqual(logger.event_buffer, ["Testing"])
        self.assertEqual(len(logger.state_history), 1)
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
        self.assertEqual(len(logger.context_buffer), 0)
        self.assertEqual(len(logger.event_buffer), 0)
        self.assertEqual(len(logger.state_history), 1)
        self.assertEqual(
            logger.state_history[-1],
            test_graph.to_json_rv(agent_node.get_room().node_id),
        )

    def test_end_meta_episode_room_logger(self):
        """
        Test calling end_meta_episode:
            - Clears the context buffer
            ** Note, future test check that things are written properly
        """
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial

        logger = test_graph.room_id_to_loggers[room_node.node_id]
        logger.context_buffer.append("Testing")
        logger._end_meta_episode()

        self.assertEqual(len(logger.context_buffer), 0)

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
        logger.context_buffer.append("Testing")
        logger._add_player()

        self.assertTrue(logger._is_logging())
        self.assertFalse(logger._is_players_afk())
        self.assertEqual(len(logger.context_buffer), 0)
        self.assertEqual(logger.event_buffer, ["Testing"])
        self.assertEqual(len(logger.state_history), 1)
        self.assertEqual(
            logger.state_history[-1], test_graph.to_json_rv(logger.room_id)
        )
        self.assertEqual(logger.num_players_present, 1)

        # Another player just ups the count
        logger._add_player()
        self.assertEqual(len(logger.context_buffer), 0)
        self.assertEqual(logger.event_buffer, ["Testing"])
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
        self.assertEqual(len(logger.context_buffer), 0)
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

        # No player in room, so this should go to context
        logger.observe_event(test_event1)
        self.assertFalse(logger._is_logging())
        self.assertEqual(len(logger.event_buffer), 0)
        self.assertEqual(len(logger.context_buffer), 1)

        logger.observe_event(test_event2)
        logger.observe_event(test_event3)
        logger.observe_event(test_event4)
        logger.observe_event(test_event5)
        logger.observe_event(test_event6)
        self.assertFalse(logger._is_logging())
        self.assertEqual(len(logger.event_buffer), 0)
        self.assertEqual(len(logger.context_buffer), 5)
        events = [json for _, _, json, _ in logger.context_buffer]
        self.assertFalse(test_event1.to_json() in events)

        # player added, should be in event buffer
        logger._add_player()
        self.assertTrue(logger._is_logging())
        self.assertEqual(len(logger.event_buffer), 5)
        self.assertEqual(len(logger.context_buffer), 0)

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
        self.assertEqual(len(logger.context_buffer), 0)
        events = [json for _, _, json, _ in logger.event_buffer]
        self.assertTrue(test_event1.to_json() in events)

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
        self.assertEqual(len(logger.context_buffer), 0)
        events = [json for _, _, json, _ in logger.event_buffer]
        self.assertTrue(test_event1.to_json() in events)

    def test_afk_observe_event_room_logger(self):
        """
        Test that after 10 turns with no player, fill buffer, then dumps into main!
        """
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial
        logger = test_graph.room_id_to_loggers[room_node.node_id]
        logger._add_player()

        test_event1 = ArriveEvent(agent_node, text_content="hello1")
        for i in range(20):
            logger.observe_event(test_event1)

        # Only up to 5 in buffer, that is the limit
        self.assertTrue(logger._is_players_afk())
        self.assertEqual(len(logger.event_buffer), 10)
        self.assertEqual(len(logger.context_buffer), 5)

        # Now, player event - dump to buffer!
        agent_node.is_player = True
        logger.observe_event(test_event1)
        self.assertFalse(logger._is_players_afk())
        self.assertEqual(len(logger.event_buffer), 16)
        self.assertEqual(len(logger.context_buffer), 0)

    def test_afk_observe_event_agent_logger(self):
        """
        Test that after 25 turns with no player, fill buffer, then dumps into main!
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
        self.assertEqual(len(logger.event_buffer), 25)
        self.assertEqual(len(logger.context_buffer), 5)

        test_event2 = ArriveEvent(agent_node, text_content="hello2")
        logger.observe_event(test_event2)
        self.assertFalse(logger._is_player_afk())
        self.assertEqual(len(logger.event_buffer), 31)
        self.assertEqual(len(logger.context_buffer), 0)

    def test_simple_room_logger_saves_and_loads_init_graph(self):
        """
        Test that the room logger properly saves and reloads the initial
        graph
        """
        # Set up the graph
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial
        room_logger = test_graph.room_id_to_loggers[room_node.node_id]

        # Check the room json was done correctly
        test_init_json = test_world.oo_graph.to_json_rv(room_node.node_id)
        room_logger._begin_meta_episode()
        room_logger._end_meta_episode()
        graph_file = os.path.join(
            self.data_dir, "light_graph_dumps", f"{room_logger._last_graphs[-1]}.json"
        )
        with open(graph_file, "r") as graph_json_file:
            written_init_json = graph_json_file.read()
            self.assertEqual(test_init_json, written_init_json)

    def test_simple_room_logger_saves_and_loads_event(self):
        """
        Test that the room logger properly saves and reloads an event
        """
        # Set up the graph
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial
        agent_node.is_player = True
        room2_node = test_graph.add_room("test room2", {})
        room_logger = test_graph.room_id_to_loggers[room_node.node_id]

        # Check an event json was done correctly
        test_event = ArriveEvent(agent_node, text_content="")
        test_init_json = test_world.oo_graph.to_json_rv(agent_node.get_room().node_id)
        room_logger.observe_event(test_event)
        room_logger._end_meta_episode()

        ref_json = test_event.to_json()
        event_file = room_logger._last_event_log
        self.assertNotEqual(os.stat(event_file).st_size, 0)
        buff = read_event_logs(event_file)
        assert len(buff) == 1

        world_name, hash_, timestamp, written_event = buff[0]
        self.assertEqual(world_name, room_logger._last_graphs[-1])
        self.assertEqual(hash_, str(test_event.__hash__()))
        ref_json = json.loads(ref_json)
        event_ref = json.loads(written_event)
        self.assertEqual(event_ref, ref_json)

    def test_simple_agent_logger_saves_and_loads_init_graph(self):
        """
        Test that the agent logger properly saves and reloads the initial
        graph
        """
        # Set up the graph
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial

        # Check the graph json was done correctly from agent's room
        test_init_json = test_world.oo_graph.to_json_rv(room_node.node_id)
        agent_logger = AgentInteractionLogger(test_graph, agent_node)
        agent_logger._begin_meta_episode()
        agent_logger._end_meta_episode()
        graph_file = os.path.join(
            self.data_dir, "light_graph_dumps", f"{agent_logger._last_graphs[-1]}.json"
        )
        with open(graph_file, "r") as graph_json_file:
            written_init_json = graph_json_file.read()
            self.assertEqual(test_init_json, written_init_json)

    def test_simple_agent_logger_saves_and_loads_event(self):
        """
        Test that the agent logger properly saves and reloads an event
        """
        # Set up the graph
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial
        agent_node.is_player = True
        room2_node = test_graph.add_room("test room2", {})
        room_logger = test_graph.room_id_to_loggers[room_node.node_id]

        # Check an event json was done correctly
        test_event = ArriveEvent(agent_node, text_content="")
        test_init_json = test_world.oo_graph.to_json_rv(agent_node.get_room().node_id)
        agent_logger = AgentInteractionLogger(test_graph, agent_node)
        agent_logger._begin_meta_episode()
        agent_logger.observe_event(test_event)
        agent_logger._end_meta_episode()
        ref_json = test_event.to_json()
        event_file = agent_logger._last_event_log
        self.assertNotEqual(os.stat(event_file).st_size, 0)
        buff = read_event_logs(event_file)
        assert len(buff) == 1

        world_name, hash_, timestamp, written_event = buff[0]
        self.assertEqual(world_name, agent_logger._last_graphs[-1])
        self.assertEqual(hash_, str(test_event.__hash__()))
        ref_json = json.loads(ref_json)
        event_ref = json.loads(written_event)
        self.assertEqual(event_ref, ref_json)

    def test_simple_room_logger_e2e(self):
        """
        Test that the room logger properly saves and reloads the graph and events
        """
        # Set up the graph
        initial = self.setUp_single_room_graph()
        test_graph, test_world, agent_node, room_node = initial
        agent_node.is_player = True
        room_node2 = test_graph.add_room("test room2", {})
        room_logger = test_graph.room_id_to_loggers[room_node.node_id]
        test_graph.add_paths_between(
            room_node, room_node2, "a path to the north", "a path to the south"
        )
        test_graph.room_id_to_loggers[room_node.node_id]._add_player()

        # Check the room and event json was done correctly for room_node
        event_room_node_observed = LeaveEvent(
            agent_node, target_nodes=[room_node2]
        ).to_json()
        test_init_json = test_world.oo_graph.to_json_rv(room_node.node_id)

        GoEvent(agent_node, target_nodes=[room_node2]).execute(test_world)

        room_logger = test_graph.room_id_to_loggers[room_node.node_id]
        graph_file = os.path.join(
            self.data_dir, "light_graph_dumps", f"{room_logger._last_graphs[-1]}.json"
        )
        self.assertNotEqual(os.stat(graph_file).st_size, 0)
        with open(graph_file, "r") as graph_json_file:
            written_init_json = graph_json_file.read()
            self.assertEqual(test_init_json, written_init_json)
        event_file = room_logger._last_event_log
        self.assertNotEqual(os.stat(event_file).st_size, 0)
        buff = read_event_logs(event_file)
        assert len(buff) == 1

        world_name, hash_, timestamp, written_event = buff[0]
        self.assertEqual(world_name, room_logger._last_graphs[-1])
        ref_json = json.loads(event_room_node_observed)
        event_ref = json.loads(written_event)
        for k in ref_json:
            self.assertEqual(ref_json[k], event_ref[k], f"Event Json should match")


if __name__ == "__main__":
    unittest.main()
