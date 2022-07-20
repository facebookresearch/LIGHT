#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.abs

import unittest
import shutil, tempfile
from omegaconf import OmegaConf
import os
import json
import time
import sqlalchemy

from light.graph.structured_graph import OOGraph
from light.data_model.db.environment import (
    EnvDB,
    DBRoomInsideType,
    DBEdgeType,
    DBFlagTargetType,
    DBQuestTargetType,
    DBAgent,
    DBAgentName,
    DBObject,
    DBObjectName,
    DBRoom,
    DBRoomName,
    DBEdge,
    DBTextEdge,
    DBFlag,
    DBGraph,
    DBEdit,
    DBQuest,
)
from light.data_model.db.base import LightDBConfig, DBStatus, DBSplitType
from sqlalchemy.orm import Session


class TestEnvironmentDB(unittest.TestCase):
    """
    Unit tests for the LIGHT EnvDB.
    Builds simple test cases with standard inserts, but generally is a
    set of monolithic tests for each table in the EnvDB
    """

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.config = LightDBConfig(backend="test", file_root=self.data_dir)

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def set_up_some_nodes(self):
        # Create some test entries in the env DB
        opt = {"is_logging": True, "log_path": self.data_dir}
        test_graph = OOGraph(opt)
        agent_node = test_graph.add_agent("My test agent", {})
        room_node = test_graph.add_room("test room", {})
        agent_node.force_move_to(room_node)
        test_world = World({}, None, True)
        test_world.oo_graph = test_graph
        return (test_graph, test_world, agent_node, room_node)

    def test_initialize_env_db(self):
        """Ensure it's possible to initialize the db"""
        db = EnvDB(self.config)

    def test_create_load_inspect_agents(self):
        """Ensure it's possible to create and load agents"""
        # Create three agents, assert they have unique IDs but base_ids map
        db = EnvDB(self.config)
        BASE_NAME_1 = "king"
        BASE_NAME_2 = "queen"
        FULL_NAME_1 = "king of the orcs"
        FULL_NAME_2 = "king of the rats"
        FULL_NAME_3 = "queen of the land"

        # First agent should test mostly default values
        TEST_PERSONA_1 = "test_persona_1"
        TEST_DESC_1 = "test_desc_1"
        agent_1_id = db.create_agent_entry(
            name=FULL_NAME_1,
            base_name=BASE_NAME_1,
            persona=TEST_PERSONA_1,
            physical_description=TEST_DESC_1,
        )

        # Ensure id created is correct
        self.assertIsNotNone(agent_1_id)
        self.assertTrue(
            DBAgent.is_id(agent_1_id), f"Created ID {agent_1_id} not DBAgent ID"
        )
        self.assertFalse(
            DBObject.is_id(agent_1_id), f"Created ID {agent_1_id} passes as DBObject ID"
        )

        # Ensure agent created and matches defaults and provided
        agent_1 = db.get_agent(agent_1_id)
        base_id_1 = agent_1.base_id
        self.assertTrue(DBAgentName.is_id(base_id_1), "Base ID not correct format")
        self.assertEqual(
            agent_1.db_id, agent_1_id, "Marked db_id differs from initially returned id"
        )
        self.assertEqual(agent_1.persona, TEST_PERSONA_1)
        self.assertEqual(agent_1.name, FULL_NAME_1)
        self.assertEqual(agent_1.physical_description, TEST_DESC_1)
        self.assertEqual(agent_1.built_occurrences, 0)
        self.assertEqual(agent_1.name_prefix, "a")
        self.assertEqual(agent_1.status, DBStatus.REVIEW)
        self.assertIsNone(agent_1.charisma)
        self.assertIsNone(agent_1.constitution)
        self.assertIsNone(agent_1.strength)
        self.assertIsNone(agent_1.dexterity)
        self.assertIsNone(agent_1.intelligence)
        self.assertIsNone(agent_1.wisdom)
        self.assertIsNone(agent_1.is_plural)
        self.assertIsNone(agent_1.size)
        self.assertIsNone(agent_1.contain_size)
        self.assertIsNone(agent_1.creator_id)
        self.assertIsNotNone(agent_1.create_timestamp)

        # Ensure base agent created and matches values
        base_agent_1 = db.get_agent_name(db_id=agent_1.base_id)
        self.assertEqual(base_agent_1.name, BASE_NAME_1)
        self.assertEqual(base_agent_1.db_id, agent_1.base_id)
        self.assertEqual(base_agent_1.status, DBStatus.REVIEW)
        self.assertEqual(base_agent_1.split, DBSplitType.UNSET)

        # Ensure that the link exists between base and agent
        with Session(db.engine) as session:
            session.add(base_agent_1)
            self.assertEqual(
                len(base_agent_1.agents), 1, "Should have one linked agent"
            )
            session.expunge_all()

        # Should only be one agent
        self.assertEqual(len(db.find_agents()), 1)
        self.assertEqual(len(db.find_agent_names()), 1)

        # Duplicate create should fail
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            agent_1_id = db.create_agent_entry(
                name=FULL_NAME_1,
                base_name=BASE_NAME_1,
                persona=TEST_PERSONA_1,
                physical_description=TEST_DESC_1,
            )

        # Should only be one agent
        self.assertEqual(len(db.find_agents()), 1)
        self.assertEqual(len(db.find_agent_names()), 1)

        # Create a second agent sharing the first base class
        TEST_PERSONA_2 = "test_persona_2"
        TEST_DESC_2 = "test_desc_2"
        agent_2_id = db.create_agent_entry(
            name=FULL_NAME_2,
            base_name=BASE_NAME_1,
            persona=TEST_PERSONA_2,
            physical_description=TEST_DESC_2,
        )

        # Ensure agent exists now, and that the base class is correct
        agent_2 = db.get_agent(agent_2_id)
        self.assertEqual(
            agent_2.db_id, agent_2_id, "Marked db_id differs from initially returned id"
        )
        self.assertEqual(agent_2.persona, TEST_PERSONA_2)
        self.assertEqual(agent_2.name, FULL_NAME_2)
        self.assertEqual(agent_2.physical_description, TEST_DESC_2)
        self.assertEqual(agent_2.base_id, agent_2.base_id)

        # Ensure only one base class, but two agents
        self.assertEqual(len(db.find_agents()), 2)
        self.assertEqual(len(db.find_agent_names()), 1)

        # Create a third agent, with all custom attributes
        TEST_PERSONA_3 = "test_persona_3"
        TEST_DESC_3 = "test_desc_3"
        agent_3_id = db.create_agent_entry(
            name=FULL_NAME_3,
            base_name=BASE_NAME_2,
            persona=TEST_PERSONA_3,
            physical_description=TEST_DESC_3,
            name_prefix="hello",
            status=DBStatus.ACCEPTED,
            charisma=1,
            constitution=2,
            strength=3,
            dexterity=4,
            intelligence=5,
            wisdom=6,
            is_plural=True,
            size=7,
            contain_size=8,
            creator_id="test",
        )

        # Ensure id created is correct
        self.assertIsNotNone(agent_3_id)
        self.assertTrue(
            DBAgent.is_id(agent_3_id), f"Created ID {agent_3_id} not DBAgent ID"
        )
        self.assertFalse(
            DBObject.is_id(agent_3_id), f"Created ID {agent_3_id} passes as DBObject ID"
        )

        # Ensure that the custom attributes all work
        agent_3 = db.get_agent(agent_3_id)
        base_id_3 = agent_3.base_id
        self.assertNotEqual(base_id_3, base_id_1)
        self.assertTrue(DBAgentName.is_id(base_id_3), "Base ID not correct format")
        self.assertEqual(
            agent_3.db_id, agent_3_id, "Marked db_id differs from initially returned id"
        )
        self.assertEqual(agent_3.persona, TEST_PERSONA_3)
        self.assertEqual(agent_3.name, FULL_NAME_3)
        self.assertEqual(agent_3.physical_description, TEST_DESC_3)
        self.assertEqual(agent_3.built_occurrences, 0)
        self.assertEqual(agent_3.name_prefix, "hello")
        self.assertEqual(agent_3.status, DBStatus.ACCEPTED)
        self.assertEqual(agent_3.charisma, 1)
        self.assertEqual(agent_3.constitution, 2)
        self.assertEqual(agent_3.strength, 3)
        self.assertEqual(agent_3.dexterity, 4)
        self.assertEqual(agent_3.intelligence, 5)
        self.assertEqual(agent_3.wisdom, 6)
        self.assertTrue(agent_3.is_plural)
        self.assertEqual(agent_3.size, 7)
        self.assertEqual(agent_3.contain_size, 8)
        self.assertEqual(agent_3.creator_id, "test")
        self.assertIsNotNone(agent_3.create_timestamp)

        # Ensure base agent created and matches values
        base_agent_2 = db.get_agent_name(db_id=agent_3.base_id)
        self.assertEqual(base_agent_2.name, BASE_NAME_2)
        self.assertEqual(base_agent_2.db_id, agent_3.base_id)
        self.assertEqual(base_agent_2.status, DBStatus.REVIEW)
        self.assertEqual(base_agent_2.split, DBSplitType.UNSET)

        # Ensure two base classes, and three agents
        self.assertEqual(len(db.find_agents()), 3)
        self.assertEqual(len(db.find_agent_names()), 2)

        base_agent_1 = db.get_agent_name(db_id=agent_1.base_id)
        # Ensure the base classes properly link to the agents
        with Session(db.engine) as session:
            session.add(base_agent_1)
            self.assertEqual(
                len(base_agent_1.agents), 2, "Base 1 Should have two linked agents"
            )
            session.add(base_agent_2)
            self.assertEqual(
                len(base_agent_2.agents), 1, "Base 2 Should have one linked agent"
            )
            session.expunge_all()

        # Ensure that all agents base names are present when in session
        with Session(db.engine) as session:
            session.add(agent_1)
            session.add(agent_2)
            session.add(agent_3)
            self.assertEqual(agent_1.base_name.name, agent_2.base_name.name)
            self.assertNotEqual(agent_1.base_name.name, agent_3.base_name.name)

        # assert that getting agent names fail on all invalid cases
        with self.assertRaises(AssertionError):
            base_agent_1 = db.get_agent_name(db_id="FAK-fake")
        with self.assertRaises(KeyError):
            base_agent_1 = db.get_agent_name(db_id="AGN-fake")
        with self.assertRaises(KeyError):
            base_agent_1 = db.get_agent_name(name="fake")
        with self.assertRaises(KeyError):
            base_agent_1 = db.get_agent_name(
                db_id=agent_1.base_id, status=DBStatus.ACCEPTED
            )
        with self.assertRaises(KeyError):
            base_agent_1 = db.get_agent_name(
                db_id=agent_1.base_id, split=DBSplitType.TRAIN
            )

        # Advanced agent name searches
        matched_status = db.find_agent_names(status=DBStatus.REVIEW)
        self.assertEqual(len(matched_status), 2)
        unmatched_status = db.find_agent_names(status=DBStatus.ACCEPTED)
        self.assertEqual(len(unmatched_status), 0)
        matched_split = db.find_agent_names(split=DBSplitType.UNSET)
        self.assertEqual(len(matched_split), 2)
        unmatched_split = db.find_agent_names(split=DBSplitType.TRAIN)
        self.assertEqual(len(unmatched_split), 0)
        name_exact_match = db.find_agent_names(name=BASE_NAME_1)
        self.assertEqual(len(name_exact_match), 1)
        name_partial_match_1 = db.find_agent_names(name="qu")
        self.assertEqual(len(name_partial_match_1), 1)
        name_partial_match_2 = db.find_agent_names(name="n")
        self.assertEqual(len(name_partial_match_2), 2)
        name_no_match = db.find_agent_names(name="zzz")
        self.assertEqual(len(name_no_match), 0)

        # Advanced agent searches
        base_id_match_0 = db.find_agents(base_id="AGN-fake")
        self.assertEqual(len(base_id_match_0), 0)
        base_id_match_1 = db.find_agents(base_id=base_agent_2.db_id)
        self.assertEqual(len(base_id_match_1), 1)
        base_id_match_2 = db.find_agents(base_id=base_agent_1.db_id)
        self.assertEqual(len(base_id_match_2), 2)
        name_exact_match = db.find_agents(name=FULL_NAME_1)
        self.assertEqual(len(name_exact_match), 1)
        name_match_0 = db.find_agents(name="zzzzz")
        self.assertEqual(len(name_match_0), 0)
        name_match_1 = db.find_agents(name="orcs")
        self.assertEqual(len(name_match_1), 1)
        name_match_2 = db.find_agents(name="king")
        self.assertEqual(len(name_match_2), 2)
        persona_exact_match = db.find_agents(persona=TEST_PERSONA_3)
        self.assertEqual(len(persona_exact_match), 1)
        persona_match_0 = db.find_agents(persona="zzz")
        self.assertEqual(len(persona_match_0), 0)
        persona_match_1 = db.find_agents(persona="3")
        self.assertEqual(len(persona_match_1), 1)
        persona_match_3 = db.find_agents(persona="test")
        self.assertEqual(len(persona_match_3), 3)
        description_exact_match = db.find_agents(physical_description=TEST_DESC_1)
        self.assertEqual(len(description_exact_match), 1)
        description_match_0 = db.find_agents(physical_description="zzz")
        self.assertEqual(len(description_match_0), 0)
        description_match_1 = db.find_agents(physical_description="3")
        self.assertEqual(len(description_match_1), 1)
        description_match_3 = db.find_agents(physical_description="test")
        self.assertEqual(len(description_match_3), 3)
        name_prefix_match_0 = db.find_agents(name_prefix="test")
        self.assertEqual(len(name_prefix_match_0), 0)
        name_prefix_match_1 = db.find_agents(name_prefix="hello")
        self.assertEqual(len(name_prefix_match_1), 1)
        name_prefix_match_2 = db.find_agents(name_prefix="a")
        self.assertEqual(len(name_prefix_match_2), 2)
        is_plural_match_0 = db.find_agents(is_plural=False)
        self.assertEqual(len(is_plural_match_0), 0)
        is_plural_match_1 = db.find_agents(is_plural=True)
        self.assertEqual(len(is_plural_match_1), 1)
        status_match_0 = db.find_agents(status=DBStatus.QUESTIONABLE)
        self.assertEqual(len(status_match_0), 0)
        status_match_1 = db.find_agents(status=DBStatus.ACCEPTED)
        self.assertEqual(len(status_match_1), 1)
        status_match_2 = db.find_agents(status=DBStatus.REVIEW)
        self.assertEqual(len(status_match_2), 2)
        split_match_0 = db.find_agents(split=DBSplitType.UNSEEN)
        self.assertEqual(len(split_match_0), 0)
        split_match_3 = db.find_agents(split=DBSplitType.UNSET)
        self.assertEqual(len(split_match_3), 3)
        creator_id_match_0 = db.find_agents(creator_id="fake")
        self.assertEqual(len(creator_id_match_0), 0)
        creator_id_match_1 = db.find_agents(creator_id="test")
        self.assertEqual(len(creator_id_match_1), 1)

    def test_create_load_inspect_rooms(self):
        """Ensure it's possible to create and load rooms"""
        # Create three rooms, assert they have unique IDs but base_ids map
        db = EnvDB(self.config)
        BASE_NAME_1 = "bedroom"
        BASE_NAME_2 = "forest"
        FULL_NAME_1 = "master bedroom"
        FULL_NAME_2 = "dingy bedroom"
        FULL_NAME_3 = "fairy forest"

        # First room should test mostly default values
        TEST_STORY_1 = "test_story_1"
        TEST_DESC_1 = "test_desc_1"
        room_1_id = db.create_room_entry(
            name=FULL_NAME_1,
            base_name=BASE_NAME_1,
            description=TEST_DESC_1,
            backstory=TEST_STORY_1,
        )

        # Ensure id created is correct
        self.assertIsNotNone(room_1_id)
        self.assertTrue(
            DBRoom.is_id(room_1_id), f"Created ID {room_1_id} not DBRoom ID"
        )
        self.assertFalse(
            DBObject.is_id(room_1_id), f"Created ID {room_1_id} passes as DBObject ID"
        )

        # Ensure room created and matches defaults and provided
        room_1 = db.get_room(room_1_id)
        base_id_1 = room_1.base_id
        print(room_1, room_1.__dict__)
        self.assertTrue(DBRoomName.is_id(base_id_1), "Base ID not correct format")
        self.assertEqual(
            room_1.db_id, room_1_id, "Marked db_id differs from initially returned id"
        )
        self.assertEqual(room_1.name, FULL_NAME_1)
        self.assertEqual(room_1.description, TEST_DESC_1)
        self.assertEqual(room_1.backstory, TEST_STORY_1)
        self.assertEqual(room_1.built_occurrences, 0)
        self.assertEqual(room_1.status, DBStatus.REVIEW)
        self.assertIsNone(room_1.rarity)
        self.assertEqual(room_1.indoor_status, DBRoomInsideType.UNKNOWN)
        self.assertIsNone(room_1.size)
        self.assertIsNone(room_1.creator_id)
        self.assertIsNotNone(room_1.create_timestamp)

        # Ensure base room created and matches values
        base_room_1 = db.get_room_name(db_id=room_1.base_id)
        self.assertEqual(base_room_1.name, BASE_NAME_1)
        self.assertEqual(base_room_1.db_id, room_1.base_id)
        self.assertEqual(base_room_1.status, DBStatus.REVIEW)
        self.assertEqual(base_room_1.split, DBSplitType.UNSET)

        # Ensure that the link exists between base and room
        with Session(db.engine) as session:
            session.add(base_room_1)
            self.assertEqual(len(base_room_1.rooms), 1, "Should have one linked room")
            session.expunge_all()

        # Should only be one room
        self.assertEqual(len(db.find_rooms()), 1)
        self.assertEqual(len(db.find_room_names()), 1)

        # Duplicate create should fail
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            room_1_id = db.create_room_entry(
                name=FULL_NAME_1,
                base_name=BASE_NAME_1,
                description=TEST_DESC_1,
                backstory=TEST_STORY_1,
            )

        # Should only be one room
        self.assertEqual(len(db.find_rooms()), 1)
        self.assertEqual(len(db.find_room_names()), 1)

        # Create a second room sharing the first base class
        TEST_STORY_2 = "test_story_2"
        TEST_DESC_2 = "test_desc_2"
        room_2_id = db.create_room_entry(
            name=FULL_NAME_2,
            base_name=BASE_NAME_1,
            description=TEST_DESC_2,
            backstory=TEST_STORY_2,
        )

        # Ensure room exists now, and that the base class is correct
        room_2 = db.get_room(room_2_id)
        self.assertEqual(
            room_2.db_id, room_2_id, "Marked db_id differs from initially returned id"
        )
        self.assertEqual(room_2.name, FULL_NAME_2)
        self.assertEqual(room_2.description, TEST_DESC_2)
        self.assertEqual(room_2.backstory, TEST_STORY_2)
        self.assertEqual(room_2.base_id, room_2.base_id)
        self.assertEqual(room_2.indoor_status, DBRoomInsideType.UNKNOWN)

        # Ensure only one base class, but two rooms
        self.assertEqual(len(db.find_rooms()), 2)
        self.assertEqual(len(db.find_room_names()), 1)

        # Create a third room, with all custom attributes
        TEST_STORY_3 = "test_story_3"
        TEST_DESC_3 = "test_desc_3"
        room_3_id = db.create_room_entry(
            name=FULL_NAME_3,
            base_name=BASE_NAME_2,
            description=TEST_DESC_3,
            backstory=TEST_STORY_3,
            indoor_status=DBRoomInsideType.OUTSIDE,
            rarity=1,
            size=2,
            status=DBStatus.ACCEPTED,
            creator_id="test",
        )

        # Ensure id created is correct
        self.assertIsNotNone(room_3_id)
        self.assertTrue(
            DBRoom.is_id(room_3_id), f"Created ID {room_3_id} not DBRoom ID"
        )
        self.assertFalse(
            DBObject.is_id(room_3_id), f"Created ID {room_3_id} passes as DBObject ID"
        )

        # Ensure that the custom attributes all work
        room_3 = db.get_room(room_3_id)
        base_id_3 = room_3.base_id
        self.assertNotEqual(base_id_3, base_id_1)
        self.assertTrue(DBRoomName.is_id(base_id_3), "Base ID not correct format")
        self.assertEqual(
            room_3.db_id, room_3_id, "Marked db_id differs from initially returned id"
        )
        self.assertEqual(room_3.name, FULL_NAME_3)
        self.assertEqual(room_3.description, TEST_DESC_3)
        self.assertEqual(room_3.backstory, TEST_STORY_3)
        self.assertEqual(room_3.built_occurrences, 0)
        self.assertEqual(room_3.status, DBStatus.ACCEPTED)
        self.assertEqual(room_3.rarity, 1)
        self.assertEqual(room_3.size, 2)
        self.assertEqual(room_3.indoor_status, DBRoomInsideType.OUTSIDE)
        self.assertEqual(room_3.creator_id, "test")
        self.assertIsNotNone(room_3.create_timestamp)

        # Ensure base room created and matches values
        base_room_2 = db.get_room_name(db_id=room_3.base_id)
        self.assertEqual(base_room_2.name, BASE_NAME_2)
        self.assertEqual(base_room_2.db_id, room_3.base_id)
        self.assertEqual(base_room_2.status, DBStatus.REVIEW)
        self.assertEqual(base_room_2.split, DBSplitType.UNSET)

        # Ensure two base classes, and three rooms
        self.assertEqual(len(db.find_rooms()), 3)
        self.assertEqual(len(db.find_room_names()), 2)

        base_room_1 = db.get_room_name(db_id=room_1.base_id)
        # Ensure the base classes properly link to the rooms
        with Session(db.engine) as session:
            session.add(base_room_1)
            self.assertEqual(
                len(base_room_1.rooms), 2, "Base 1 Should have two linked rooms"
            )
            session.add(base_room_2)
            self.assertEqual(
                len(base_room_2.rooms), 1, "Base 2 Should have one linked room"
            )
            session.expunge_all()

        # Ensure that all rooms base names are present when in session
        with Session(db.engine) as session:
            session.add(room_1)
            session.add(room_2)
            session.add(room_3)
            self.assertEqual(room_1.base_name.name, room_2.base_name.name)
            self.assertNotEqual(room_1.base_name.name, room_3.base_name.name)

        # assert that getting room names fail on all invalid cases
        with self.assertRaises(AssertionError):
            base_room_1 = db.get_room_name(db_id="FAK-fake")
        with self.assertRaises(KeyError):
            base_room_1 = db.get_room_name(db_id="RMN-fake")
        with self.assertRaises(KeyError):
            base_room_1 = db.get_room_name(name="fake")
        with self.assertRaises(KeyError):
            base_room_1 = db.get_room_name(
                db_id=room_1.base_id, status=DBStatus.ACCEPTED
            )
        with self.assertRaises(KeyError):
            base_room_1 = db.get_room_name(
                db_id=room_1.base_id, split=DBSplitType.TRAIN
            )

        # Advanced room name searches
        matched_status = db.find_room_names(status=DBStatus.REVIEW)
        self.assertEqual(len(matched_status), 2)
        unmatched_status = db.find_room_names(status=DBStatus.ACCEPTED)
        self.assertEqual(len(unmatched_status), 0)
        matched_split = db.find_room_names(split=DBSplitType.UNSET)
        self.assertEqual(len(matched_split), 2)
        unmatched_split = db.find_room_names(split=DBSplitType.TRAIN)
        self.assertEqual(len(unmatched_split), 0)
        name_exact_match = db.find_room_names(name=BASE_NAME_1)
        self.assertEqual(len(name_exact_match), 1)
        name_partial_match_1 = db.find_room_names(name="bed")
        self.assertEqual(len(name_partial_match_1), 1)
        name_partial_match_2 = db.find_room_names(name="r")
        self.assertEqual(len(name_partial_match_2), 2)
        name_no_match = db.find_room_names(name="zzz")
        self.assertEqual(len(name_no_match), 0)

        # Advanced room searches
        base_id_match_0 = db.find_rooms(base_id="AGN-fake")
        self.assertEqual(len(base_id_match_0), 0)
        base_id_match_1 = db.find_rooms(base_id=base_room_2.db_id)
        self.assertEqual(len(base_id_match_1), 1)
        base_id_match_2 = db.find_rooms(base_id=base_room_1.db_id)
        self.assertEqual(len(base_id_match_2), 2)
        name_exact_match = db.find_rooms(name=FULL_NAME_1)
        self.assertEqual(len(name_exact_match), 1)
        name_match_0 = db.find_rooms(name="zzzzz")
        self.assertEqual(len(name_match_0), 0)
        name_match_1 = db.find_rooms(name="dingy")
        self.assertEqual(len(name_match_1), 1)
        name_match_2 = db.find_rooms(name="bed")
        self.assertEqual(len(name_match_2), 2)
        backstory_exact_match = db.find_rooms(backstory=TEST_STORY_3)
        self.assertEqual(len(backstory_exact_match), 1)
        backstory_match_0 = db.find_rooms(backstory="zzz")
        self.assertEqual(len(backstory_match_0), 0)
        backstory_match_1 = db.find_rooms(backstory="3")
        self.assertEqual(len(backstory_match_1), 1)
        backstory_match_3 = db.find_rooms(backstory="test")
        self.assertEqual(len(backstory_match_3), 3)
        description_exact_match = db.find_rooms(description=TEST_DESC_1)
        self.assertEqual(len(description_exact_match), 1)
        description_match_0 = db.find_rooms(description="zzz")
        self.assertEqual(len(description_match_0), 0)
        description_match_1 = db.find_rooms(description="3")
        self.assertEqual(len(description_match_1), 1)
        description_match_3 = db.find_rooms(description="test")
        self.assertEqual(len(description_match_3), 3)
        status_match_0 = db.find_rooms(status=DBStatus.QUESTIONABLE)
        self.assertEqual(len(status_match_0), 0)
        status_match_1 = db.find_rooms(status=DBStatus.ACCEPTED)
        self.assertEqual(len(status_match_1), 1)
        status_match_2 = db.find_rooms(status=DBStatus.REVIEW)
        self.assertEqual(len(status_match_2), 2)
        split_match_0 = db.find_rooms(split=DBSplitType.UNSEEN)
        self.assertEqual(len(split_match_0), 0)
        split_match_3 = db.find_rooms(split=DBSplitType.UNSET)
        self.assertEqual(len(split_match_3), 3)
        indoor_status_match_0 = db.find_rooms(indoor_status=DBRoomInsideType.MULTI_ROOM)
        self.assertEqual(len(indoor_status_match_0), 0)
        indoor_status_match_1 = db.find_rooms(indoor_status=DBRoomInsideType.OUTSIDE)
        self.assertEqual(len(indoor_status_match_1), 1)
        indoor_status_match_2 = db.find_rooms(indoor_status=DBRoomInsideType.UNKNOWN)
        self.assertEqual(len(indoor_status_match_2), 2)
        creator_id_match_0 = db.find_rooms(creator_id="fake")
        self.assertEqual(len(creator_id_match_0), 0)
        creator_id_match_1 = db.find_rooms(creator_id="test")
        self.assertEqual(len(creator_id_match_1), 1)

    def test_create_load_inspect_objects(self):
        """Ensure it's possible to create and load objects"""
        # Create three objects, assert they have unique IDs but base_ids map
        db = EnvDB(self.config)
        BASE_NAME_1 = "ball"
        BASE_NAME_2 = "shovel"
        FULL_NAME_1 = "red ball"
        FULL_NAME_2 = "metal ball"
        FULL_NAME_3 = "garden shovel"

        # First object should test mostly default values
        TEST_DESC_1 = "test_desc_1"
        object_1_id = db.create_object_entry(
            name=FULL_NAME_1,
            base_name=BASE_NAME_1,
            physical_description=TEST_DESC_1,
            is_container=0,
            is_drink=0,
            is_food=0,
            is_gettable=1,
            is_surface=0,
            is_wearable=0,
            is_weapon=0,
        )

        # Ensure id created is correct
        self.assertIsNotNone(object_1_id)
        self.assertTrue(
            DBObject.is_id(object_1_id), f"Created ID {object_1_id} not DBObject ID"
        )
        self.assertFalse(
            DBRoom.is_id(object_1_id), f"Created ID {object_1_id} passes as DBRoom ID"
        )

        # Ensure object created and matches defaults and provided
        object_1 = db.get_object(object_1_id)
        base_id_1 = object_1.base_id
        self.assertTrue(DBObjectName.is_id(base_id_1), "Base ID not correct format")
        self.assertEqual(
            object_1.db_id,
            object_1_id,
            "Marked db_id differs from initially returned id",
        )
        self.assertEqual(object_1.name, FULL_NAME_1)
        self.assertEqual(object_1.physical_description, TEST_DESC_1)
        self.assertEqual(object_1.is_container, 0)
        self.assertEqual(object_1.is_drink, 0)
        self.assertEqual(object_1.is_food, 0)
        self.assertEqual(object_1.is_gettable, 1)
        self.assertEqual(object_1.is_surface, 0)
        self.assertEqual(object_1.is_wearable, 0)
        self.assertEqual(object_1.is_weapon, 0)
        self.assertEqual(object_1.built_occurrences, 0)
        self.assertEqual(object_1.name_prefix, "a")
        self.assertEqual(object_1.status, DBStatus.REVIEW)
        self.assertIsNone(object_1.is_plural)
        self.assertIsNone(object_1.size)
        self.assertIsNone(object_1.contain_size)
        self.assertIsNone(object_1.value)
        self.assertIsNone(object_1.rarity)
        self.assertIsNone(object_1.creator_id)
        self.assertIsNotNone(object_1.create_timestamp)

        # Ensure base object created and matches values
        base_object_1 = db.get_object_name(db_id=object_1.base_id)
        self.assertEqual(base_object_1.name, BASE_NAME_1)
        self.assertEqual(base_object_1.db_id, object_1.base_id)
        self.assertEqual(base_object_1.status, DBStatus.REVIEW)
        self.assertEqual(base_object_1.split, DBSplitType.UNSET)

        # Ensure that the link exists between base and object
        with Session(db.engine) as session:
            session.add(base_object_1)
            self.assertEqual(
                len(base_object_1.objects), 1, "Should have one linked object"
            )
            session.expunge_all()

        # Should only be one object
        self.assertEqual(len(db.find_objects()), 1)
        self.assertEqual(len(db.find_object_names()), 1)

        # Duplicate create should fail
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            object_1_id = db.create_object_entry(
                name=FULL_NAME_1,
                base_name=BASE_NAME_1,
                physical_description=TEST_DESC_1,
                is_container=0,
                is_drink=0,
                is_food=0,
                is_gettable=1,
                is_surface=0,
                is_wearable=0,
                is_weapon=0,
            )

        # Should only be one object
        self.assertEqual(len(db.find_objects()), 1)
        self.assertEqual(len(db.find_object_names()), 1)

        # Create a second object sharing the first base class
        TEST_DESC_2 = "test_desc_2"
        object_2_id = db.create_object_entry(
            name=FULL_NAME_2,
            base_name=BASE_NAME_1,
            physical_description=TEST_DESC_2,
            is_container=0,
            is_drink=0,
            is_food=0,
            is_gettable=1,
            is_surface=0,
            is_wearable=0,
            is_weapon=0,
        )

        # Ensure object exists now, and that the base class is correct
        object_2 = db.get_object(object_2_id)
        self.assertEqual(
            object_2.db_id,
            object_2_id,
            "Marked db_id differs from initially returned id",
        )
        self.assertEqual(object_2.name, FULL_NAME_2)
        self.assertEqual(object_2.physical_description, TEST_DESC_2)
        self.assertEqual(object_2.base_id, object_2.base_id)

        # Ensure only one base class, but two objects
        self.assertEqual(len(db.find_objects()), 2)
        self.assertEqual(len(db.find_object_names()), 1)

        # Create a third object, with all custom attributes
        TEST_DESC_3 = "test_desc_3"
        object_3_id = db.create_object_entry(
            name=FULL_NAME_3,
            base_name=BASE_NAME_2,
            physical_description=TEST_DESC_3,
            is_container=0,
            is_drink=0,
            is_food=0,
            is_gettable=1,
            is_surface=0,
            is_wearable=0,
            is_weapon=0,
            name_prefix="hello",
            is_plural=True,
            size=1,
            contain_size=2,
            value=3,
            rarity=4,
            status=DBStatus.ACCEPTED,
            creator_id="test",
        )

        # Ensure id created is correct
        self.assertIsNotNone(object_3_id)
        self.assertTrue(
            DBObject.is_id(object_3_id), f"Created ID {object_3_id} not DBObject ID"
        )
        self.assertFalse(
            DBRoom.is_id(object_3_id), f"Created ID {object_3_id} passes as DBRoom ID"
        )

        # Ensure that the custom attributes all work
        object_3 = db.get_object(object_3_id)
        base_id_3 = object_3.base_id
        self.assertNotEqual(base_id_3, base_id_1)
        self.assertTrue(DBObjectName.is_id(base_id_3), "Base ID not correct format")
        self.assertEqual(
            object_3.db_id,
            object_3_id,
            "Marked db_id differs from initially returned id",
        )
        self.assertEqual(object_3.name, FULL_NAME_3)
        self.assertEqual(object_3.physical_description, TEST_DESC_3)
        self.assertEqual(object_3.built_occurrences, 0)
        self.assertEqual(object_3.is_container, 0)
        self.assertEqual(object_3.is_drink, 0)
        self.assertEqual(object_3.is_food, 0)
        self.assertEqual(object_3.is_gettable, 1)
        self.assertEqual(object_3.is_surface, 0)
        self.assertEqual(object_3.is_wearable, 0)
        self.assertEqual(object_3.is_weapon, 0)
        self.assertEqual(object_3.built_occurrences, 0)
        self.assertEqual(object_3.name_prefix, "hello")
        self.assertEqual(object_3.status, DBStatus.ACCEPTED)
        self.assertEqual(object_3.is_plural, True)
        self.assertEqual(object_3.size, 1)
        self.assertEqual(object_3.contain_size, 2)
        self.assertEqual(object_3.value, 3)
        self.assertEqual(object_3.rarity, 4)
        self.assertEqual(object_3.creator_id, "test")
        self.assertIsNotNone(object_3.create_timestamp)

        # Ensure base object created and matches values
        base_object_2 = db.get_object_name(db_id=object_3.base_id)
        self.assertEqual(base_object_2.name, BASE_NAME_2)
        self.assertEqual(base_object_2.db_id, object_3.base_id)
        self.assertEqual(base_object_2.status, DBStatus.REVIEW)
        self.assertEqual(base_object_2.split, DBSplitType.UNSET)

        # Ensure two base classes, and three objects
        self.assertEqual(len(db.find_objects()), 3)
        self.assertEqual(len(db.find_object_names()), 2)

        base_object_1 = db.get_object_name(db_id=object_1.base_id)
        # Ensure the base classes properly link to the objects
        with Session(db.engine) as session:
            session.add(base_object_1)
            self.assertEqual(
                len(base_object_1.objects), 2, "Base 1 Should have two linked objects"
            )
            session.add(base_object_2)
            self.assertEqual(
                len(base_object_2.objects), 1, "Base 2 Should have one linked object"
            )
            session.expunge_all()

        # Ensure that all objects base names are present when in session
        with Session(db.engine) as session:
            session.add(object_1)
            session.add(object_2)
            session.add(object_3)
            self.assertEqual(object_1.base_name.name, object_2.base_name.name)
            self.assertNotEqual(object_1.base_name.name, object_3.base_name.name)

        # assert that getting object names fail on all invalid cases
        with self.assertRaises(AssertionError):
            base_object_1 = db.get_object_name(db_id="FAK-fake")
        with self.assertRaises(KeyError):
            base_object_1 = db.get_object_name(db_id="OBN-fake")
        with self.assertRaises(KeyError):
            base_object_1 = db.get_object_name(name="fake")
        with self.assertRaises(KeyError):
            base_object_1 = db.get_object_name(
                db_id=object_1.base_id, status=DBStatus.ACCEPTED
            )
        with self.assertRaises(KeyError):
            base_object_1 = db.get_object_name(
                db_id=object_1.base_id, split=DBSplitType.TRAIN
            )

        # Advanced object name searches
        matched_status = db.find_object_names(status=DBStatus.REVIEW)
        self.assertEqual(len(matched_status), 2)
        unmatched_status = db.find_object_names(status=DBStatus.ACCEPTED)
        self.assertEqual(len(unmatched_status), 0)
        matched_split = db.find_object_names(split=DBSplitType.UNSET)
        self.assertEqual(len(matched_split), 2)
        unmatched_split = db.find_object_names(split=DBSplitType.TRAIN)
        self.assertEqual(len(unmatched_split), 0)
        name_exact_match = db.find_object_names(name=BASE_NAME_1)
        self.assertEqual(len(name_exact_match), 1)
        name_partial_match_1 = db.find_object_names(name="vel")
        self.assertEqual(len(name_partial_match_1), 1)
        name_partial_match_2 = db.find_object_names(name="l")
        self.assertEqual(len(name_partial_match_2), 2)
        name_no_match = db.find_object_names(name="zzz")
        self.assertEqual(len(name_no_match), 0)

        # Advanced object searches
        base_id_match_0 = db.find_objects(base_id="OBN-fake")
        self.assertEqual(len(base_id_match_0), 0)
        base_id_match_1 = db.find_objects(base_id=base_object_2.db_id)
        self.assertEqual(len(base_id_match_1), 1)
        base_id_match_2 = db.find_objects(base_id=base_object_1.db_id)
        self.assertEqual(len(base_id_match_2), 2)
        name_exact_match = db.find_objects(name=FULL_NAME_1)
        self.assertEqual(len(name_exact_match), 1)
        name_match_0 = db.find_objects(name="zzzzz")
        self.assertEqual(len(name_match_0), 0)
        name_match_1 = db.find_objects(name="metal")
        self.assertEqual(len(name_match_1), 1)
        name_match_2 = db.find_objects(name="ball")
        self.assertEqual(len(name_match_2), 2)
        description_exact_match = db.find_objects(physical_description=TEST_DESC_1)
        self.assertEqual(len(description_exact_match), 1)
        description_match_0 = db.find_objects(physical_description="zzz")
        self.assertEqual(len(description_match_0), 0)
        description_match_1 = db.find_objects(physical_description="3")
        self.assertEqual(len(description_match_1), 1)
        description_match_3 = db.find_objects(physical_description="test")
        self.assertEqual(len(description_match_3), 3)
        name_prefix_match_0 = db.find_objects(name_prefix="test")
        self.assertEqual(len(name_prefix_match_0), 0)
        name_prefix_match_1 = db.find_objects(name_prefix="hello")
        self.assertEqual(len(name_prefix_match_1), 1)
        name_prefix_match_2 = db.find_objects(name_prefix="a")
        self.assertEqual(len(name_prefix_match_2), 2)
        is_plural_match_0 = db.find_objects(is_plural=False)
        self.assertEqual(len(is_plural_match_0), 0)
        is_plural_match_1 = db.find_objects(is_plural=True)
        self.assertEqual(len(is_plural_match_1), 1)
        status_match_0 = db.find_objects(status=DBStatus.QUESTIONABLE)
        self.assertEqual(len(status_match_0), 0)
        status_match_1 = db.find_objects(status=DBStatus.ACCEPTED)
        self.assertEqual(len(status_match_1), 1)
        status_match_2 = db.find_objects(status=DBStatus.REVIEW)
        self.assertEqual(len(status_match_2), 2)
        split_match_0 = db.find_objects(split=DBSplitType.UNSEEN)
        self.assertEqual(len(split_match_0), 0)
        split_match_3 = db.find_objects(split=DBSplitType.UNSET)
        self.assertEqual(len(split_match_3), 3)
        creator_id_match_0 = db.find_objects(creator_id="fake")
        self.assertEqual(len(creator_id_match_0), 0)
        creator_id_match_1 = db.find_objects(creator_id="test")
        self.assertEqual(len(creator_id_match_1), 1)
        is_container_match_0 = db.find_objects(is_container=True)
        self.assertEqual(len(is_container_match_0), 0)
        is_container_match_3 = db.find_objects(is_container=False)
        self.assertEqual(len(is_container_match_3), 3)
        is_drink_match_0 = db.find_objects(is_drink=True)
        self.assertEqual(len(is_drink_match_0), 0)
        is_drink_match_3 = db.find_objects(is_drink=False)
        self.assertEqual(len(is_drink_match_3), 3)
        is_food_match_0 = db.find_objects(is_food=True)
        self.assertEqual(len(is_food_match_0), 0)
        is_food_match_3 = db.find_objects(is_food=False)
        self.assertEqual(len(is_food_match_3), 3)
        is_gettable_match_0 = db.find_objects(is_gettable=False)
        self.assertEqual(len(is_gettable_match_0), 0)
        is_gettable_match_3 = db.find_objects(is_gettable=True)
        self.assertEqual(len(is_gettable_match_3), 3)
        is_surface_match_0 = db.find_objects(is_surface=True)
        self.assertEqual(len(is_surface_match_0), 0)
        is_surface_match_3 = db.find_objects(is_surface=False)
        self.assertEqual(len(is_surface_match_3), 3)
        is_wearable_match_0 = db.find_objects(is_wearable=True)
        self.assertEqual(len(is_wearable_match_0), 0)
        is_wearable_match_3 = db.find_objects(is_wearable=False)
        self.assertEqual(len(is_wearable_match_3), 3)
        is_weapon_match_0 = db.find_objects(is_weapon=True)
        self.assertEqual(len(is_weapon_match_0), 0)
        is_weapon_match_3 = db.find_objects(is_weapon=False)
        self.assertEqual(len(is_weapon_match_3), 3)

    def test_create_load_edges(self):
        """Ensure it's possible to create edges, and load them from DBElems"""

    def test_create_load_flags(self):
        """Ensure it's possible to create and load flags"""

    def test_arbitrary_attributes(self):
        """Ensure the arbitrary attributes are created properly"""

    def test_create_load_edits(self):
        """Ensure it's possible to create, load, and reject edits"""

    def test_create_load_link_quests(self):
        """Ensure that quests are saving and loading as expected"""

    def test_create_load_graphs(self):
        """Ensure that graph loading is functioning as expected"""

    def test_initialize_env_db_cache(self):
        """Ensure it's possible to load everything to the cache"""
        db = EnvDB(self.config)
        # self.set_up_some_nodes()
        # self.set_up_some_edges()
