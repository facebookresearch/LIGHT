#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.abs

import unittest

from light.graph.elements.graph_nodes import GraphAgent
from light.graph.structured_graph import OOGraph
from light.world.world import World
from light.graph.events.graph_events import EmoteEvent
from light.world.souls.test_soul import TestSoul

class TestGraphNodes(unittest.TestCase):
    """Unit tests for simple souls"""

    def test_init_soul(self):
        '''Ensure that souls can be created'''
        test_graph = OOGraph()
        agent_node = test_graph.add_agent("My test agent", {})
        room_node = test_graph.add_room("test room", {})
        agent_node.force_move_to(room_node)
        test_world = World({}, None, True)
        test_world.oo_graph = test_graph
        test_soul = TestSoul(agent_node, test_world)
        self.assertEqual(agent_node, test_soul.target_node)
        self.assertEqual(test_world, test_soul.world)

        test_event = EmoteEvent.construct_from_args(agent_node, targets=[], text="smile")
        test_soul.do_act(test_event)

        test_soul.reap()
       
    # TODO add interactions over the world when the world->soul flow
    # is properly written.



if __name__ == '__main__':
    unittest.main()
