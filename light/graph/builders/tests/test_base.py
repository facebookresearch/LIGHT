# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

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
    DB_TYPE_CHAR,
    DB_TYPE_OBJ,
    DB_STATUS_REJECTED,
    DB_EDGE_IN_CONTAINED,
    DB_EDGE_EX_CONTAINED,
    DB_EDGE_WORN,
    DB_EDGE_WIELDED,
    DB_EDGE_NEIGHBOR,
)
from light.graph.builders.base_elements import (
    DBRoom,
    DBObject,
    DBCharacter,
)


class TestDBGraphBuilder(unittest.TestCase):
    DB_NAME = "test_db.db"

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.data_dir, self.DB_NAME)
        self.ldb = LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME))
        with self.ldb as test:
            rbase_id = test.create_base_room("room")[0]
            self.roomID = test.create_room("room1", rbase_id, "dirty", "old")[0]
            self.roomID2 = test.create_room("room2", rbase_id, "dirty neighbor", "old")[
                0
            ]
            cbase_id = test.create_base_character("troll")[0]
            self.charID = test.create_character(
                "troll under the bridge", cbase_id, "Male", "Tall"
            )[0]
            self.charID2 = test.create_character(
                "troll2 under the bridge", cbase_id, "Female", "Short"
            )[0]
            test.create_node_content(self.roomID, self.charID, DB_EDGE_IN_CONTAINED, 1)
            test.create_node_content(self.roomID, self.charID2, DB_EDGE_EX_CONTAINED, 1)
            self.obase_id = test.create_base_object("room4")[0]
            self.objID = test.create_object(
                "OBJ_1", self.obase_id, 0.4, 0.2, 0, 0, 0, 0, 0, "big"
            )[0]
            self.objID2 = test.create_object(
                "OBJ_2", self.obase_id, 0.2, 0.3, 0, 0, 0, 0, 0, "Small"
            )[0]
            test.create_node_content(self.roomID, self.objID, DB_EDGE_IN_CONTAINED, 1)
            test.create_node_content(
                self.charID, self.objID, DB_EDGE_IN_CONTAINED, 1
            )  # carrying
            test.create_node_content(self.roomID, self.objID2, DB_EDGE_EX_CONTAINED, 1)
            test.create_node_content(
                self.charID, self.objID2, DB_EDGE_WIELDED, 1
            )  # wielded
            test.create_node_content(
                self.charID, self.objID2, DB_EDGE_WORN, 1
            )  # wearing
            test.create_text_edge(self.roomID, "Spear", DB_EDGE_IN_CONTAINED, 1)
            test.create_text_edge(self.charID, "Spear", DB_EDGE_WIELDED, 1)  # wielding
            test.create_text_edge(self.roomID, "Knife", DB_EDGE_EX_CONTAINED, 1)
            test.create_text_edge(self.objID, "Knife", DB_EDGE_IN_CONTAINED, 1)
            test.create_text_edge(self.objID, "Cake", DB_EDGE_IN_CONTAINED, 1)
            test.create_text_edge(
                self.charID, "Knife", DB_EDGE_IN_CONTAINED, 1
            )  # carrying
            test.create_text_edge(self.charID, "Coat", DB_EDGE_WORN, 1)  # wearing
            # object containment:
            test.create_node_content(self.objID, self.objID2, DB_EDGE_IN_CONTAINED, 1)
            test.create_text_edge(
                self.roomID, "Dirty Neighbor", DB_EDGE_NEIGHBOR, 1
            )  # Neighbor
        self.graphBuilder = DBGraphBuilder(self.ldb)

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def test_get_room_from_id(self):
        room = self.graphBuilder.get_room_from_id(self.roomID)
        self.assertEqual(room.description, "dirty")
        self.assertEqual(room.db_id, self.roomID)
        self.assertEqual(room.background, "old")
        self.assertEqual(room.setting, "room1")
        self.assertEqual(room.in_characters["db"][0], self.charID)
        self.assertEqual(room.ex_characters["db"][0], self.charID2)
        self.assertEqual(room.in_objects["db"][0], self.objID)
        self.assertEqual(room.ex_objects["db"][0], self.objID2)
        self.assertEqual(room.in_objects["text"][0], "Spear")
        self.assertEqual(room.ex_objects["text"][0], "Knife")

    def test_get_obj_from_id(self):
        obj = self.graphBuilder.get_obj_from_id(self.objID)
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
                        "description",
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
        self.assertEqual(obj.is_plural, 0)
        self.assertEqual(obj.name, "OBJ_1")
        self.assertEqual(obj.name_prefix, "a")
        self.assertEqual(obj.description, "big")

    def test_get_char_from_id(self):
        char = self.graphBuilder.get_char_from_id(self.charID)
        self.assertEqual(char.is_plural, 0)
        self.assertEqual(char.persona, "Male")
        self.assertEqual(char.name, "troll under the bridge")
        self.assertEqual(char.char_type, "unknown")
        self.assertEqual(char.desc, "Tall")
        self.assertEqual(char.carrying_objects["db"][0], self.objID)
        self.assertEqual(char.wielding_objects["db"][0], self.objID2)
        self.assertEqual(char.wearing_objects["db"][0], self.objID2)
        self.assertEqual(char.carrying_objects["text"][0], "Knife")
        self.assertEqual(char.wielding_objects["text"][0], "Spear")
        self.assertEqual(char.wearing_objects["text"][0], "Coat")
        self.assertEqual(char.base_form, "troll")

    def test_char_deferred_properties(self):
        char1 = self.graphBuilder.get_char_from_id(self.charID)
        room1 = self.graphBuilder.get_room_from_id(self.roomID)
        self.assertIn(self.roomID, char1.in_room_ids)
        self.assertIn(self.charID, room1.in_characters["db"])
        char2 = self.graphBuilder.get_char_from_id(self.charID2)
        self.assertIn(self.roomID, char2.ex_room_ids)
        self.assertIn(self.charID2, room1.ex_characters["db"])

    def test_obj_deferred_properties(self):
        obj1 = self.graphBuilder.get_obj_from_id(self.objID)
        obj2 = self.graphBuilder.get_obj_from_id(self.objID2)
        self.assertNotIn(
            obj2.name, obj1.containing_objs
        )  # SInce containing obj is only text edges atm
        self.assertIn("Knife", obj1.containing_objs)
        self.assertIn("Cake", obj1.containing_objs)

    def test_deferred_room_prop(self):
        room1 = self.graphBuilder.get_room_from_id(self.roomID)
        self.assertIn("Dirty Neighbor", room1.neighbors)

    def test_cached_db_objects(self):
        roomDB = DBRoom(self.ldb, self.roomID)
        charDB = DBCharacter(self.ldb, self.charID)
        objDB = DBObject(self.ldb, self.objID)
        with self.ldb as test:
            cache = test.cache
        roomCache = DBRoom(self.ldb, self.roomID, cache)
        charCache = DBCharacter(self.ldb, self.charID, cache)
        objCache = DBObject(self.ldb, self.objID, cache)
        roomCache.get_text_edges(DB_EDGE_NEIGHBOR)
        self.assertEqual(roomDB.setting, roomCache.setting)
        self.assertEqual(roomDB.category, roomCache.category)
        self.assertEqual(roomDB.in_characters, roomCache.in_characters)
        self.assertEqual(roomDB.neighbors, roomCache.neighbors)
        self.assertEqual(roomDB.data_split, roomCache.data_split)
        self.assertEqual(charDB.data_split, charCache.data_split)
        self.assertEqual(objDB.data_split, objCache.data_split)
        self.assertEqual(roomDB.ex_objects, roomCache.ex_objects)
        self.assertEqual(roomDB.ex_characters, roomCache.ex_characters)
        self.assertEqual(roomDB.in_objects, roomCache.in_objects)
        self.assertEqual(roomDB.in_characters, roomCache.in_characters)
        self.assertEqual(objDB.in_room_ids, objDB.in_room_ids)
        self.assertEqual(objDB.ex_room_ids, objDB.ex_room_ids)
        self.assertEqual(charDB.in_room_ids, charDB.in_room_ids)
        self.assertEqual(charDB.ex_room_ids, charDB.ex_room_ids)
        self.assertEqual(charDB.carrying_objects, charCache.carrying_objects)
        self.assertEqual(charDB.wearing_objects, charCache.wearing_objects)
        self.assertEqual(charDB.wielding_objects, charCache.wielding_objects)
        self.assertEqual(charDB.base_form, charCache.base_form)
        self.assertEqual(objDB.base_form, objCache.base_form)
        self.assertEqual(objDB.contained_by, objCache.contained_by)
        self.assertEqual(objDB.containing_objs, objCache.containing_objs)


if __name__ == "__main__":
    unittest.main()
