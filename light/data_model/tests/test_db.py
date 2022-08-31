#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.abs

import shutil, tempfile
import sqlite3
import unittest
import time
import json
import os
import pickle

from light.data_model.light_database import (
    LIGHTDatabase,
    DB_EDGE_IN_CONTAINED,
    DB_EDGE_EX_CONTAINED,
    DB_EDGE_WORN,
    DB_EDGE_WIELDED,
    DB_EDGE_NEIGHBOR,
    EDGE_TYPES,
    DB_TYPE_BASE_CHAR,
    DB_TYPE_CHAR,
    DB_TYPE_BASE_OBJ,
    DB_TYPE_OBJ,
    DB_TYPE_BASE_ROOM,
    DB_TYPE_ROOM,
    DB_TYPE_EDGE,
    DB_TYPE_TEXT_EDGE,
    DB_TYPE_INTERACTION,
    DB_TYPE_UTTERANCE,
    DB_TYPE_PARTICIPANT,
    DB_TYPE_TURN,
    DB_TYPE_PLAYER,
    DB_TYPE_WORLD,
    ENTITY_TYPES,
    DB_STATUS_PROD,
    DB_STATUS_REVIEW,
    DB_STATUS_REJECTED,
    DB_STATUS_QUESTIONABLE,
    DB_STATUS_ACCEPTED,
    DB_STATUS_ACCEPT_ONE,
    DB_STATUS_ACCEPT_ALL,
    CONTENT_STATUSES,
    EDIT_STATUSES,
)


