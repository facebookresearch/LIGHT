#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil, tempfile

from light.data_model.db.environment import EnvDB, DBEdgeType
from light.data_model.db.base import LightLocalDBConfig
from light.graph.builders.base import DBGraphBuilder, GraphBuilderConfig


class TestDBGraphBuilder(unittest.TestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        db_config = LightLocalDBConfig(file_root=self.data_dir)
        builder_conf = GraphBuilderConfig()

        self.env_db = EnvDB(db_config)
        self.roomID = self.env_db.create_room_entry("room1", "room", "dirty", "old")
        self.roomID2 = self.env_db.create_room_entry(
            "room2", "room", "dirty neighbor", "old"
        )
        self.charID = self.env_db.create_agent_entry(
            "troll under the bridge", "troll", "Male", "Tall"
        )
        self.charID2 = self.env_db.create_agent_entry(
            "troll2 under the bridge", "troll", "Female", "Short"
        )
        self.env_db.create_edge(self.roomID, self.charID, DBEdgeType.CONTAINS)
        self.env_db.create_edge(self.roomID, self.charID2, DBEdgeType.MAY_CONTAIN)
        self.objID = self.env_db.create_object_entry(
            "OBJ_1",
            "obj",
            "big",
            0.4,
            0.2,
            0,
            0,
            0,
            0,
            0,
        )
        self.objID2 = self.env_db.create_object_entry(
            "OBJ_2",
            "obj",
            "Small",
            0.2,
            0.3,
            0,
            0,
            0,
            0,
            0,
        )
        self.env_db.create_edge(self.roomID, self.objID, DBEdgeType.CONTAINS)
        self.env_db.create_edge(
            self.charID, self.objID, DBEdgeType.CONTAINS
        )  # carrying
        self.env_db.create_edge(self.roomID, self.objID2, DBEdgeType.MAY_CONTAIN)
        self.env_db.create_edge(
            self.charID, self.objID2, DBEdgeType.WIELDING
        )  # wielded
        self.env_db.create_text_edge(self.roomID, "Spear", DBEdgeType.CONTAINS)
        self.env_db.create_text_edge(
            self.charID, "Spear", DBEdgeType.WIELDING
        )  # wielding
        self.env_db.create_text_edge(self.roomID, "Knife", DBEdgeType.MAY_CONTAIN)
        self.env_db.create_text_edge(self.objID, "Knife", DBEdgeType.CONTAINS)
        self.env_db.create_text_edge(self.objID, "Cake", DBEdgeType.CONTAINS)
        self.env_db.create_text_edge(
            self.charID, "Knife", DBEdgeType.CONTAINS
        )  # carrying
        self.env_db.create_text_edge(self.charID, "Coat", DBEdgeType.WEARING)  # wearing
        # object containment:
        self.env_db.create_edge(self.objID, self.objID2, DBEdgeType.CONTAINS)
        self.env_db.create_text_edge(
            self.roomID, "Dirty Neighbor", DBEdgeType.NEIGHBOR
        )  # Neighbor
        self.graphBuilder = DBGraphBuilder(
            builder_conf, self.env_db, allow_blocked=True
        )

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def test_get_room_from_id(self):
        room = self.graphBuilder.get_room_from_id(self.roomID)
        assert room is not None
        self.assertEqual(room.description, "dirty")
        self.assertEqual(room.db_id, self.roomID)
        self.assertEqual(room.backstory, "old")
        self.assertEqual(room.name, "room1")
        edges = room.node_edges
        edge_map = {e.child_id: e.edge_type for e in edges}
        self.assertEqual(edge_map[self.charID], DBEdgeType.CONTAINS)
        self.assertEqual(edge_map[self.charID2], DBEdgeType.MAY_CONTAIN)
        self.assertEqual(edge_map[self.objID], DBEdgeType.CONTAINS)
        self.assertEqual(edge_map[self.objID2], DBEdgeType.MAY_CONTAIN)

        text_edges = room.text_edges
        text_edge_map = {e.child_text: e.edge_type for e in text_edges}
        self.assertEqual(text_edge_map.get("Spear"), DBEdgeType.CONTAINS, text_edge_map)
        self.assertEqual(
            text_edge_map.get("Knife"), DBEdgeType.MAY_CONTAIN, text_edge_map
        )

    def test_get_obj_from_id(self):
        obj = self.graphBuilder.get_obj_from_id(self.objID)
        self.assertIsNotNone(obj)
        assert obj is not None
        self.assertTrue(
            set.issubset(
                set(
                    [
                        "is_gettable",
                        "is_wearable",
                        "is_weapon",
                        "is_food",
                        "is_drink",
                        "is_container",
                        "is_surface",
                        "physical_description",
                        "name",
                        "name_prefix",
                        "is_plural",
                    ]
                ),
                set(vars(obj).keys()),
            )
        )
        self.assertEqual(obj.is_container, 0.4)
        self.assertEqual(obj.is_drink, 0.2)
        self.assertEqual(obj.is_food, 0)
        self.assertEqual(obj.is_weapon, 0)
        self.assertEqual(obj.is_surface, 0)
        self.assertIsNone(obj.is_plural)
        self.assertEqual(obj.name, "OBJ_1")
        self.assertEqual(obj.name_prefix, "a")
        self.assertEqual(obj.physical_description, "big")

    def test_get_char_from_id(self):
        char = self.graphBuilder.get_char_from_id(self.charID)
        assert char is not None
        self.assertIsNone(char.is_plural, None)
        self.assertEqual(char.persona, "Male")
        self.assertEqual(char.name, "troll under the bridge")
        self.assertEqual(char.physical_description, "Tall")

        edges = char.node_edges
        edge_map = {e.child_id: e.edge_type for e in edges}
        self.assertEqual(edge_map[self.objID], DBEdgeType.CONTAINS)
        self.assertEqual(edge_map[self.objID2], DBEdgeType.WIELDING)

        text_edges = char.text_edges
        text_edge_map = {e.child_text: e.edge_type for e in text_edges}
        self.assertEqual(text_edge_map["Knife"], DBEdgeType.CONTAINS, text_edge_map)
        self.assertEqual(text_edge_map["Spear"], DBEdgeType.WIELDING, text_edge_map)
        self.assertEqual(text_edge_map["Coat"], DBEdgeType.WEARING, text_edge_map)

    def test_deferred_room_prop(self):
        room1 = self.graphBuilder.get_room_from_id(self.roomID)
        assert room1 is not None
        edges = room1.text_edges
        self.assertIn("Dirty Neighbor", [e.child_text for e in edges])


if __name__ == "__main__":
    unittest.main()
