#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil, tempfile
import sqlite3
import os
import pickle

from light.graph.builders.base import DBGraphBuilder
from light.data_model.light_database import (
    LIGHTDatabase,
    DB_TYPE_ROOM,
    DB_TYPE_BASE_ROOM,
    DB_TYPE_CHAR,
    DB_TYPE_OBJ,
    DB_STATUS_REJECTED,
    DB_EDGE_IN_CONTAINED,
    DB_EDGE_EX_CONTAINED,
    DB_EDGE_WORN,
    DB_EDGE_WIELDED,
    DB_STATUS_PROD,
)
from light.graph.builders.db_utils import assign_datasplit


class TestDBGraphBuilder(unittest.TestCase):
    DB_NAME = "test_db.db"
    EMPTY_DB = "empty.db"

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        empty = LIGHTDatabase(os.path.join(self.data_dir, self.EMPTY_DB))
        self.ldb = LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME))
        with self.ldb as test:
            # Create Base Rooms
            self.rbase_id = test.create_base_room("broom1")[0]
            self.rbase_id2 = test.create_base_room("broom2")[0]
            self.rbase_id3 = test.create_base_room("broom3")[0]
            rbase_id_rejected = test.create_base_room(
                "rejected_broom", entry_attributes={"status": DB_STATUS_REJECTED}
            )[0]

            # Create Rooms
            self.roomID = test.create_room("room1", self.rbase_id, "dirty", "old")[0]
            self.roomID2 = test.create_room("room2", self.rbase_id2, "clean", "new")[0]
            self.roomID3 = test.create_room(
                "room3",
                self.rbase_id3,
                "neutral",
                "no history",
                {"status": DB_STATUS_REJECTED},
            )[0]

            # Create Characters
            cbase_id = test.create_base_character("troll")[0]
            cbase_id2 = test.create_base_character(
                name="troll", entry_attributes={"status": DB_STATUS_REJECTED}
            )[0]

            self.charID = test.create_character(
                "troll under the bridge", cbase_id, "Male", "Tall"
            )[0]
            self.charID2 = test.create_character(
                "troll2 under the bridge", cbase_id, "Female", "Short"
            )[0]
            self.charID3 = test.create_character(
                "troll3 rejected",
                cbase_id2,
                "Child",
                "Short",
                entry_attributes={"status": DB_STATUS_REJECTED},
            )[0]

            # Create Objects
            self.obase_id = test.create_base_object("baseobj")[0]
            self.objID = test.create_object(
                "OBJ_1", self.obase_id, 0.4, 0.2, 0, 0, 0, 0, 0, "big"
            )[0]
            self.objID2 = test.create_object(
                "OBJ_2", self.obase_id, 0.2, 0.3, 0, 0, 0, 0, 0, "Small"
            )[0]
            self.objID3 = test.create_object(
                "OBJ_3",
                self.obase_id,
                0.2,
                0.3,
                0,
                0,
                0,
                0,
                0,
                "Small",
                {"status": DB_STATUS_REJECTED},
            )[0]

            # Create Text Edges
            test.create_text_edge(self.roomID, "Knife", DB_EDGE_EX_CONTAINED, 1)
            test.create_text_edge(self.roomID, "Cake", DB_EDGE_IN_CONTAINED, 1)
            test.create_text_edge(
                self.roomID,
                "Rejected",
                DB_EDGE_IN_CONTAINED,
                1,
                {"status": DB_STATUS_REJECTED},
            )

            # Create DB Edges
            test.create_node_content(self.roomID, self.charID, DB_EDGE_IN_CONTAINED, 1)
            test.create_node_content(self.roomID, self.charID2, DB_EDGE_EX_CONTAINED, 1)
            test.create_node_content(
                self.roomID2,
                self.charID3,
                DB_EDGE_EX_CONTAINED,
                1,
                {"status": DB_STATUS_REJECTED},
            )

        self.graphBuilder = DBGraphBuilder(self.ldb)
        self.graphBuilderEmpty = DBGraphBuilder(empty)

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def test_get_random_room(self):
        self.assertIsNone(self.graphBuilderEmpty.get_random_room())
        self.assertNotEqual(
            self.graphBuilder.get_random_room().db_id, self.roomID3
        )  # roomID3 is id of an rejected room
        self.assertIn(
            self.graphBuilder.get_random_room().db_id, [self.roomID, self.roomID2]
        )

    def test_get_random_char(self):
        self.assertIsNone(self.graphBuilderEmpty.get_random_char())
        self.assertNotEqual(
            self.graphBuilder.get_random_char().name, "troll3 rejected"
        )  # troll3 is rejected char
        self.assertIn(
            self.graphBuilder.get_random_char().name,
            ["troll under the bridge", "troll2 under the bridge"],
        )

    def test_get_random_obj(self):
        self.assertIsNone(self.graphBuilderEmpty.get_random_obj())
        self.assertNotEqual(
            self.graphBuilder.get_random_obj().name, "OBJ_3"
        )  # roomID3 is id of an rejected room
        self.assertIn(self.graphBuilder.get_random_obj().name, ["OBJ_1", "OBJ_2"])

    def test_get_room_categories(self):
        self.assertEqual(self.graphBuilderEmpty.get_room_categories(), [])
        self.assertNotIn(
            "rejected_broom", self.graphBuilder.get_room_categories()
        )  # test if rejected baseroom is in the list
        self.assertEqual(
            self.graphBuilder.get_room_categories(), ["broom1", "broom2", "broom3"]
        )

    def test_get_text_edges(self):
        test_room = self.graphBuilder.get_room_from_id(self.roomID)
        self.assertNotIn("Cake", test_room.get_text_edges(DB_EDGE_EX_CONTAINED))
        self.assertEqual(
            test_room.get_text_edges(),
            ["Knife", "Cake"],
            "Should only return non rejected edges",
        )
        self.assertEqual(test_room.get_text_edges(DB_EDGE_EX_CONTAINED), ["Knife"])

    def test_get_db_edges(self):
        test_room = self.graphBuilder.get_room_from_id(self.roomID)
        self.assertNotIn(self.charID2, test_room.get_db_edges(DB_EDGE_IN_CONTAINED))
        self.assertEqual(test_room.get_db_edges(), [self.charID, self.charID2])
        self.assertEqual(test_room.get_db_edges(DB_EDGE_IN_CONTAINED), [self.charID])

    def test_update_split(self):
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            obj_ids = {
                o["id"]: test.get_id(o["id"])[0]["split"] for o in test.get_object()
            }
            for o in test.get_object():
                test.update_split(o["id"], "val")
            splits = [test.get_id(o["id"])[0]["split"] for o in test.get_object()]
            self.assertEqual(set(splits), set(["val"]))

    def test_datasplit(self):
        test_room = self.graphBuilder.get_room_from_id(self.roomID)
        self.assertIsNotNone(test_room.data_split)
        self.assertIn(test_room.data_split, ["test", "train", "val"])

    def test_assign_datasplit(self):
        # Test on Base Room as they do not get an automatic assignment
        db_path = os.path.join(self.data_dir, self.DB_NAME)
        with LIGHTDatabase(db_path) as ldb:
            entries = ldb.get_id(type=DB_TYPE_BASE_ROOM)
        pre_assigned = [e["split"] for e in entries]
        for e in pre_assigned:
            self.assertIsNone(e)

        assign_datasplit(db_path, DB_TYPE_BASE_ROOM)
        with LIGHTDatabase(db_path) as ldb:
            entries = ldb.get_id(type=DB_TYPE_BASE_ROOM)
        assigned = [e["split"] for e in entries]
        for e in assigned:
            self.assertIsNotNone(e)
            self.assertIn(e, ["test", "train", "val"])

    def test_data_split_at_creation(self):
        db_path = os.path.join(self.data_dir, self.DB_NAME)
        with LIGHTDatabase(db_path) as ldb:
            room_id, _ = ldb.create_room(
                "tempt room",
                self.rbase_id,
                "temp room to test datasplit",
                "does it have a datasplit",
                entry_attributes={"is_from_pickle": False, "status": DB_STATUS_PROD},
            )
            self.assertIn(ldb.get_id(id=room_id)[0]["split"], ["test", "train", "val"])


if __name__ == "__main__":
    unittest.main()