class TestDatabase(unittest.TestCase):
    """Various unit tests for the SQLite database"""

    DB_NAME = "test_db.db"

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def assert_sqlite_row_equal(self, expected_dict, sqlite_row, msg=None):
        """Ensure that everything in the expected dict was set in the given row"""
        for key, value in expected_dict.items():
            self.assertEqual(value, sqlite_row[key], msg)

    def assert_sqlite_rows_equal(self, expected_dicts, sqlite_rows, msg=None):
        """Ensure that everything in the given dicts was correct in the given rows"""
        for x in range(len(sqlite_rows)):
            self.assert_sqlite_row_equal(expected_dicts[x], sqlite_rows[x], msg)

    def test_column_names(self):
        """Test that column name and type can be retrieved for a specific table"""
        # base room
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            self.assertEqual(
                test.get_columns(DB_TYPE_BASE_ROOM), {"id": "integer", "name": "text"}
            )
        # room
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            self.assertEqual(
                test.get_columns(DB_TYPE_ROOM),
                {
                    "id": "integer",
                    "name": "text",
                    "base_id": "integer",
                    "description": "text",
                    "backstory": "text",
                },
            )
        # raise exception when type is invalid
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                test.get_columns("invalid_type")

    def test_create_entries(self):
        # Test if base room can be successfully created
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            rbase_id = test.create_base_room("room")[0]
            self.assert_sqlite_row_equal(
                {"id": rbase_id, "name": "room"},
                test.get_base_room()[0],
                "Base room cannot be created",
            )

        # Test if room can be successfully created and inherit base room
        # name when name is null
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            rcontent_id1 = test.create_room("room1", rbase_id, "dirty", "old")[0]
            self.assert_sqlite_row_equal(
                {
                    "id": rcontent_id1,
                    "name": "room1",
                    "base_id": rbase_id,
                    "description": "dirty",
                    "backstory": "old",
                },
                test.get_room()[0],
                "Room cannot be created",
            )
            rcontent_id2 = test.create_room(None, rbase_id, "dirty", "old")[0]
            self.assert_sqlite_row_equal(
                {
                    "id": rcontent_id2,
                    "name": "room",
                    "base_id": rbase_id,
                    "description": "dirty",
                    "backstory": "old",
                },
                test.get_room(id=rcontent_id2)[0],
                "Room cannot inherit base room name extended name is not given",
            )

        # Test if base character can be successfully created
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            cbase_id = test.create_base_character("troll")[0]
            self.assert_sqlite_row_equal(
                {"id": cbase_id, "name": "troll"},
                test.get_base_character()[0],
                "Base character cannot be created",
            )

        # Test if character can be successfully created
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            ccontent_id1 = test.create_character(
                "troll under the bridge", cbase_id, "Male", "Tall"
            )[0]
            self.assert_sqlite_row_equal(
                {
                    "id": ccontent_id1,
                    "name": "troll under the bridge",
                    "base_id": cbase_id,
                    "persona": "Male",
                    "physical_description": "Tall",
                },
                test.get_character()[0],
                "Character cannot be created",
            )

        # Test if base object can be successfully created
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            obase_id = test.create_base_object("room4")[0]
            self.assert_sqlite_row_equal(
                {"id": obase_id, "name": "room4"},
                test.get_base_object()[0],
                "Base object cannot be created",
            )

        # Test if object can be successfully created (Without custom tag attributes)
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            ocontent_id1 = test.create_object(
                None, obase_id, 0.4, 0.2, 0, 0, 0, 0, 0, "big", {}, None, None
            )[0]
            self.assert_sqlite_row_equal(
                {
                    "id": ocontent_id1,
                    "name": "room4",
                    "base_id": obase_id,
                    "is_container": 0.4,
                    "is_drink": 0.2,
                    "is_food": 0,
                    "is_gettable": 0,
                    "is_surface": 0,
                    "is_wearable": 0,
                    "is_weapon": 0,
                    "physical_description": "big",
                },
                test.get_object()[0],
                "Object cannot be created",
            )

        # Test if object can be successfully created (With custom tag attributes)
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            obase_id2 = test.create_base_object("room334")[0]
            ocontent_id2 = test.create_object(
                None,
                obase_id2,
                0.4,
                0.2,
                0,
                0,
                0,
                0,
                0,
                "big",
                {},
                None,
                None,
                5,
                3,
                "round",
                1,
            )[0]
            self.assert_sqlite_row_equal(
                {
                    "id": ocontent_id2,
                    "name": "room334",
                    "base_id": obase_id2,
                    "is_container": 0.4,
                    "is_drink": 0.2,
                    "is_food": 0,
                    "is_gettable": 0,
                    "is_surface": 0,
                    "is_wearable": 0,
                    "is_weapon": 0,
                    "physical_description": "big",
                    "size": 5,
                    "contain_size": 3,
                    "shape": "round",
                    "value": 1,
                },
                test.get_object(base_id=obase_id2)[0],
                "Object cannot be created",
            )

        # Test if node content (edge) can be successfully created
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            check_id = test.create_node_content(
                rcontent_id1, ccontent_id1, DB_EDGE_EX_CONTAINED, 0
            )[0]
            self.assert_sqlite_row_equal(
                {
                    "id": check_id,
                    "parent_id": rcontent_id1,
                    "child_id": ccontent_id1,
                    "edge_type": DB_EDGE_EX_CONTAINED,
                    "edge_strength": 0,
                },
                test.get_node_content()[0],
                "Node content (edge) cannot be created for ex_contained",
            )

        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            check_id = test.create_node_content(
                rcontent_id1, ccontent_id1, DB_EDGE_IN_CONTAINED, 1
            )[0]
            self.assert_sqlite_row_equal(
                {
                    "id": check_id,
                    "parent_id": rcontent_id1,
                    "child_id": ccontent_id1,
                    "edge_type": DB_EDGE_IN_CONTAINED,
                    "edge_strength": 1,
                },
                test.get_node_content(edge_strength=1)[0],
                "Node content (edge) cannot be created for in_contained",
            )

        # Test if text edge can be successfully created
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            check_id = test.create_text_edge(
                rcontent_id1, "Spear", DB_EDGE_NEIGHBOR, 1
            )[0]
            self.assert_sqlite_row_equal(
                {
                    "id": check_id,
                    "parent_id": rcontent_id1,
                    "child_text": "Spear",
                    "edge_type": DB_EDGE_NEIGHBOR,
                    "edge_strength": 1,
                },
                test.get_text_edge(child_text="Spear")[0],
                "Neighbor Text edge cannot be created",
            )

        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            check_id = test.create_text_edge(
                rcontent_id2,
                "The Abyss",
                DB_EDGE_NEIGHBOR,
                1,
                child_desc="Falling into the endless crater",
                child_label="down",
            )[0]
            self.assert_sqlite_row_equal(
                {
                    "id": check_id,
                    "parent_id": rcontent_id2,
                    "child_text": "The Abyss",
                    "edge_type": DB_EDGE_NEIGHBOR,
                    "edge_strength": 1,
                    "child_desc": "Falling into the endless crater",
                    "child_label": "down",
                },
                test.get_text_edge(parent_id=rcontent_id2)[0],
                "Neighbors edge cannot be created",
            )

        # Test if player can be successfully created
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            player1 = test.create_player()[0]
            self.assert_sqlite_row_equal(
                {"id": player1}, test.get_player()[0], "Player cannot be created"
            )

        # Test if utterance can be successfully created
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            utterance1 = test.create_utterance("Hi")[0]
            self.assert_sqlite_row_equal(
                {"id": utterance1, "dialogue": "Hi"},
                test.get_utterance()[0],
                "Utterance cannot be created",
            )
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            utterance2 = test.create_utterance("Hello")[0]
            utterances = test.get_utterance()
            self.assert_sqlite_row_equal(
                {"id": utterance1, "dialogue": "Hi"},
                utterances[0],
                "Utterance cannot be created",
            )
            self.assert_sqlite_row_equal(
                {"id": utterance2, "dialogue": "Hello"},
                utterances[1],
                "Utterance cannot be created",
            )

        # Test if interaction can be successfully created and if duplicate
        # interactions are alllowed
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            interaction1 = test.create_interaction(rcontent_id1)[0]
            self.assert_sqlite_row_equal(
                {"id": interaction1, "setting_id": rcontent_id1},
                test.get_interaction()[0],
                "Interaction cannot be created",
            )

        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            interaction2 = test.create_interaction(rcontent_id1)[0]
            self.assertEqual(
                len(test.get_interaction()),
                2,
                "Duplicate interaction cannot be created",
            )

        # Test if participant can be successfully created
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            participant1 = test.create_participant(interaction2, ccontent_id1, player1)[
                0
            ]
            self.assert_sqlite_row_equal(
                {
                    "id": participant1,
                    "interaction_id": interaction2,
                    "character_id": ccontent_id1,
                    "player_id": player1,
                },
                test.get_participant()[0],
                "Participant cannot be created",
            )

        # Test if turn can be successfully created
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            turn1 = test.create_turn(
                interaction1, 1, 1, "action", None, "hit", participant1, participant1
            )[0]
            self.assert_sqlite_row_equal(
                {
                    "id": turn1,
                    "interaction_id": interaction1,
                    "turn_number": 1,
                    "turn_time": 1,
                    "interaction_type": "action",
                    "utterance_id": None,
                    "action": "hit",
                    "speaker_id": participant1,
                    "listener_id": participant1,
                },
                test.get_turn()[0],
                "Turn (action) cannot be created",
            )

        # Test if turn with no listener (spoken to a room) can be successfully
        # created
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            turn2 = test.create_turn(
                interaction2, 1, 1, "speech", utterance1, "", participant1, None
            )[0]
            self.assert_sqlite_row_equal(
                {
                    "id": turn2,
                    "interaction_id": interaction2,
                    "turn_number": 1,
                    "turn_time": 1,
                    "interaction_type": "speech",
                    "utterance_id": utterance1,
                    "action": "",
                    "speaker_id": participant1,
                    "listener_id": None,
                },
                test.get_turn(interaction_type="speech")[0],
                "Turn (speech) cannot be created",
            )

        # Prepare for testing if duplication alters id_table
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            id_len_before_dup = len(test.get_id())

        # Test if duplicate base room is avoided
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            base_room_name = "room"
            rbase_id_dup = test.create_base_room(base_room_name)[0]
            self.assertEqual(
                len(test.get_base_room(name=base_room_name)),
                1,
                "Base room is duplicated",
            )

        # Test if duplicate room is avoided
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            rcontent_id_dup = test.create_room("room1", rbase_id, "dirty", "old")[0]
            self.assertEqual(
                len(
                    test.get_room(
                        name="room1",
                        base_id=rbase_id,
                        description="dirty",
                        backstory="old",
                    )
                ),
                1,
                "Room is duplicated",
            )

        # Test if duplicate base character is avoided
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            cbase_id_dup = test.create_base_character("troll")[0]
            self.assertEqual(
                len(test.get_base_character(name="troll")),
                1,
                "Base character is duplicated",
            )

        # Test if duplicate character is avoided
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            ccontent_id1_dup = test.create_character(
                "troll under the bridge", cbase_id, "Male", "Tall"
            )[0]
            self.assertEqual(
                len(
                    test.get_character(
                        name="troll under the bridge",
                        base_id=cbase_id,
                        persona="Male",
                        physical_description="Tall",
                    )
                ),
                1,
                "Character is duplicated",
            )

        # Test if duplicate base object is avoided
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            obase_id_dup = test.create_base_object("room4")[0]
            self.assertEqual(
                len(test.get_base_object(name="room4")),
                1,
                "Base character is duplicated",
            )

        # Test if duplicate object is avoided
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            ocontent_id1_dup = test.create_object(
                None, obase_id, 0.4, 0.2, 0, 0, 0, 0, 0, "big", {}, None, None
            )[0]
            self.assertEqual(
                len(
                    test.get_object(
                        name="room4",
                        base_id=obase_id,
                        is_container=0.4,
                        is_drink=0.2,
                        is_food=0,
                        is_gettable=0,
                        is_surface=0,
                        is_wearable=0,
                        is_weapon=0,
                        physical_description="big",
                    )
                ),
                1,
                "Object is duplicated",
            )

        # Test if duplicate node content is avoided
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            test.create_node_content(
                rcontent_id1, ccontent_id1, DB_EDGE_EX_CONTAINED, 0
            )
            self.assertEqual(
                len(
                    test.get_node_content(
                        parent_id=rcontent_id1,
                        child_id=ccontent_id1,
                        edge_type=DB_EDGE_EX_CONTAINED,
                        edge_strength=0,
                    )
                ),
                1,
                "Node content (edge) is duplicated",
            )

        # Test if duplicate text edge is avoided
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            test.create_text_edge(rcontent_id1, "Spear", "neighbor", 1)
            self.assertEqual(
                len(test.get_text_edge(child_text="Spear")),
                1,
                "Text edge is duplicated",
            )

        # Test if duplicate utterance is avoided
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            utterance_dup = test.create_utterance("Hi")
            self.assertEqual(
                len(test.get_utterance(dialogue="Hi")), 1, "Utterance is duplicated"
            )

        # Test if duplicate participant is avoided
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            participant1_dup = test.create_participant(
                interaction2, ccontent_id1, player1
            )
            self.assertEqual(
                len(
                    test.get_participant(
                        interaction_id=interaction2,
                        character_id=ccontent_id1,
                        player_id=player1,
                    )
                ),
                1,
                "Participant is duplicated",
            )

        # Test if duplicate turn is avoided
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            turn1_dup = test.create_turn(
                interaction1, 1, 1, "action", None, "hit", participant1, participant1
            )
            self.assertEqual(
                len(
                    test.get_turn(
                        interaction_id=interaction1,
                        turn_number=1,
                        turn_time=1,
                        interaction_type="action",
                        utterance_id=None,
                        action="hit",
                        speaker_id=participant1,
                        listener_id=participant1,
                    )
                ),
                1,
                "Turn is duplicated",
            )

        # Check if id_table has been altered during duplication testing
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            self.assertEqual(
                id_len_before_dup,
                len(test.get_id()),
                "ID table has been altered during duplication testing",
            )

        # Test if foreign key constraint for room is working
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                test.create_room(None, rbase_id + 1, "dirty", "old")[0]

        # Test if foreign key constraint for character is working
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                test.create_character(
                    "troll under the bridge", cbase_id + 1, "Male", "Tall"
                )[0]

        # Test if foreign key constraint for object is working
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                test.create_object(None, obase_id + 1, 0.4, 0.2, 0, 0, 0, 0, 0, "big")[
                    0
                ]

        # Test if attributes constraints for object are working
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                test.create_object(None, obase_id, 4, 0.2, 0, 0, 0, 0, 0, "big")[0]

        # Test if foreign key constraint for node content is working
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                test.create_node_content(turn2, ccontent_id1, DB_EDGE_EX_CONTAINED, 0)

        # Test if edge type constraints for node content is working
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                test.create_node_content(turn2, ccontent_id1, "contained", 0)

        # Test if edge strength constraints for node content is working
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                test.create_node_content(turn2, ccontent_id1, "contained", 0.5)

        # Test if foreign key constraint for interaction is working
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                test.create_interaction(rcontent_id1 - 1)

        # Test if interaction foreign key constraint for participant is working
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                test.create_participant(interaction2 + 1, ccontent_id1, player1)

        # Test if character foreign key constraint for participant is working
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                test.create_participant(interaction2, ccontent_id1 + 1, player1)

        # Test if player foreign key constraint for participant is working
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                test.create_participant(interaction2, ccontent_id1, player1 + 1)

        # Test if interaction foreign key constraint for turn is working
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                turn1 = test.create_turn(
                    interaction1 - 1,
                    1,
                    1,
                    "action",
                    None,
                    "hit",
                    participant1,
                    participant1,
                )

        # Test if interaction type foreign key constraint for turn is working
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                turn1 = test.create_turn(
                    interaction1,
                    2,
                    1,
                    "actionsssss",
                    None,
                    "hit",
                    participant1,
                    participant1,
                )

        # Test if utterance ID foreign key constraint for turn is working
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                turn1 = test.create_turn(
                    interaction1,
                    3,
                    1,
                    "action",
                    utterance2 + 1,
                    "hit",
                    participant1,
                    participant1,
                )

        # Test if speaker foreign key constraint for turn is working
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                test.create_turn(
                    interaction1,
                    4,
                    1,
                    "action",
                    utterance2,
                    "hit",
                    participant1 + 1,
                    participant1,
                )

        # Test if listener foreign key constraint for turn is working
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                test.create_turn(
                    interaction1,
                    5,
                    1,
                    "action",
                    utterance2,
                    "hit",
                    participant1,
                    participant1 + 1,
                )

        # Test if all changes are rolled back when an error occurs
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                prev_id_len = len(test.get_id())
                test.create_room(None, rbase_id, "dirty", "new")[0]
                test.create_room("big room", rbase_id + 1, "clean", "old")[0]
        # Reopen an instance so __exit__ is called
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            # Test if the first valid insert is also reverted
            self.assertEqual(
                len(test.get_room(name="room", description="dirty", backstory="new")), 0
            )
            # Test if the id_table is unaffected
            self.assertEqual(len(test.get_id()), prev_id_len)

    # -----------------World Saving Test-----------------#

    def test_create_graph_nodes(self):
        """Test that graph node creation works and behaves as expected"""
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            player0 = test.create_user("test")[0]
            w_id = test.create_world("swamp", player0, 3, 3, 1)[0]

            rbase_id = test.create_base_room("room")[0]
            rcontent_id1 = test.create_room("room1", rbase_id, "dirty", "old")[0]
            cbase_id = test.create_base_character("troll")[0]
            ccontent_id1 = test.create_character(None, cbase_id, "tall", "big")[0]
            obase_id = test.create_base_object("object")[0]
            ocontent_id1 = test.create_object(
                "small obj", obase_id, 0, 0, 0, 0, 0, 0, 0, "dusty"
            )[0]
            rnode_id = test.create_graph_node(w_id, rcontent_id1)[0]
            cnode_id = test.create_graph_node(w_id, ccontent_id1)[0]
            onode_id = test.create_graph_node(w_id, ocontent_id1)[0]
            self.assert_sqlite_row_equal(
                {"id": rnode_id, "entity_id": rcontent_id1},
                test.get_node(rnode_id)[0],
                "Node entity id does not match room id",
            )
            self.assert_sqlite_row_equal(
                {"id": cnode_id, "entity_id": ccontent_id1},
                test.get_node(cnode_id)[0],
                "Node entity id does not match character id",
            )
            self.assert_sqlite_row_equal(
                {"id": onode_id, "entity_id": ocontent_id1},
                test.get_node(onode_id)[0],
                "Node entity id does not match object id",
            )

    def test_create_tiles(self):
        """Test that edge creation works and behaves as expected"""
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            player0 = test.create_user("test")[0]
            w_id = test.create_world("swamp", player0, 3, 3, 1)[0]

            rbase_id = test.create_base_room("room")[0]
            rcontent_id1 = test.create_room("room1", rbase_id, "dirty", "old")[0]

            rnode_id1 = test.create_graph_node(w_id, rcontent_id1)[0]

            tile_id = test.create_tile(w_id, rnode_id1, "#FFFFF", 1, 1, 0)[0]
            res = test.get_tiles(w_id)[0]
            self.assert_sqlite_row_equal(
                {
                    "id": tile_id,
                    "world_id": w_id,
                    "room_node_id": rnode_id1,
                    "color": "#FFFFF",
                    "x_coordinate": 1,
                    "y_coordinate": 1,
                    "floor": 0,
                },
                res,
                "Tile was not created succesfully",
            )

    def test_create_graph_edges(self):
        """Test that edge creation works and behaves as expected"""
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            player0 = test.create_user("test")[0]
            w_id = test.create_world("swamp", player0, 3, 3, 1)[0]

            rbase_id = test.create_base_room("room")[0]
            rcontent_id1 = test.create_room("room1", rbase_id, "dirty", "old")[0]
            rcontent_id2 = test.create_room("room2", rbase_id, "dirty", "old")[0]
            cbase_id = test.create_base_character("troll")[0]
            ccontent_id1 = test.create_character(None, cbase_id, "tall", "big")[0]

            rnode_id1 = test.create_graph_node(w_id, rcontent_id1)[0]
            rnode_id2 = test.create_graph_node(w_id, rcontent_id2)[0]
            cnode_id = test.create_graph_node(w_id, ccontent_id1)[0]

            tile_id = test.create_tile(w_id, rnode_id1, "#FFFFF", 1, 1, 0)[0]
            edge1 = test.create_graph_edge(
                w_id, rnode_id1, rnode_id2, "neighbors to the north"
            )[0]
            edge2 = test.create_graph_edge(w_id, rnode_id1, cnode_id, "contains")[0]
            edges = set()
            test.get_edges(tile_id, edges)
            edge_list = [{x: edge[x] for x in edge.keys()} for edge in edges]
            self.assertCountEqual(
                [
                    {
                        "id": edge1,
                        "w_id": w_id,
                        "src_id": rnode_id1,
                        "dst_id": rnode_id2,
                        "edge_type": "neighbors to the north",
                    },
                    {
                        "id": edge2,
                        "w_id": w_id,
                        "src_id": rnode_id1,
                        "dst_id": cnode_id,
                        "edge_type": "contains",
                    },
                ],
                edge_list,
            )

    def test_create_world(self):
        """Test that world creation works and behaves as expected"""
        # Test if a new world can be successfully created
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            player0 = test.create_user("test")[0]
            w_id = test.create_world("swamp", player0, 3, 3, 1)[0]
            self.assert_sqlite_row_equal(
                {
                    "id": w_id,
                    "name": "swamp",
                    "owner_id": player0,
                    "height": 3,
                    "width": 3,
                    "num_floors": 1,
                },
                test.get_world(w_id, player0)[0],
                "New World cannot be created",
            )

    def test_set_inactive_world(self):
        """Test that creation is active, and we make inactive with the set_inactive"""
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            player0 = test.create_user("test")[0]
            w1_id = test.create_world("swamp", player0, 3, 3, 1)[0]
            self.assertEqual(test.get_world(w1_id, player0)[0]["in_use"], 1)
            test.set_world_inactive(w1_id, player0)
            self.assertEqual(test.get_world(w1_id, player0)[0]["in_use"], 0)

    def test_autosave_basic(self):
        """Test that autosave works"""
        world_dict = {
            "dimensions": {
                "id": None,
                "name": "default",
                "height": 3,
                "width": 3,
                "floors": 1,
            },
            "entities": {"room": {}, "character": {}, "object": {}, "nextID": 1},
            "map": {"tiles": [], "edges": []},
        }
        curr_time = time.ctime(time.time())
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            player0 = test.create_user("test")[0]
            test.set_autosave(
                json.dumps(world_dict),
                player0,
                curr_time,
            )
            autosave = test.get_autosave(player0)
        self.assert_sqlite_row_equal(
            {
                "owner_id": player0,
                "timestamp": curr_time,
                "world_dump": json.dumps(world_dict),
            },
            autosave,
        )

    def test_autosave_update(self):
        """Test that autosave updates properly"""
        world_dict = {
            "dimensions": {
                "id": None,
                "name": "default",
                "height": 3,
                "width": 3,
                "floors": 1,
            },
            "entities": {"room": {}, "character": {}, "object": {}, "nextID": 1},
            "map": {"tiles": [], "edges": []},
        }
        curr_time = time.ctime(time.time())
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            player0 = test.create_user("test")[0]
            test.set_autosave(
                json.dumps(world_dict),
                player0,
                curr_time,
            )
            second_time = time.ctime(time.time())
            world_dict["dimensions"]["height"] = 10
            test.set_autosave(
                json.dumps(world_dict),
                player0,
                second_time,
            )
            autosave = test.get_autosave(
                player0,
            )
        self.assertEqual(autosave["timestamp"], second_time)
        self.assertEqual(json.loads(autosave["world_dump"])["dimensions"]["height"], 10)

    def test_view_worlds(self):
        """Test that view worlds returns all active worlds owned by player and only those worlds!"""
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            player0 = test.create_user("test")[0]
            w1_id = test.create_world("swamp", player0, 3, 3, 1)[0]
            w2_id = test.create_world("dragon guarded castle", player0, 2, 4, 2)[0]
            w3_id = test.create_world("far far away", player0, 2, 4, 2)[0]
            test.set_world_inactive(w3_id, player0)
            res = test.view_worlds(player0)
            self.assertEqual(len(res), 2)
            self.assertEqual(
                res,
                [
                    {
                        "height": 3,
                        "id": w1_id,
                        "in_use": 1,
                        "name": "swamp",
                        "num_floors": 1,
                        "owner_id": player0,
                        "width": 3,
                    },
                    {
                        "height": 2,
                        "id": w2_id,
                        "in_use": 1,
                        "name": "dragon guarded castle",
                        "num_floors": 2,
                        "owner_id": player0,
                        "width": 4,
                    },
                ],
            )

            # Can't see player0's worlds!
            player1 = test.create_user("test2")[0]
            w3_id = test.create_world("swamp2", player1, 3, 3, 5)[0]
            res = test.view_worlds(player1)
            self.assertEqual(len(res), 1)
            self.assertEqual(
                [
                    {
                        "height": 3,
                        "id": w3_id,
                        "in_use": 1,
                        "name": "swamp2",
                        "num_floors": 5,
                        "owner_id": player1,
                        "width": 3,
                    }
                ],
                res,
            )

    def test_world_deletion(self):
        """Test that delete worlds works as expected (ownly owner can delete)"""
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            player0 = test.create_user("test")[0]
            player1 = test.create_user("test2")[0]
            w1_id = test.create_world("swamp", player0, 3, 3, 1)[0]

            with self.assertRaises(Exception):
                test.delete_world(w1_id, player1)
            self.assertEqual(len(test.view_worlds(player0)), 1)
            test.delete_world(w1_id, player0)
            self.assertEqual(len(test.view_worlds(player0)), 0)

    def test_world_limit(self):
        """Test that the limit on world creation is enforced properly"""
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            player0 = test.create_user("test")[0]
            player1 = test.create_user("test2")[0]
            for i in range(10):
                test.create_world("swamp" + str(i), player0, 3, 3, 1)[0]
            res = test.create_world("swamp10", player0, 3, 3, 1)
            self.assertEqual(res, (-1, False))
            res = test.create_world("swamp10", player1, 3, 3, 1)
            self.assertEqual(res[1], True)

    # ---------------------------------------------------#

    def test_status(self):
        """Test that status in the master ID table behaves as expected"""
        # test if created entities have default value of False for is_from_pickle
        # and DB_STATUS_REVIEW for status
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            rbase_id = test.create_base_room("room")[0]
            rcontent_id1 = test.create_room("room1", rbase_id, "dirty", "old")[0]
            cbase_id = test.create_base_character("troll")[0]
            ccontent_id1 = test.create_character(None, cbase_id, "tall", "big")[0]
            for i in test.get_id():
                assert i[2] == DB_STATUS_REVIEW and i[3] == 0

        # test if status can be successfully changed to DB_STATUS_PROD
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            test.update_status(rbase_id, DB_STATUS_PROD)
            self.assert_sqlite_row_equal(
                {
                    "id": rbase_id,
                    "type": DB_TYPE_BASE_ROOM,
                    "status": DB_STATUS_PROD,
                    "is_from_pickle": 0,
                },
                test.get_id(id=rbase_id)[0],
            )
            self.assert_sqlite_row_equal(
                {
                    "id": rcontent_id1,
                    "type": DB_TYPE_ROOM,
                    "status": DB_STATUS_REVIEW,
                    "is_from_pickle": 0,
                },
                test.get_id(id=rcontent_id1)[0],
            )

        # test if status can be successfully changed to DB_STATUS_REJECTED
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            test.update_status(ccontent_id1, DB_STATUS_REJECTED)
            self.assert_sqlite_row_equal(
                {
                    "id": cbase_id,
                    "type": DB_TYPE_BASE_CHAR,
                    "status": DB_STATUS_REVIEW,
                    "is_from_pickle": 0,
                },
                test.get_id(id=cbase_id)[0],
            )
            self.assert_sqlite_row_equal(
                {
                    "id": ccontent_id1,
                    "type": DB_TYPE_CHAR,
                    "status": DB_STATUS_REJECTED,
                    "is_from_pickle": 0,
                },
                test.get_id(id=ccontent_id1)[0],
            )

        # test if passing an unknown status raises an error
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                test.update_status(ccontent_id1, "unknown")

        # test if passing an unknown ID raises an error
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                test.update_status(-1, "unknown")

    # TODO return to update when game save format is finalized
    def test_save_single_game(self):
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            graph = "graph_name"
            creator = test.create_player()[0]
            base_room1 = test.create_base_room("baseroom1")[0]
            room1 = test.create_room("room1", base_room1, "dirty", "old")[0]
            base_room2 = test.create_base_room("baseroom2")[0]
            room2 = test.create_room("room2", base_room2, "clean", "old")[0]
            room3 = test.create_room("room3", base_room2, "clean", "new")[0]
            base_char = test.create_base_character("troll")[0]
            char = test.create_character(None, base_char, "tall", "big")[0]
            base_obj = test.create_base_object("obj")[0]
            # test % wildcard in front of search string works
            obj1 = test.create_object(
                "small obj", base_obj, 0, 0, 0, 0, 0, 0, 0, "dusty"
            )[0]
            # test % wildcard after search string works
            obj2 = test.create_object(
                "big obj", base_obj, 0, 0, 0, 0, 0, 0, 1, "clean"
            )[0]
            room1_room2 = test.create_node_content(room1, room2, "neighbor", 1)[0]
            room1_room3 = test.create_node_content(room1, room3, "neighbor", 1)[0]
            room1_char = test.create_node_content(room1, char, DB_EDGE_IN_CONTAINED, 1)[
                0
            ]
            room1_obj1 = test.create_node_content(room1, obj1, DB_EDGE_IN_CONTAINED, 1)[
                0
            ]
            room2_obj2 = test.create_node_content(room2, obj2, DB_EDGE_IN_CONTAINED, 1)[
                0
            ]
            edges = {
                room1: [
                    {
                        "child": room2,
                        "type": "neighbor",
                        "edge": room1_room2,
                        "direction": "W",
                    },
                    {
                        "child": room3,
                        "type": "neighbor",
                        "edge": room1_room3,
                        "direction": "N",
                    },
                    {"child": char, "type": "non_neighbor", "edge": room1_char},
                    {"child": obj1, "type": "non_neighbor", "edge": room1_obj1},
                ],
                room2: [{"child": obj2, "type": "non_neighbor", "edge": room2_obj2}],
                room3: [],
            }
            game_id = test.save_single_game(graph, edges, creator)
            self.assert_sqlite_row_equal(
                {"game_id": game_id, "graph": "graph_name", "creator": creator},
                test.get_games()[0],
            )
            self.assert_sqlite_rows_equal(
                [
                    {"component_id": 1, "game": game_id, "component": room1},
                    {"component_id": 2, "game": game_id, "component": char},
                    {"component_id": 3, "game": game_id, "component": obj1},
                    {"component_id": 4, "game": game_id, "component": room2},
                    {"component_id": 5, "game": game_id, "component": obj2},
                    {"component_id": 6, "game": game_id, "component": room3},
                ],
                test.get_game_components(),
            )
            self.assert_sqlite_rows_equal(
                [
                    {
                        "edge_id": 1,
                        "game": game_id,
                        "parent": room1,
                        "child": room2,
                        "edge": room1_room2,
                        "direction": "W",
                    },
                    {
                        "edge_id": 2,
                        "game": game_id,
                        "parent": room1,
                        "child": room3,
                        "edge": room1_room3,
                        "direction": "N",
                    },
                    {
                        "edge_id": 3,
                        "game": game_id,
                        "parent": room1,
                        "child": char,
                        "edge": room1_char,
                        "direction": None,
                    },
                    {
                        "edge_id": 4,
                        "game": game_id,
                        "parent": room1,
                        "child": obj1,
                        "edge": room1_obj1,
                        "direction": None,
                    },
                    {
                        "edge_id": 5,
                        "game": game_id,
                        "parent": room2,
                        "child": obj2,
                        "edge": room2_obj2,
                        "direction": None,
                    },
                ],
                test.get_game_edges(),
            )

    def test_load_single_conversation(self):
        """Tests whether loading a single conversation works"""
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            base_room = test.create_base_room("room")[0]
            room = test.create_room("room1", base_room, "dirty", "old")[0]
            base_char = test.create_base_character("troll")[0]
            char = test.create_character(None, base_char, "tall", "big")[0]
            player0 = test.create_player()[0]
            player1 = test.create_player()[0]
            player2 = test.create_player()[0]
            participants = [(char, player0), (char, player1), (char, player2)]
            turns = [
                {
                    "speaker": 0,
                    "listener": None,
                    "interaction": {"type": "speech", "content": "utterance1"},
                    "turn_time": 5,
                },
                {
                    "speaker": 2,
                    "listener": 1,
                    "interaction": {"type": "emote", "content": "emote1"},
                    "turn_time": 4,
                },
                {
                    "speaker": 2,
                    "listener": None,
                    "interaction": {"type": "action", "content": "action1"},
                    "turn_time": 3,
                },
                {
                    "speaker": 1,
                    "listener": 2,
                    "interaction": {"type": "speech", "content": "utterance2"},
                    "turn_time": 2,
                },
            ]
            interaction_id = test.add_single_conversation(room, participants, turns)
            # check that the interaction is correct
            self.assert_sqlite_row_equal(
                {"id": interaction_id, "setting_id": room},
                test.get_query(interaction_id),
            )
            # check that the participants are correct
            participants_retrieved = test.get_id(type="participant", expand=True)
            self.assert_sqlite_rows_equal(
                [
                    {
                        "interaction_id": interaction_id,
                        "character_id": char,
                        "player_id": player0,
                    },
                    {
                        "interaction_id": interaction_id,
                        "character_id": char,
                        "player_id": player1,
                    },
                    {
                        "interaction_id": interaction_id,
                        "character_id": char,
                        "player_id": player2,
                    },
                ],
                participants_retrieved,
            )
            # check that the turns are correct
            turns_retrieved = test.get_id(type="turn", expand=True)
            utterance1 = test.get_utterance(dialogue="utterance1")[0][0]
            utterance2 = test.get_utterance(dialogue="utterance2")[0][0]
            par0 = test.get_participant(character_id=char, player_id=player0)[0][0]
            par1 = test.get_participant(character_id=char, player_id=player1)[0][0]
            par2 = test.get_participant(character_id=char, player_id=player2)[0][0]
            self.assert_sqlite_rows_equal(
                [
                    {
                        "interaction_id": interaction_id,
                        "turn_number": 0,
                        "turn_time": 5,
                        "interaction_type": "speech",
                        "utterance_id": utterance1,
                        "action": None,
                        "speaker_id": par0,
                        "listener_id": None,
                    },
                    {
                        "interaction_id": interaction_id,
                        "turn_number": 1,
                        "turn_time": 4,
                        "interaction_type": "emote",
                        "utterance_id": None,
                        "action": "emote1",
                        "speaker_id": par2,
                        "listener_id": par1,
                    },
                    {
                        "interaction_id": interaction_id,
                        "turn_number": 2,
                        "turn_time": 3,
                        "interaction_type": "action",
                        "utterance_id": None,
                        "action": "action1",
                        "speaker_id": par2,
                        "listener_id": None,
                    },
                    {
                        "interaction_id": interaction_id,
                        "turn_number": 3,
                        "turn_time": 2,
                        "interaction_type": "speech",
                        "utterance_id": utterance2,
                        "action": None,
                        "speaker_id": par1,
                        "listener_id": par2,
                    },
                ],
                turns_retrieved,
            )

            # test whether duplicate conversation is detected and ignored
            interaction_id_dup = test.add_single_conversation(room, participants, turns)
            self.assertEqual(interaction_id_dup, -1)
            participants_retrieved_dup = test.get_id(type="participant", expand=True)
            self.assertEqual(len(participants_retrieved_dup), 3)
            turns_retrieved_dup = test.get_id(type="turn", expand=True)
            self.assertEqual(len(turns_retrieved_dup), 4)

    def test_load_single_conversation_errors(self):
        """Tests whether errors are detected when loading conversations"""
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            base_room = test.create_base_room("room")[0]
            room = test.create_room("room1", base_room, "dirty", "old")[0]
            base_char = test.create_base_character("troll")[0]
            char = test.create_character(None, base_char, "tall", "big")[0]
            player0 = test.create_player()[0]
            player1 = test.create_player()[0]
            player2 = test.create_player()[0]
            participants = [(char, player0), (char, player1), (char, player2)]
            turns = [
                {
                    "speaker": 0,
                    "listener": None,
                    "interaction": {"type": "speech", "content": "utterance1"},
                    "turn_time": 5,
                },
                {
                    "speaker": 2,
                    "listener": 1,
                    "interaction": {"type": "emote", "content": "emote1"},
                    "turn_time": 4,
                },
                {
                    "speaker": None,
                    "listener": None,
                    "interaction": {"type": "action", "content": "action1"},
                    "turn_time": 3,
                },
            ]
            # error should be raised when speaker is null in a conversation
            with self.assertRaises(Exception):
                _interaction_id = test.add_single_conversation(
                    room, participants, turns
                )

    def test_load_data(self):
        """
        Test if pickle files can be successfully loaded into the database.
        Creates temporary pickle files and attempts to load them.
        """
        enviro_data = {}
        enviro_data["objects"] = {
            0: {
                "base_form": ["tree"],
                "desc_entries": 1,
                "descriptions": ["the tree is tall and leafy"],
                "ex_room_ids": [],
                "holding_character_ids": [],
                "in_room_ids": [1],
                "is_container": 0.0,
                "is_drink": 0.0,
                "is_food": 0.0,
                "is_gettable": 1.0,
                "is_plural": 1.0,
                "is_surface": 0.0,
                "is_weapon": 0.0,
                "is_wearable": 0.0,
                "link_entries": 1,
                "name": "towering pine trees",
                "object_id": 0,
            },
            1: {
                "base_form": ["Long skinny tree", "tree"],
                "desc_entries": 2,
                "descriptions": [
                    "the tree is tall and skinny",
                    "the tree is short and thick",
                ],
                "ex_room_ids": [],
                "holding_character_ids": [],
                "in_room_ids": [1],
                "is_container": 0.0,
                "is_drink": 0.0,
                "is_food": 0.0,
                "is_gettable": 0.0,
                "is_plural": 1.0,
                "is_surface": 0.0,
                "is_weapon": 0.0,
                "is_wearable": 0.0,
                "link_entries": 1,
                "name": "Long skinny trees",
                "object_id": 1,
            },
        }
        enviro_data["characters"] = {
            0: {
                "base_form": ["Deer", "deer long"],
                "carrying_objects": [],
                "char_type": "creature",
                "character_id": 0,
                "corrected_name": "deer",
                "desc": "magestic and beautiful deer",
                "ex_room_ids": [0],
                "in_room_ids": [],
                "is_plural": 0,
                "name": "deer",
                "orig_room_id": 0,
                "personas": ["I am a deer"],
                "wearing_objects": [],
                "wielding_objects": [],
            },
            1: {
                "base_form": ["animal"],
                "carrying_objects": [1],
                "char_type": "person",
                "character_id": 1,
                "corrected_name": "other animals",
                "desc": "A friendly and playful beast",
                "ex_room_ids": [],
                "in_room_ids": [1],
                "is_plural": 1,
                "name": "other animals",
                "orig_room_id": 1,
                "personas": ["I like to play", "I like to sleep"],
                "wearing_objects": [0],
                "wielding_objects": [],
            },
        }
        enviro_data["rooms"] = {
            0: {
                "background": "old forest",
                "category": "Forest",
                "description": "huge trees",
                "ex_characters": [1],
                "ex_objects": [1],
                "in_characters": [],
                "in_objects": [],
                "neighbors": [1],
                "room_id": 0,
                "setting": "Entrance to the Pine trees",
            },
            1: {
                "background": "abandoned boat",
                "category": "Shore",
                "description": "It is a glamorous wooden ship.",
                "ex_characters": [],
                "ex_objects": [],
                "in_characters": [0],
                "in_objects": [],
                "neighbors": [0],
                "room_id": 1,
                "setting": "A battleship",
            },
        }
        enviro_data["neighbors"] = {
            0: {
                "connection": "down the hill",
                "destination": "creek",
                "direction": "West",
                "inverse_id": None,
                "room_id": 1,
            },
            1: {
                "connection": "northern trail",
                "destination": "picnic area",
                "direction": "North",
                "inverse_id": None,
                "room_id": 1,
            },
        }
        enviro_pickle = open(os.path.join(self.data_dir, "enviro.pickle"), "wb")
        pickle.dump(enviro_data, enviro_pickle)
        enviro_pickle.close()

        conv_data = [
            {
                "accepted_agents": ["deer", "Other animals"],
                "conv_info": {
                    "acts": [
                        {
                            "duration": 1,
                            "episode_done": False,
                            "id": "Deer",
                            "message_id": "d63d6649-62a3-4ecd-a868-94119c44e7ae",
                            "task_data": {
                                "action": "",
                                "actions": ["give sword to other animals"],
                                "carrying": [],
                                "persona": "I am a deer",
                                "room_agents": ["deer", "other animals"],
                                "room_objects": [],
                                "setting": "A battleship",
                                "text_context": "A battleship",
                                "wearing": [],
                                "wielding": [],
                            },
                            "text": "hello",
                        },
                        {
                            "duration": 2,
                            "episode_done": False,
                            "id": "other animals",
                            "message_id": "d63d6649-62a3-4ecd-a868-94119c44e7af",
                            "task_data": {
                                "action": "",
                                "actions": [],
                                "carrying": [],
                                "persona": "I like to play",
                                "room_agents": ["deer", "other animals"],
                                "room_objects": [],
                                "setting": "A battleship",
                                "text_context": "A battleship",
                                "wearing": [],
                                "wielding": [],
                            },
                            "text": "hello to you too",
                        },
                    ],
                    "characters": [
                        [
                            "deer",
                            {
                                "base_form": ["deer"],
                                "carrying_objects": [],
                                "char_type": "creature",
                                "character_id": 0,
                                "corrected_name": "deer",
                                "desc": "magestic and beautiful",
                                "ex_room_ids": [0, 1],
                                "id": 0,
                                "in_room_ids": [],
                                "is_plural": 0,
                                "name": "deer",
                                "orig_room_id": 0,
                                "personas": ["I am a deer", "I like to play"],
                                "wearing_objects": [],
                                "wielding_objects": [],
                            },
                        ],
                        [
                            "other animals",
                            {
                                "base_form": ["animal"],
                                "carrying_objects": [1],
                                "char_type": "person",
                                "character_id": 1,
                                "corrected_name": "other animals",
                                "desc": "A friendly and playful beast",
                                "ex_room_ids": [],
                                "id": 1,
                                "in_room_ids": [1],
                                "is_plural": 1,
                                "name": "other animals",
                                "orig_room_id": 1,
                                "personas": ["I like to play", "I like to sleep"],
                                "wearing_objects": [0],
                                "wielding_objects": [],
                            },
                        ],
                    ],
                    "needs-pickle": None,
                    "room": {
                        "background": "abandoned boat",
                        "category": "Shore",
                        "description": "It is a glamorous wooden ship.",
                        "ex_characters": [],
                        "ex_objects": [1],
                        "in_characters": [0],
                        "in_objects": [],
                        "neighbors": [0],
                        "id": 1,
                        "setting": "A battleship",
                    },
                },
            }
        ]
        conv_pickle = open(os.path.join(self.data_dir, "conv.pickle"), "wb")
        pickle.dump(conv_data, conv_pickle)
        conv_pickle.close()

        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            test.add_environment_data(
                os.path.join(self.data_dir, "enviro.pickle"), disable_TQDM=True
            )
            test.add_conversation_data(
                os.path.join(self.data_dir, "conv.pickle"), disable_TQDM=True
            )

        # check that all entries loaded from pickle file has is_from_pickle as True
        # and status set as "in produciton"
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            for i in test.get_id():
                assert i[2] == DB_STATUS_PROD and i[3] == 1

        # Test if base rooms and rooms are created successfully
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            self.assertEqual(
                len(test.get_base_room(name="Forest")),
                1,
                "Base room is not successfully created",
            )
            self.assertEqual(
                len(test.get_base_room(name="Shore")),
                1,
                "Base room is not successfully created",
            )
            rooms_no_id = set([i[1:] for i in test.get_room()])
            self.assertEqual(
                rooms_no_id,
                set(
                    [
                        ("Entrance to the Pine trees", 1, "huge trees", "old forest"),
                        (
                            "A battleship",
                            3,
                            "It is a glamorous wooden ship.",
                            "abandoned boat",
                        ),
                    ]
                ),
                "Rooms are not successfully created",
            )

        # Test if base characters and characters are created successfully
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            self.assertEqual(
                len(test.get_base_character(name="animal")),
                1,
                "Base character is not successfully created",
            )
            self.assertEqual(
                len(test.get_base_character(name="deer long")),
                0,
                "Did not use the shorter base character name when multiple "
                "are provided",
            )
            self.assertEqual(
                len(test.get_base_character(name="deer")),
                1,
                "Base character name is not successfully converted to all "
                "lower case",
            )
            chars_no_id = set([i[1:5] for i in test.get_character()])
            self.assertEqual(
                chars_no_id,
                set(
                    [
                        ("deer", 5, "I am a deer", "magestic and beautiful deer"),
                        (
                            "other animals",
                            7,
                            "I like to play",
                            "A friendly and playful beast",
                        ),
                        (
                            "other " "animals",
                            7,
                            "I like to sleep",
                            "A friendly and playful " "beast",
                        ),
                    ]
                ),
                "Characters are not successfully created",
            )

        # Test if base objects and objects are created successfully
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            self.assertEqual(
                len(test.get_base_object(name="tree")),
                1,
                "Base object is not successfully created",
            )
            objects_no_id = set([i[1:11] for i in test.get_object()])
            self.assertEqual(
                objects_no_id,
                set(
                    [
                        (
                            "towering pine trees",
                            10,
                            0,
                            0,
                            0,
                            1,
                            0,
                            0,
                            0,
                            "the tree is tall and leafy",
                        ),
                        (
                            "Long skinny trees",
                            10,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            "the tree is tall and skinny",
                        ),
                    ]
                ),
                "Objects are not successfully created",
            )

        # Test if node contents (edges) are created successfully
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            edges_no_id = set([i[1:] for i in test.get_node_content()])
            self.assertEqual(
                edges_no_id,
                set(
                    [
                        (8, 13, DB_EDGE_IN_CONTAINED, 1),
                        (9, 13, DB_EDGE_IN_CONTAINED, 1),
                        (2, 8, DB_EDGE_EX_CONTAINED, 0),
                        (8, 11, DB_EDGE_WORN, 1),
                        (2, 13, DB_EDGE_EX_CONTAINED, 0),
                        (4, 6, DB_EDGE_IN_CONTAINED, 1),
                        (9, 11, DB_EDGE_WORN, 1),
                        (2, 9, DB_EDGE_EX_CONTAINED, 0),
                    ]
                ),
                "Node contents are not successfully created",
            )

        # Test that a conversation can be loaded successfully
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            self.assertEqual(len(test.get_player()), 2, "Incorrect number" "of players")
            players = [i[0] for i in test.get_player()]
            players_from_participants = [i[3] for i in test.get_participant()]
            self.assertEqual(
                set(players),
                set(players_from_participants),
                "Players do not correspond to participants",
            )
            self.assertEqual(len(test.get_interaction()), 1)
            interaction_id = test.get_interaction()[0][0]
            self.assertEqual(len(test.get_character(name="deer")), 1)
            deer_id = test.get_character(name="deer")[0][0]
            self.assertEqual(len(test.get_character(name="other animals")), 2)
            animal_id = test.get_character(name="other animals")[0][0]
            self.assertEqual(len(test.get_participant(character_id=deer_id)), 1)
            deer_participant = test.get_participant(character_id=deer_id)[0][0]
            self.assertEqual(len(test.get_participant(character_id=animal_id)), 1)
            animal_participant = test.get_participant(character_id=animal_id)[0][0]
            self.assertEqual(len(test.get_utterance(dialogue="hello")), 1)
            utterance1 = test.get_utterance(dialogue="hello")[0][0]
            self.assertEqual(len(test.get_utterance(dialogue="hello to you too")), 1)
            utterance2 = test.get_utterance(dialogue="hello to you too")[0][0]
            # check that the turns are created as expected
            turns_no_id = [i[1:] for i in test.get_turn()]
            turn1 = (
                interaction_id,
                0,
                1,
                "speech",
                utterance1,
                None,
                deer_participant,
                animal_participant,
            )
            turn2 = (
                interaction_id,
                1,
                2,
                "speech",
                utterance2,
                None,
                animal_participant,
                deer_participant,
            )
            self.assertEqual(set([turn1, turn2]), set(turns_no_id))

    def test_edit_entity(self):
        """
        Tests whether editing entities in the database (except for utterances)
        is working correctly
        """
        # Set up necessary content in the database for the unit test
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            rbase_id = test.create_base_room("room")[0]
            rcontent_id1 = test.create_room("room1", rbase_id, "dirty", "old")[0]
            player1 = test.create_player()[0]

        # Test if an edit for the name of a room can be submitted
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            edit0 = test.submit_edit(rbase_id, "name", "base room edit", player1)
            edit1 = test.submit_edit(rcontent_id1, "name", "room edit", player1)
            self.assertEqual(
                [i[:7] for i in test.get_edit(edit_id=edit1)],
                [
                    (
                        edit1,
                        rcontent_id1,
                        "name",
                        "room1",
                        "room edit",
                        player1,
                        DB_STATUS_REVIEW,
                    )
                ],
                "Edit not submitted correctly",
            )

        # Test if a non-utterance edit can be marked as rejected
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            test.reject_edit(edit1)
            self.assertEqual(
                [i[:7] for i in test.get_edit(edit_id=edit1)],
                [
                    (
                        edit1,
                        rcontent_id1,
                        "name",
                        "room1",
                        "room edit",
                        player1,
                        DB_STATUS_REJECTED,
                    )
                ],
                "Edit not rejected correctly",
            )

        # Test if a non-utterance edit can be marked as accepted and enacted
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            test.accept_edit(edit1, DB_STATUS_ACCEPTED)
            self.assertEqual(
                [i[:7] for i in test.get_edit(edit_id=edit1)],
                [
                    (
                        edit1,
                        rcontent_id1,
                        "name",
                        "room1",
                        "room edit",
                        player1,
                        DB_STATUS_ACCEPTED,
                    )
                ],
                "Edit not accepted correctly",
            )
            self.assertEqual(
                [i[:5] for i in test.get_room(id=rcontent_id1)],
                [(rcontent_id1, "room edit", rbase_id, "dirty", "old")],
            )

        # Test if an edit for the name of a base form can be viewed
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            self.assertEqual(
                test.view_edit(edit0),
                {
                    "edit_id": edit0,
                    "id": rbase_id,
                    "field": "name",
                    "unedited_value": "room",
                    "edited_value": "base room edit",
                    "status": DB_STATUS_REVIEW,
                    "type": DB_TYPE_BASE_ROOM,
                    "player_id": player1,
                },
                "Cannot view edit for base form correctly",
            )

        # Test if an edit for the name of a entity can be viewed
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            self.assertEqual(
                test.view_edit(edit1),
                {
                    "base": "room",
                    "edit_id": edit1,
                    "id": rcontent_id1,
                    "field": "name",
                    "unedited_value": "room1",
                    "edited_value": "room edit",
                    "status": DB_STATUS_ACCEPTED,
                    "type": "room",
                    "player_id": player1,
                },
                "Cannot view edit for entity correctly",
            )

    def test_edit_utterance(self):
        """
        Tests whether editing utterances updates both the edits table and the
        database when the edits are accepted (accepted_one or accepted_all)
        """
        # Set up necessary content in the database for the unit test
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            rbase_id = test.create_base_room("room")[0]
            rcontent_id1 = test.create_room("room1", rbase_id, "dirty", "old")[0]
            cbase_id = test.create_base_character("troll")[0]
            ccontent_id1 = test.create_character(None, cbase_id, "tall", "big")[0]
            player1 = test.create_player()[0]
            player2 = test.create_player()[0]
            player3 = test.create_player()[0]
            utterance1 = test.create_utterance("Hi")[0]
            utterance2 = test.create_utterance("Hello")[0]
            utterance3 = test.create_utterance("Hi edit")[0]
            utterance4 = test.create_utterance("Hi edit2")[0]
            interaction1 = test.create_interaction(rcontent_id1)[0]
            interaction2 = test.create_interaction(rcontent_id1)[0]
            interaction3 = test.create_interaction(rcontent_id1)[0]
            participant1 = test.create_participant(interaction1, ccontent_id1, player1)[
                0
            ]
            participant2 = test.create_participant(interaction2, ccontent_id1, player2)[
                0
            ]
            participant3 = test.create_participant(interaction3, ccontent_id1, player3)[
                0
            ]
            turn1_1 = test.create_turn(
                interaction1, 0, 1, "speech", utterance1, "", participant1, None
            )[0]
            turn1_2 = test.create_turn(
                interaction1, 1, 1, "speech", utterance2, "", participant1, None
            )[0]
            turn2_1 = test.create_turn(
                interaction2, 0, 1, "speech", utterance1, "", participant2, None
            )[0]
            turn2_2 = test.create_turn(
                interaction2, 1, 1, "speech", utterance1, "", participant2, participant2
            )[0]
            turn3_1 = test.create_turn(
                interaction3, 0, 1, "speech", utterance1, "", participant3, None
            )[0]

        # Test if an edit for an utterance can be submitted
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            edit2 = test.submit_edit(turn2_1, "utterance_id", "Hi edit", player2)
            self.assertEqual(
                [i[:7] for i in test.get_edit(edit_id=edit2)],
                [
                    (
                        edit2,
                        turn2_1,
                        "utterance_id",
                        str(utterance1),
                        str(utterance3),
                        player2,
                        DB_STATUS_REVIEW,
                    )
                ],
                "Utterance edit not submitted correctly",
            )

        # Test if an edit for an utterance can be submitted
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            edit3 = test.submit_edit(turn2_2, "utterance_id", "Hi edit2", player2)
            self.assertEqual(
                [i[:7] for i in test.get_edit(edit_id=edit3)],
                [
                    (
                        edit3,
                        turn2_2,
                        "utterance_id",
                        str(utterance1),
                        str(utterance4),
                        player2,
                        DB_STATUS_REVIEW,
                    )
                ],
                "Utterance edit not submitted correctly",
            )

        # Test if an utterance edit can be marked as accepted_all and
        # edited successfully in the database
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            # prev_edit_turns contains all turns that contain the utterance
            # marked for editing
            prev_edit_turns = test.get_turn(utterance_id=utterance1)
            # prev_interactions contains all interactions that contains the
            # utterance marked for editing
            prev_interactions = set()
            for t in prev_edit_turns:
                prev_interactions.add(t[1])
            # prev_turns contains all turns in prev_interactions that do not
            # contain the utterance marked for editing
            prev_turns = set()
            for i in prev_interactions:
                prev_turns.update(test.get_turn(interaction_id=i))
            prev_turns = prev_turns - set(prev_edit_turns)
            # change status to accept_all and enact edit
            test.accept_edit(edit3, DB_STATUS_ACCEPT_ALL)
            # Check that the actual turn marked for editing is not changed in
            # the database (we want to create a duplicate conversation with the
            # edit but keep the original conversation the same)
            self.assertEqual(
                [i[:9] for i in test.get_turn(id=turn2_2)],
                [
                    (
                        turn2_2,
                        interaction2,
                        1,
                        1,
                        "speech",
                        utterance1,
                        "",
                        participant2,
                        participant2,
                    )
                ],
            )
            after_edit_turns = test.get_turn(utterance_id=utterance4)
            # check that the turns containing the edited utterance are
            # identical except for ids and the edited utterance in the original
            # turns and the turns duplicated when the edit is enacted
            prev_edit_turn_no_id_interaction = [i[2:5] + i[6:] for i in prev_edit_turns]
            after_edit_turn_no_id_interaction = [
                i[2:5] + i[6:] for i in after_edit_turns
            ]
            self.assertEqual(
                set(prev_edit_turn_no_id_interaction),
                set(after_edit_turn_no_id_interaction),
            )
            # check that the turns not containing the edited utterance are
            # identical except for ids in the original turns and the turns
            # duplicated when the utterance is enacted
            after_interactions = set()
            for t in after_edit_turns:
                after_interactions.add(t[1])
            after_turns = set()
            for i in after_interactions:
                after_turns.update(test.get_turn(interaction_id=i))
            after_turns = after_turns - set(after_edit_turns)
            prev_turns = [i[2:5] + i[6:] for i in prev_turns]
            after_turns = [i[2:5] + i[6:] for i in after_turns]
            self.assertEqual(set(prev_turns), set(after_turns))

        # Test if an edit for an utterance can be viewed
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            self.assertEqual(
                test.view_edit(edit2),
                {
                    "edit_id": edit2,
                    "id": turn2_1,
                    "field": "utterance_id",
                    "edited_value": "Hi edit",
                    "status": DB_STATUS_REVIEW,
                    "type": "utterance",
                    "utterances": ["Hi", "Hi"],
                    "room": "room1",
                    "characters": ["troll"],
                    "turn_number": 0,
                    "player_id": player2,
                },
                "Cannot view edit for utterance correctly",
            )

        # Test if an edit for utterance can be marked as rejected
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            test.reject_edit(edit2)
            self.assertEqual(
                [i[:7] for i in test.get_edit(edit_id=edit2)],
                [
                    (
                        edit2,
                        turn2_1,
                        "utterance_id",
                        str(utterance1),
                        str(test.create_utterance("Hi edit")[0]),
                        player2,
                        DB_STATUS_REJECTED,
                    )
                ],
                "Utterance edit not rejected correctly",
            )

        # Test if an utterance edit can be marked as accepted one and enacted
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            test.accept_edit(edit2, DB_STATUS_ACCEPT_ONE)
            self.assertEqual(
                [i[:7] for i in test.get_edit(edit_id=edit2)],
                [
                    (
                        edit2,
                        turn2_1,
                        "utterance_id",
                        str(utterance1),
                        str(utterance3),
                        player2,
                        DB_STATUS_ACCEPT_ONE,
                    )
                ],
                "Utterance edit for one not accepted correctly",
            )
            # Check that the actual turn marked for editing is not changed in
            # the database (we want to create a duplicate conversation with the
            # edit but keep the original conversation the same)
            self.assertEqual(
                [i[:9] for i in test.get_turn(id=turn2_1)],
                [
                    (
                        turn2_1,
                        interaction2,
                        0,
                        1,
                        "speech",
                        utterance1,
                        "",
                        participant2,
                        None,
                    )
                ],
            )
            # Interaction that contains the turn marked for editing
            prev_interaction = interaction2
            # Interation duplicated from prev_interaction (identical except the
            # turn marked for editing, which is edited in after_interaction
            # but not prev_interaction)
            after_interaction = test.get_turn(utterance_id=utterance3)[-1][1]
            # turns contained in prev_interaction and after_interaction
            prev_turns = test.get_turn(interaction_id=prev_interaction)
            after_turns = test.get_turn(interaction_id=after_interaction)
            # check that all but one turn (the one marked for editing) are
            # identical in prev_turns and after_turns in all fields but id and
            # interaction ID
            prev_turns_no_id_interaction = [i[2:] for i in prev_turns]
            after_turns_no_id_interaction = [i[2:] for i in after_turns]
            self.assertEqual(
                len(
                    set(prev_turns_no_id_interaction)
                    & set(after_turns_no_id_interaction)
                ),
                len(prev_turns) - 1,
            )
            # chekc that the one turn marked for editing in the duplicated
            # conversation has correct information
            self.assertEqual(
                [i[:9] for i in test.get_turn(utterance_id=utterance3)][-1][2:],
                (0, 1, "speech", utterance3, "", participant2, None),
            )
            # chekc that the one turn marked for editing in the original
            # conversation has correct information (not altered)
            self.assertEqual(
                [i[:9] for i in test.get_turn(id=turn1_1)],
                [
                    (
                        turn1_1,
                        interaction1,
                        0,
                        1,
                        "speech",
                        utterance1,
                        "",
                        participant1,
                        None,
                    )
                ],
            )
            # chekc that other turn(s) with the same utterance are not affected
            # in accepted_one
            self.assertEqual(
                [i[:9] for i in test.get_turn(id=turn3_1)],
                [
                    (
                        turn3_1,
                        interaction3,
                        0,
                        1,
                        "speech",
                        utterance1,
                        "",
                        participant3,
                        None,
                    )
                ],
            )

        # Test if an exception is raised when the edited field does
        # not exist for the entity being edited
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                edit4 = test.submit_edit(
                    rcontent_id1, "name error", "room edit", player1
                )

        # Test if an exception is raised when a non-player is passed into
        # the player field
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                edit4 = test.submit_edit(
                    rcontent_id1, "name error", "room edit", player1 - 1
                )

        # Test if an exception is raised when the edit ID is not valid
        with self.assertRaises(Exception):
            with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
                test.view_edit(edit3 + 10)

    def test_search_db_no_fts(self):
        """
        Tests whether searching database returns entries that contain the search
        string and does not return entries that contain part of or none of the
        search string. Does not use FTS
        """
        # Test if searching for rooms works properly
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            base_room = test.create_base_room("room")[0]
            # test % wildcard in front of search string works
            room1 = test.create_room("small room", base_room, "tiny", "old")[0]
            # test % wildcard after search string works
            room2 = test.create_room("roomsmall", base_room, "tiny", "old")[0]
            # test % wildcard before and after search string works
            room3 = test.create_room("small room small", base_room, "tiny", "old")[0]
            # test that if the search string is not present exactly, the result
            # is not returned
            room4 = test.create_room("small oom", base_room, "tiny", "old")[0]
            # test that exact string is returned
            room5 = test.create_room(None, base_room, "tiny", "old")[0]
            # test that capitalization is ignored
            room6 = test.create_room("Room", base_room, "tiny", "old")[0]
            result = test.search_database("room", "room", fts=False)
            self.assertEqual(
                [i[:5] for i in result],
                [
                    (room1, "small room", base_room, "tiny", "old"),
                    (room2, "roomsmall", base_room, "tiny", "old"),
                    (room3, "small room small", base_room, "tiny", "old"),
                    (room5, "room", base_room, "tiny", "old"),
                    (room6, "Room", base_room, "tiny", "old"),
                ],
            )

        # Test if searching for characters works properly
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            base_char = test.create_base_character("char")[0]
            # test % wildcard in front of search string works
            char1 = test.create_character("small char", base_char, "tall", "young")[0]
            # test % wildcard after search string works
            char2 = test.create_character("charsmall", base_char, "tall", "young")[0]
            # test % wildcard before and after search string works
            char3 = test.create_character(
                "small char small", base_char, "tall", "young"
            )[0]
            # test that if the search string is not present exactly, the result
            # is not returned
            char4 = test.create_character("small har", base_char, "tall", "young")[0]
            # test that exact string is returned
            char5 = test.create_character(None, base_char, "tall", "young")[0]
            # test that capitalization is ignored
            char6 = test.create_character("Char", base_char, "tall", "young")[0]
            result = test.search_database("character", "char", fts=False)
            self.assertEqual(
                [i[:5] for i in result],
                [
                    (char1, "small char", base_char, "tall", "young"),
                    (char2, "charsmall", base_char, "tall", "young"),
                    (char3, "small char small", base_char, "tall", "young"),
                    (char5, "char", base_char, "tall", "young"),
                    (char6, "Char", base_char, "tall", "young"),
                ],
            )

        # Test if searching for objects works properly
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            base_obj = test.create_base_object("obj")[0]
            # test % wildcard in front of search string works
            obj1 = test.create_object(
                "small obj", base_obj, 0, 0, 0, 0, 0, 0, 0, "dusty"
            )[0]
            # test % wildcard after search string works
            obj2 = test.create_object(
                "objsmall", base_obj, 0, 0, 0, 0, 0, 0, 0, "dusty"
            )[0]
            # test % wildcard before and after search string works
            obj3 = test.create_object(
                "small obj small", base_obj, 0, 0, 0, 0, 0, 0, 0, "dusty"
            )[0]
            # test that if the search string is not present exactly, the result
            # is not returned
            obj4 = test.create_object(
                "small ob", base_obj, 0, 0, 0, 0, 0, 0, 0, "dusty"
            )[0]
            # test that exact string is returned
            obj5 = test.create_object(None, base_obj, 0, 0, 0, 0, 0, 0, 0, "dusty")[0]
            # test that capitalization is ignored
            obj6 = test.create_object("Obj", base_obj, 0, 0, 0, 0, 0, 0, 0, "dusty")[0]
            result = test.search_database("object", "obj", fts=False)
            self.assertEqual(
                [i[:11] for i in result],
                [
                    (obj1, "small obj", base_obj, 0, 0, 0, 0, 0, 0, 0, "dusty"),
                    (obj2, "objsmall", base_obj, 0, 0, 0, 0, 0, 0, 0, "dusty"),
                    (obj3, "small obj small", base_obj, 0, 0, 0, 0, 0, 0, 0, "dusty"),
                    (obj5, "obj", base_obj, 0, 0, 0, 0, 0, 0, 0, "dusty"),
                    (obj6, "Obj", base_obj, 0, 0, 0, 0, 0, 0, 0, "dusty"),
                ],
            )

    def test_fts_triggers(self):
        """
        Test if the triggers for FTS are working properly. Since all types of
        entities use the same format for triggers and it's done through a for
        loop, it's not necessary to check this for all entities. We will
        check base rooms and characters. Base rooms has one column in FTS and
        characters have multiple columns
        """
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            rbase_id = test.create_base_room("rooms")[0]
            self.assertEqual(
                [i[:2] for i in test.search_database("base room", "rooms")],
                [(rbase_id, "rooms")],
            )
            test.c.execute(
                """
                UPDATE base_rooms_table
                SET name = 'building'
                WHERE id = ?;
                """,
                (rbase_id,),
            )
            self.assertEqual(
                [i[:2] for i in test.search_database("base room", "rooms")], []
            )
            test.c.execute(
                """
                UPDATE base_rooms_table
                SET name = 'rooms'
                WHERE id = ?;
                """,
                (rbase_id,),
            )
            self.assertEqual(
                [i[:2] for i in test.search_database("base room", "rooms")],
                [(rbase_id, "rooms")],
            )
            test.c.execute(
                """
                DELETE FROM base_rooms_table
                WHERE id = ?;
                """,
                (rbase_id,),
            )
            self.assertEqual(
                [i[:2] for i in test.search_database("base room", "rooms")], []
            )

        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            cbase_id = test.create_base_character("person")[0]
            ccontent_id1 = test.create_character("police", cbase_id, "walking", "tall")[
                0
            ]
            ocontent_id2 = test.create_character(
                "tourist", cbase_id, "curious", "tired"
            )[0]
            self.assertEqual(
                [i[:5] for i in test.search_database("character", "tall")],
                [(ccontent_id1, "police", cbase_id, "walking", "tall")],
            )
            test.c.execute(
                """
                UPDATE characters_table
                SET physical_description = 'short'
                WHERE id = ?;
                """,
                (ccontent_id1,),
            )
            self.assertEqual(
                [i[:5] for i in test.search_database("character", "tall")], []
            )
            test.c.execute(
                """
                UPDATE characters_table
                SET physical_description = 'tall'
                WHERE id = ?;
                """,
                (ccontent_id1,),
            )
            self.assertEqual(
                [i[:5] for i in test.search_database("character", "tall")],
                [(ccontent_id1, "police", cbase_id, "walking", "tall")],
            )
            test.c.execute(
                """
                DELETE FROM characters_table
                WHERE id = ?;
                """,
                (ccontent_id1,),
            )
            self.assertEqual(
                [i[:5] for i in test.search_database("character", "tall")], []
            )

    def test_fts_search(self):
        """
        Test functionalities of full text search across database entities:
        ignore capitalizations, match against similar English language terms,
        search phrases, search prefixes.
        """
        # base room, test plural forms and capitalization
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            rbase_id = test.create_base_room("large hallways")[0]
            self.assertEqual(
                [i[:2] for i in test.search_database("base room", "HALlway")],
                [(rbase_id, "large hallways")],
            )

        # room, test phrases
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            rcontent_id1 = test.create_room("room1", rbase_id, "dirty", "old")[0]
            self.assertEqual(
                [i[:5] for i in test.search_database("room", "dirty old")],
                [(rcontent_id1, "room1", rbase_id, "dirty", "old")],
            )
            self.assertEqual(
                [i[:5] for i in test.search_database("room", "big dirty old")], []
            )

        # base character, test stemming
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            cbase_id = test.create_base_character("troll")[0]
            self.assertEqual(
                [i[:2] for i in test.search_database("base character", "trolling")],
                [(cbase_id, "troll")],
            )

        # character, test phrases
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            ccontent_id1 = test.create_character(
                "troll under the bridge", cbase_id, "Male", "Tall"
            )[0]
            self.assertEqual(
                [i[:5] for i in test.search_database("character", "tall troll")],
                [(ccontent_id1, "troll under the bridge", cbase_id, "Male", "Tall")],
            )

        # base object, test NOT keyword
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            obase_id = test.create_base_object("big room")[0]
            self.assertEqual(
                [i[:2] for i in test.search_database("base object", "big NOT room")], []
            )

        # object, test prefixes
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            ocontent_id1 = test.create_object(
                None, obase_id, 0.4, 0.2, 0, 0, 0, 0, 0, "big room"
            )[0]
            self.assertEqual(
                [i[:11] for i in test.search_database("object", "bi*")],
                [
                    (
                        ocontent_id1,
                        "big room",
                        obase_id,
                        0.4,
                        0.2,
                        0,
                        0,
                        0,
                        0,
                        0,
                        "big room",
                    )
                ],
            )

        # utterance, phrases
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            utterance1 = test.create_utterance("Hello this is a test")[0]
            self.assertEqual(
                [i[:2] for i in test.search_database("utterance", "test hello")],
                [(utterance1, "Hello this is a test")],
            )
            self.assertEqual(
                [i[:2] for i in test.search_database("utterance", "test hi")], []
            )

        # turn, phrases
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            interaction1 = test.create_interaction(rcontent_id1)[0]
            player1 = test.create_player()[0]
            participant1 = test.create_participant(interaction1, ccontent_id1, player1)[
                0
            ]
            turn1 = test.create_turn(
                interaction1, 1, 1, "action", None, "hit", participant1, participant1
            )[0]
            self.assertEqual(
                [i[:9] for i in test.search_database("turn", "hit action")],
                [
                    (
                        turn1,
                        interaction1,
                        1,
                        1,
                        "action",
                        None,
                        "hit",
                        participant1,
                        participant1,
                    )
                ],
            )

    def test_create_edges(self):
        """
        Tests whether the create_edges() returns the edges to be created given
        room, list of characters, and list of objects and successfully creates
        edges in the database when dry_run is False.
        """

        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            base_room = test.create_base_room("room")[0]
            room1 = test.create_room("room 1", base_room, "tiny", "old")[0]
            room2 = test.create_room("room 2", base_room, "tiny", "old")[0]
            room3 = test.create_room("room 3", base_room, "tiny", "old")[0]
            room4 = test.create_room("room 4", base_room, "tiny", "old")[0]
            baes_char = test.create_base_character("troll")[0]
            char1 = test.create_character(None, baes_char, "tall", "big")[0]
            char2 = test.create_character("troll2", baes_char, "short", "big")[0]
            base_obj = test.create_base_object("knife")[0]
            obj1 = test.create_object(None, base_obj, 0.4, 0.2, 0, 0, 0, 0, 0, "big")[0]
            # check that when dry_run = True, no changes are made but the returned
            # response is correct
            self.assertEqual(
                test.create_edges(
                    room1, [char1, char2], [obj1], [room2, room3, room4], True
                ),
                [
                    (room1, char2, "ex_contained", 0),
                    (room1, char1, "ex_contained", 0),
                    (room1, obj1, "ex_contained", 0),
                    (room1, room2, "neighbor", 1),
                    (room1, room3, "neighbor", 1),
                    (room1, room4, "neighbor", 1),
                ],
                "Edges are not correcly returned when dry_run = True",
            )
            self.assertEqual(test.get_id(type=DB_TYPE_EDGE), [])
            # check that when dry_run = False, changes are made and the returned
            # response is correct
            self.assertEqual(
                test.create_edges(
                    room1, [char1, char2], [obj1], [room2, room3, room4], False
                ),
                [
                    (room1, char2, "ex_contained", 0),
                    (room1, char1, "ex_contained", 0),
                    (room1, obj1, "ex_contained", 0),
                    (room1, room2, "neighbor", 1),
                    (room1, room3, "neighbor", 1),
                    (room1, room4, "neighbor", 1),
                ],
                "Edges are not correcly returned or edges are not successfully \
                created in the database when dry_run = False",
            )
            edges = test.get_id(type=DB_TYPE_EDGE, expand=True)
            edges_no_id = [i[1:] for i in edges]
            self.assertEqual(
                edges_no_id,
                [
                    (room1, char2, "ex_contained", 0),
                    (room1, char1, "ex_contained", 0),
                    (room1, obj1, "ex_contained", 0),
                    (room1, room2, "neighbor", 1),
                    (room1, room3, "neighbor", 1),
                    (room1, room4, "neighbor", 1),
                ],
            )
            # check whether the function works properly when one or more
            # lists are empty
            self.assertEqual(
                test.create_edges(room1, [], [obj1], [room2, room3, room4], True),
                [
                    (room1, obj1, "ex_contained", 0),
                    (room1, room2, "neighbor", 1),
                    (room1, room3, "neighbor", 1),
                    (room1, room4, "neighbor", 1),
                ],
                "Edges are not successfullly created when one or more lists \
                are empty",
            )

    def test_create_edges_entities_in_room_description(self):
        """
        Test that edges are marked as DB_EDGE_IN_CONTAINED when the name of the
        entity is contained in the room description.
        """
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            base_room = test.create_base_room("room")[0]
            classroom = test.create_room(
                "classroom",
                base_room,
                "The classroom contains several students and teachers. There is a giant podium near the entrance.",
                "old",
            )[0]
            room2 = test.create_room("room 2", base_room, "tiny", "old")[0]
            room3 = test.create_room("room 3", base_room, "tiny", "old")[0]
            room4 = test.create_room("room 4", base_room, "tiny", "old")[0]
            base_char = test.create_base_character("people")[0]
            teacher = test.create_character("teacher", base_char, "I teach", "older")[0]
            student = test.create_character(
                "student", base_char, "I go to school", "younger"
            )[0]
            priest = test.create_character(
                "priest", base_char, "I preach", "religious"
            )[0]
            base_obj1 = test.create_base_object("podium")[0]
            podium = test.create_object(
                None, base_obj1, 0.4, 0.2, 0, 0, 0, 0, 0, "big"
            )[0]
            base_obj2 = test.create_base_object("tree")[0]
            tree = test.create_object(None, base_obj2, 0.4, 0.2, 0, 0, 0, 0, 0, "big")[
                0
            ]
            self.assertEqual(
                test.create_edges(
                    classroom,
                    [teacher, student, priest],
                    [podium, tree],
                    [room2, room3, room4],
                    True,
                ),
                [
                    (classroom, teacher, DB_EDGE_IN_CONTAINED, 1),
                    (classroom, student, DB_EDGE_IN_CONTAINED, 1),
                    (classroom, podium, DB_EDGE_IN_CONTAINED, 1),
                    (classroom, priest, "ex_contained", 0),
                    (classroom, tree, "ex_contained", 0),
                    (classroom, room2, "neighbor", 1),
                    (classroom, room3, "neighbor", 1),
                    (classroom, room4, "neighbor", 1),
                ],
                "Edges are not correcly returned when dry_run = True",
            )
            # check that when dry_run = True, no changes are made to the
            # database
            self.assertEqual(test.get_id(type=DB_TYPE_EDGE), [])
            # check that when dry_run = False, changes are made and the returned
            # response is correct
            self.assertEqual(
                test.create_edges(
                    classroom,
                    [teacher, student, priest],
                    [podium, tree],
                    [room2, room3, room4],
                    False,
                ),
                [
                    (classroom, teacher, DB_EDGE_IN_CONTAINED, 1),
                    (classroom, student, DB_EDGE_IN_CONTAINED, 1),
                    (classroom, podium, DB_EDGE_IN_CONTAINED, 1),
                    (classroom, priest, "ex_contained", 0),
                    (classroom, tree, "ex_contained", 0),
                    (classroom, room2, "neighbor", 1),
                    (classroom, room3, "neighbor", 1),
                    (classroom, room4, "neighbor", 1),
                ],
                "Edges are not correcly returned or edges are not successfully \
                created in the database when dry_run = False",
            )
            edges = test.get_id(type=DB_TYPE_EDGE, expand=True)
            edges_no_id = [i[1:] for i in edges]
            self.assertEqual(
                edges_no_id,
                [
                    (classroom, teacher, DB_EDGE_IN_CONTAINED, 1),
                    (classroom, student, DB_EDGE_IN_CONTAINED, 1),
                    (classroom, podium, DB_EDGE_IN_CONTAINED, 1),
                    (classroom, priest, "ex_contained", 0),
                    (classroom, tree, "ex_contained", 0),
                    (classroom, room2, "neighbor", 1),
                    (classroom, room3, "neighbor", 1),
                    (classroom, room4, "neighbor", 1),
                ],
            )

    def test_create_edges_database_entities_in_room_description(self):
        """
        Test that edges are marked as DB_EDGE_IN_CONTAINED when the name of the
        entity is contained in the room description.
        """
        with LIGHTDatabase(os.path.join(self.data_dir, self.DB_NAME)) as test:
            base_room = test.create_base_room("room")[0]
            classroom = test.create_room(
                "classroom",
                base_room,
                "The classroom contains several students and teachers. There is a giant podium near the entrance.",
                "old",
            )[0]
            base_char = test.create_base_character("people")[0]
            teacher1 = test.create_character(
                "teacher", base_char, "I teach 1", "older"
            )[0]
            teacher2 = test.create_character(
                "teacher", base_char, "I teach 2", "older"
            )[0]
            teacher3 = test.create_character(
                "teacher", base_char, "I teach 3", "older"
            )[0]
            student = test.create_character(
                "student", base_char, "I go to school", "younger"
            )[0]
            priest = test.create_character(
                "priest", base_char, "I preach", "religious"
            )[0]
            base_obj1 = test.create_base_object("podium")[0]
            podium = test.create_object(
                None, base_obj1, 0.4, 0.2, 0, 0, 0, 0, 0, "big"
            )[0]
            base_obj2 = test.create_base_object("tree")[0]
            tree = test.create_object(None, base_obj2, 0.4, 0.2, 0, 0, 0, 0, 0, "big")[
                0
            ]
            self.assertIn(
                test.find_database_entities_in_rooms(classroom),
                (
                    [teacher1, student, podium],
                    [teacher2, student, podium],
                    [teacher3, student, podium],
                ),
            )
            # test that randomly selecting an entry when there are multiple with identical names works
            results = set()
            # statistically impossible to not cover all 3 cases after 200 trials
            for i in range(200):
                results.add(tuple(test.find_database_entities_in_rooms(classroom)))
            self.assertEqual(len(results), 3)


if __name__ == "__main__":
    unittest.main()
