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

    def test_create_load_inspect_rooms(self):
        """Ensure it's possible to create and load rooms"""

    def test_create_load_inspect_objects(self):
        """Ensure it's possible to create and load objects"""

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
