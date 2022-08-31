#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil, tempfile
import sqlite3
import os
import pickle
import random

from light.graph.builders.base import DBGraphBuilder
from light.graph.builders.user_world_builder import UserWorldBuilder
from light.data_model.light_database import (
    LIGHTDatabase,
    DB_TYPE_ROOM,
    DB_TYPE_CHAR,
    DB_TYPE_OBJ,
    DB_STATUS_REJECTED,
    DB_EDGE_IN_CONTAINED,
    DB_EDGE_EX_CONTAINED,
    DB_EDGE_WORN,
    DB_EDGE_WIELDED,
    DB_EDGE_NEIGHBOR,
)
from parlai.core.params import ParlaiParser
from light.graph.structured_graph import OOGraph


class TestWorldGraphBuilder(unittest.TestCase):
    DB_NAME = "test_db.db"

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        # Random seed for right random char
        random.seed(2)
        self.db_path = os.path.join(self.data_dir, self.DB_NAME)
        opt = {
            "light_db_file": self.db_path,
            "filler_probability": 0.05,
            "use_npc_models": True,
        }
        self.ldb = LIGHTDatabase(self.db_path)
        with self.ldb as test:
            self.player_id = test.create_user("test")[0]
            self.world_id = test.create_world("swamp", self.player_id, 3, 3, 1)[0]
            rbase_id = test.create_base_room("room")[0]
            self.roomID = test.create_room("room1", rbase_id, "dirty", "old")[0]
            self.roomID2 = test.create_room("room2", rbase_id, "dirty neighbor", "old")[
                0
            ]
            cbase_id = test.create_base_character("troll")[0]
            self.charID = test.create_character(
                "troll under the bridge",
                cbase_id,
                "Male",
                "Tall",
            )[0]
            self.charID2 = test.create_character(
                "troll under the bridge2", cbase_id, "Female", "Short"
            )[0]
            self.charID3 = test.create_character(
                "troll under the bridge3",
                cbase_id,
                "Male",
                "Tall",
            )[0]
            self.obase_id = test.create_base_object("room4")[0]
            self.objID = test.create_object(
                "OBJ_1", self.obase_id, 0.4, 0.2, 0, 0, 0, 0, 0, "big"
            )[0]
            self.objID2 = test.create_object(
                "OBJ_2", self.obase_id, 0.2, 0.3, 0, 0, 0, 0, 0, "Small"
            )[0]

            rnode_id1 = test.create_graph_node(self.world_id, self.roomID)[0]
            rnode_id2 = test.create_graph_node(self.world_id, self.roomID2)[0]
            cnode_id1 = test.create_graph_node(self.world_id, self.charID)[0]
            cnode_id2 = test.create_graph_node(self.world_id, self.charID2)[0]
            onode_id1 = test.create_graph_node(self.world_id, self.objID)[0]
            onode_id2 = test.create_graph_node(self.world_id, self.objID2)[0]

            tile_id1 = test.create_tile(self.world_id, rnode_id1, "#FFFFF", 1, 1, 0)[0]
            tile_id2 = test.create_tile(self.world_id, rnode_id2, "#FFFFF", 1, 2, 0)[0]
            edge1 = test.create_graph_edge(
                self.world_id, rnode_id1, rnode_id2, "neighbors to the north"
            )[0]
            edge2 = test.create_graph_edge(
                self.world_id, rnode_id1, cnode_id1, "contains"
            )[0]
            edge3 = test.create_graph_edge(
                self.world_id, rnode_id1, onode_id1, "contains"
            )[0]
            edge3 = test.create_graph_edge(
                self.world_id, rnode_id2, cnode_id2, "contains"
            )[0]
            edge4 = test.create_graph_edge(
                self.world_id, rnode_id2, onode_id2, "contains"
            )[0]

        self.graphBuilder = UserWorldBuilder(
            self.ldb, self.world_id, self.player_id, True, opt
        )
        self.testGraph, self.testWorld = self.graphBuilder.get_graph()

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def test_builder_adds_random_agent_to_graph_adds_another_to_some_room(self):
        """
        Test that the add_random_new_agent_to_graph method will add new agents
        """
        dbid_to_g = {val: key for key, val in self.graphBuilder.roomid_to_db.items()}
        gRoomId = dbid_to_g[self.roomID]
        gRoomId2 = dbid_to_g[self.roomID2]
        self.graphBuilder.add_random_new_agent_to_graph(self.testWorld)
        self.assertEqual(len(self.testGraph.agents), 3)
        contained_room_1 = len(self.testGraph.get_node(gRoomId).contained_nodes)
        contained_room_2 = len(self.testGraph.get_node(gRoomId2).contained_nodes)
        self.assertTrue(contained_room_1 == 3 or contained_room_2 == 3)

    def test_builder_returns_graph(self):
        self.assertIsInstance(self.testGraph, OOGraph)

    def test_builder_graph_valid(self):
        self.testGraph.assert_valid()

    def test_graph_contains_room(self):
        self.assertTrue(bool(self.testGraph.rooms))

    def test_graph_contains_character(self):
        self.assertTrue(bool(self.testGraph.agents))

    def test_graph_contains_object(self):
        self.assertTrue(bool(self.testGraph.objects))

    def test_builder_get_graph(self):
        # Check entities - should be 6 nodes
        self.assertEqual(len(self.testGraph.get_all_ids()), 6)
        # Should have two rooms, two agents, two objects:
        self.assertEqual(len(self.testGraph.rooms), 2)
        self.assertEqual(len(self.testGraph.objects), 2)
        self.assertEqual(len(self.testGraph.agents), 2)

        # Check the DB_IDs
        self.assertTrue(self.roomID in self.graphBuilder.roomid_to_db.values())
        self.assertTrue(self.roomID2 in self.graphBuilder.roomid_to_db.values())

        dbid_to_g = {val: key for key, val in self.graphBuilder.roomid_to_db.items()}
        # Get the graph node for the rooms:
        gRoomId = dbid_to_g[self.roomID]
        gRoomId2 = dbid_to_g[self.roomID2]

        # Now check edges:
        edge1 = self.testGraph.get_edge(gRoomId, gRoomId2)
        self.assertEqual(edge1.label, "a path to the north")
        edge2 = self.testGraph.get_edge(gRoomId2, gRoomId)
        self.assertEqual(edge2.label, "a path to the south")

        for node in self.testGraph.get_all_nodes():
            if node.room:
                # all good, nothing to do here
                pass
            elif node.name.endswith("2"):
                self.assertEqual(node.get_container().node_id, gRoomId2)
            else:
                self.assertEqual(node.get_container().node_id, gRoomId)

        # Finally check no extra added - that is, rooms contain no other objects, and
        # have no other neighbors
        self.assertEqual(len(self.testGraph.get_node(gRoomId).contained_nodes), 2)
        self.assertEqual(len(self.testGraph.get_node(gRoomId2).contained_nodes), 2)
        self.assertEqual(len(self.testGraph.get_node(gRoomId).get_neighbors()), 1)
        self.assertEqual(len(self.testGraph.get_node(gRoomId2).get_neighbors()), 1)


if __name__ == "__main__":
    unittest.main()
