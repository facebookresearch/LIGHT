#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil, tempfile
import sqlite3
import os
import pickle

from parlai_internal.projects.light.v1.graph_builders.base import DBGraphBuilder
from parlai_internal.projects.light.v1.data_model.light_database import (
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
from parlai_internal.projects.light.v1.graph_builders.base_elements import (
    DBRoom,
    DBObject,
    DBCharacter,
)


class TestDBGraphBuilder(unittest.TestCase):
    DB_NAME = "test_db.db"

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.data_dir, self.DB_NAME)
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
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
                'OBJ_1', self.obase_id, 0.4, 0.2, 0, 0, 0, 0, 0, "big"
            )[0]
            self.objID2 = test.create_object(
                'OBJ_2', self.obase_id, 0.2, 0.3, 0, 0, 0, 0, 0, "Small"
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
        self.graphBuilder = DBGraphBuilder(os.path.join(self.data_dir, self.DB_NAME))

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def test_get_room_from_id(self):
        room = self.graphBuilder.get_room_from_id(self.roomID)
        self.assertEqual(room.description, 'dirty')
        self.assertEqual(room.db_id, self.roomID)
        self.assertEqual(room.background, 'old')
        self.assertEqual(room.setting, 'room1')
        self.assertEqual(room.in_characters['db'][0], self.charID)
        self.assertEqual(room.ex_characters['db'][0], self.charID2)
        self.assertEqual(room.in_objects['db'][0], self.objID)
        self.assertEqual(room.ex_objects['db'][0], self.objID2)
        self.assertEqual(room.in_objects['text'][0], "Spear")
        self.assertEqual(room.ex_objects['text'][0], "Knife")