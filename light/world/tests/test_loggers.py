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
from light.graph.events.graph_events import ArriveEvent, EmoteEvent
from light.world.content_loggers import RoomInteractionLogger

class TestInteractionLoggers(unittest.TestCase):
    """Unit tests for Interaction Loggers"""

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def test_simple_room_logger_saves_and_loads_init_graph(self):
        """
        Test that the room logger properly saves and reloads the initial 
        graph
        """
        test_graph = OOGraph()
        agent_node = test_graph.add_agent("My test agent", {})
        room_node = test_graph.add_room("test room", {})
        agent_node.force_move_to(room_node)
        test_world = World({}, None, True)
        test_world.oo_graph = test_graph 
        test_init_json = test_world.oo_graph.to_json_rv(room_node.node_id)
        room_logger = RoomInteractionLogger(test_graph, self.data_dir, room_node.node_id)
        room_logger._begin_meta_episode()
        room_logger._end_meta_episode()
        graph_file = os.path.join(self.data_dir, 'light_graph_dumps',f'{room_logger._last_logged_to}.json')
        with open(graph_file, 'r') as graph_json_file:
            written_init_json = graph_json_file.read()
            self.assertEqual(test_init_json, written_init_json)
    
    def test_simple_room_logger_saves_and_loads_event(self):
        """
        Test that the room logger properly saves and reloads an event 
        """
        test_graph = OOGraph()
        agent_node = test_graph.add_agent("My test agent", {})
        agent_node.is_player = True
        room_node = test_graph.add_room("test room", {})
        room2_node = test_graph.add_room("test room2", {})
        agent_node.force_move_to(room_node)
        test_world = World({}, None, True)
        test_world.oo_graph = test_graph 
        test_event = ArriveEvent(agent_node, text_content="")
        self.maxDiff = None
        test_init_json = test_world.oo_graph.to_json_rv(agent_node.get_room().node_id)
        room_logger = RoomInteractionLogger(test_graph, self.data_dir, room_node.node_id)
        room_logger.observe_event(test_event)
        room_logger._end_meta_episode()

        ref_json = test_event.to_json()
        event_file = os.path.join(self.data_dir, 'light_event_dumps/room',f'{room_logger._last_logged_to}_events.json')
        self.assertNotEqual(os.stat(event_file).st_size, 0)
        with open(event_file, 'r') as event_json_file:
            parity = True
            for line in event_json_file:
                if parity:
                    time_stamp = line
                else:
                    written_event = line
                    self.assertEqual(ref_json, written_event)
                parity = not parity

if __name__ == "__main__":
    unittest.main()
