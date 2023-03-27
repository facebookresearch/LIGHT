#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil, tempfile
import os

from light.data_model.db.environment import EnvDB, DBEdgeType
from light.data_model.db.base import LightLocalDBConfig
from light.graph.builders.base import DBGraphBuilder, GraphBuilderConfig


class TestDBGraphBuilder(unittest.TestCase):
    DB_NAME = "test_db.db"
    EMPTY_DB = "empty.db"

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.empty_dir = os.path.join(self.data_dir, "empty")
        self.full_dir = os.path.join(self.data_dir, "full")
        os.makedirs(self.empty_dir, exist_ok=True)
        os.makedirs(self.full_dir, exist_ok=True)
        db_config_empty = LightLocalDBConfig(file_root=self.empty_dir)
        db_config_full = LightLocalDBConfig(file_root=self.full_dir)
        builder_conf = GraphBuilderConfig()

        self.env_db = EnvDB(db_config_full)
        self.empty_db = EnvDB(db_config_empty)

        # Create Base Rooms
        self.rbase_id = self.env_db.create_room_name("broom1")
        self.rbase_id2 = self.env_db.create_room_name("broom2")
        self.rbase_id3 = self.env_db.create_room_name("broom3")

        # Create Rooms
        self.roomID = self.env_db.create_room_entry("room1", "broom1", "dirty", "old")
        self.roomID2 = self.env_db.create_room_entry("room2", "broom2", "clean", "new")

        # Create Characters
        self.charID = self.env_db.create_agent_entry(
            "troll under the bridge", "troll", "Male", "Tall"
        )
        self.charID2 = self.env_db.create_agent_entry(
            "troll2 under the bridge", "troll", "Female", "Short"
        )

        # Create Objects
        self.obase_id = self.env_db.create_object_name("baseobj")[0]
        self.objID = self.env_db.create_object_entry(
            "OBJ_1", "baseobj", "big", 0.4, 0.2, 0, 0, 0, 0, 0
        )
        self.objID2 = self.env_db.create_object_entry(
            "OBJ_2", "baseobj", "Small", 0.2, 0.3, 0, 0, 0, 0, 0
        )

        # Create Text Edges
        self.env_db.create_text_edge(self.roomID, "Knife", DBEdgeType.MAY_CONTAIN)
        self.env_db.create_text_edge(self.roomID, "Cake", DBEdgeType.CONTAINS)

        # Create DB Edges
        self.env_db.create_edge(self.roomID, self.charID, DBEdgeType.CONTAINS)
        self.env_db.create_edge(self.roomID, self.charID2, DBEdgeType.MAY_CONTAIN)

        self.graphBuilder = DBGraphBuilder(
            builder_conf, self.env_db, allow_blocked=True
        )
        self.graphBuilderEmpty = DBGraphBuilder(builder_conf, self.empty_db)

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def test_get_random_room(self):
        self.assertIsNone(self.graphBuilderEmpty.get_random_room())
        room = self.graphBuilder.get_random_room()
        assert room is not None
        self.assertIn(room.db_id, [self.roomID, self.roomID2])

    def test_get_random_char(self):
        self.assertIsNone(self.graphBuilderEmpty.get_random_char())
        char = self.graphBuilder.get_random_char()
        assert char is not None
        self.assertIn(
            char.name,
            ["troll under the bridge", "troll2 under the bridge"],
        )

    def test_get_random_obj(self):
        self.assertIsNone(self.graphBuilderEmpty.get_random_obj())
        obj = self.graphBuilder.get_random_obj()
        assert obj is not None
        self.assertIn(obj.name, ["OBJ_1", "OBJ_2"])

    def test_get_room_categories(self):
        self.assertEqual(self.graphBuilderEmpty.get_room_categories(), [])
        self.assertEqual(
            self.graphBuilder.get_room_categories(), ["broom1", "broom2", "broom3"]
        )

    def test_get_text_edges(self):
        test_room = self.graphBuilder.get_room_from_id(self.roomID)
        assert test_room is not None
        self.assertEqual(len(test_room.text_edges), 2)


if __name__ == "__main__":
    unittest.main()
