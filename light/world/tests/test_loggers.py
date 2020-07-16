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

from parlai.core.params import ParlaiParser

class TestInteractionLoggers(unittest.TestCase):
    """Unit tests for Interaction Loggers"""

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.parser = ParlaiParser()
        self.parser.add_argument(
            '--is-logging',
            type='bool',
            default=True,
            help="Log events with interaction loggers",
        )
        self.parser.add_argument(
            '--log-path',
            type=str,
            default=self.data_dir,
            help="Write the events logged to this path",
        )

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def test_simple_room_logger_saves_and_loads_init_graph(self):
        """
        Test that the room logger properly saves and reloads the initial 
        graph
        """
        # Set up the graph 
        opt, _ = self.parser.parse_and_process_known_args()
        test_graph = OOGraph(opt)
        agent_node = test_graph.add_agent("My test agent", {})
        room_node = test_graph.add_room("test room", {})
        agent_node.force_move_to(room_node)
        test_world = World({}, None, True)
        test_world.oo_graph = test_graph 
        room_logger = test_graph.room_id_to_loggers[room_node.node_id]

        # Check the room json was done correctly
        test_init_json = test_world.oo_graph.to_json_rv(room_node.node_id)
        room_logger._begin_meta_episode()
        room_logger._end_meta_episode()
        graph_file = os.path.join(self.data_dir, 'light_graph_dumps',f'{room_logger._last_graphs[-1]}.json')
        with open(graph_file, 'r') as graph_json_file:
            written_init_json = graph_json_file.read()
            self.assertEqual(test_init_json, written_init_json)
    
    def test_simple_room_logger_saves_and_loads_event(self):
        """
        Test that the room logger properly saves and reloads an event 
        """
        # Set up the graph 
        opt, _ = self.parser.parse_and_process_known_args()
        test_graph = OOGraph(opt)
        agent_node = test_graph.add_agent("My test agent", {})
        agent_node.is_player = True
        room_node = test_graph.add_room("test room", {})
        room2_node = test_graph.add_room("test room2", {})
        agent_node.force_move_to(room_node)
        test_world = World({}, None, True)
        test_world.oo_graph = test_graph 
        room_logger = test_graph.room_id_to_loggers[room_node.node_id]

        # Check an event json was done correctly
        test_event = ArriveEvent(agent_node, text_content="")
        test_init_json = test_world.oo_graph.to_json_rv(agent_node.get_room().node_id)
        room_logger.observe_event(test_event)
        room_logger._end_meta_episode()

        ref_json = test_event.to_json()
        event_file = room_logger._last_event_log
        self.assertNotEqual(os.stat(event_file).st_size, 0)
        # Note:  Lines alternate graph-hash, timestamp, json, use parity to help with this!
        with open(event_file, 'r') as event_json_file:
            parity = 0
            for line in event_json_file:
                # check graph
                if parity == 0:
                    world_hash = line.split(" ")
                    self.assertEqual(world_hash[0], room_logger._last_graphs[-1])
                    self.assertEqual(world_hash[1], str(test_event.__hash__()) + "\n")
                elif parity == 2:
                    written_event = json.loads(line)
                    ref_json = json.loads(ref_json)
                    self.assertEqual(ref_json, written_event)
                parity += 1
                parity %= 3

    def test_simple_agent_logger_saves_and_loads_init_graph(self):
        """
        Test that the agent logger properly saves and reloads the initial 
        graph
        """
        # Set up the graph 
        opt, _ = self.parser.parse_and_process_known_args()
        test_graph = OOGraph(opt)
        agent_node = test_graph.add_agent("My test agent", {})
        room_node = test_graph.add_room("test room", {})
        agent_node.force_move_to(room_node)
        test_world = World({}, None, True)
        test_world.oo_graph = test_graph 

        # Check the graph json was done correctly from agent's room
        test_init_json = test_world.oo_graph.to_json_rv(room_node.node_id)
        agent_logger = AgentInteractionLogger(test_graph, agent_node)
        agent_logger._begin_meta_episode()
        agent_logger._end_meta_episode()
        graph_file = os.path.join(self.data_dir, 'light_graph_dumps',f'{agent_logger._last_graphs[-1]}.json')
        with open(graph_file, 'r') as graph_json_file:
            written_init_json = graph_json_file.read()
            self.assertEqual(test_init_json, written_init_json)
    
    def test_simple_agent_logger_saves_and_loads_event(self):
        """
        Test that the room logger properly saves and reloads an event 
        """
        # Set up the graph 
        opt, _ = self.parser.parse_and_process_known_args()
        test_graph = OOGraph(opt)
        agent_node = test_graph.add_agent("My test agent", {})
        agent_node.is_player = True
        room_node = test_graph.add_room("test room", {})
        room2_node = test_graph.add_room("test room2", {})
        agent_node.force_move_to(room_node)
        test_world = World({}, None, True)
        test_world.oo_graph = test_graph 

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
        # Note:  Lines alternate timestamp, json, use parity to help with this!
        with open(event_file, 'r') as event_json_file:
            parity = 0
            for line in event_json_file:
                # check graph
                if parity == 0:
                    world_hash = line.split(" ")
                    self.assertEqual(world_hash[0], agent_logger._last_graphs[-1])
                    self.assertEqual(world_hash[1], str(test_event.__hash__()) + "\n")
                elif parity == 2:
                    written_event = json.loads(line)
                    ref_json = json.loads(ref_json)
                    self.assertEqual(ref_json, written_event)
                parity += 1
                parity %= 3

    # TODO: Add simple unit type test - create new graph, loggers, log the events seperate tada!
    def test_simple_room_logger_e2e(self):
        """
        Test that the room logger properly saves and reloads the graph and events
        """
        # Set up the graph 
        opt, _ = self.parser.parse_and_process_known_args()
        test_graph = OOGraph(opt)
        agent_node = test_graph.add_agent("My test agent", {})
        agent_node.is_player = True
        room_node = test_graph.add_room("test room", {})
        room_node2 = test_graph.add_room("test room2", {})
        test_graph.add_paths_between(room_node, room_node2, 'a path to the north', 'a path to the south')
        agent_node.force_move_to(room_node)
        test_graph.room_id_to_loggers[room_node.node_id]._add_player()

        # Now, set the player flag
        test_world = World({}, None, True)
        test_world.oo_graph = test_graph 


        # Check the room and event json was done correctly for room_node
        event_room_node_observed = LeaveEvent(agent_node, target_nodes=[room_node2]).to_json()
        test_init_json = test_world.oo_graph.to_json_rv(room_node.node_id)

        test_event = GoEvent(agent_node, target_nodes=[room_node2]).execute(test_world)
        
        room_logger = test_graph.room_id_to_loggers[room_node.node_id]
        graph_file = os.path.join(self.data_dir, 'light_graph_dumps', f'{room_logger._last_graphs[-1]}.json')       
        self.assertNotEqual(os.stat(graph_file).st_size, 0)
        with open(graph_file, 'r') as graph_json_file:
            written_init_json = graph_json_file.read()
            self.assertEqual(test_init_json, written_init_json)
        event_file = room_logger._last_event_log
        self.assertNotEqual(os.stat(event_file).st_size, 0)
        with open(event_file, 'r') as event_json_file:
            parity = 0
            for line in event_json_file:
                # check graph
                if parity == 0:
                    world_hash = line.split(" ")
                    self.assertEqual(world_hash[0], room_logger._last_graphs[-1])
                elif parity == 2:
                    written_event = json.loads(line)
                    ref_json = json.loads(event_room_node_observed)
                    self.assertEqual(ref_json, written_event)
                parity += 1
                parity %= 3



if __name__ == "__main__":
    unittest.main()
