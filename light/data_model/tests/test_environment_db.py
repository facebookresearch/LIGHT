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
    DBNodeAttribute,
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
    HasDBIDMixin,
)
from typing import List
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

    def set_up_some_nodes(self, db: EnvDB):
        # Create some test entries in the env DB
        agent_ids: List[str] = []
        room_ids: List[str] = []
        object_ids: List[str] = []
        for x in range(5):
            agent_ids.append(
                db.create_agent_entry(
                    name=f"test_agent_{x}",
                    base_name="agent",
                    persona="agent_persona",
                    physical_description="agent_description",
                )
            )
            room_ids.append(
                db.create_room_entry(
                    name=f"test_room_{x}",
                    base_name="room",
                    description="room_description",
                    backstory="room_backstory",
                )
            )
            object_ids.append(
                db.create_object_entry(
                    name=f"test_object_{x}",
                    base_name="object",
                    physical_description="object_description",
                    is_container=0,
                    is_drink=0,
                    is_food=0,
                    is_gettable=1,
                    is_surface=0,
                    is_wearable=0,
                    is_weapon=0,
                )
            )
        return agent_ids, room_ids, object_ids

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
        FULL_NAME_2 = "elder king of the rats"
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
        self.assertEqual(agent_2.name_prefix, "an")

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
        name_prefix_match_a = db.find_agents(name_prefix="a")
        self.assertEqual(len(name_prefix_match_a), 1)
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
        FULL_NAME_1 = "azure ball"
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
        self.assertEqual(object_1.name_prefix, "an")
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
        self.assertEqual(object_2.name_prefix, "a")

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
        name_prefix_match_a = db.find_objects(name_prefix="a")
        self.assertEqual(len(name_prefix_match_a), 1)
        name_prefix_match_an = db.find_objects(name_prefix="an")
        self.assertEqual(len(name_prefix_match_an), 1)
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
        db = EnvDB(self.config)

        # get some things to use
        agent_ids, room_ids, object_ids = self.set_up_some_nodes(db)
        agent_1_id = agent_ids[0]
        agent_2_id = agent_ids[1]
        agent_3_id = agent_ids[2]
        object_1_id = object_ids[0]
        object_2_id = object_ids[1]
        object_3_id = object_ids[2]
        room_1_id = room_ids[0]
        room_2_id = room_ids[1]

        # Create first edge
        edge_1_id = db.create_edge(
            parent_id=room_1_id,
            child_id=agent_1_id,
            edge_type=DBEdgeType.CONTAINS,
        )
        self.assertTrue(DBEdge.is_id(edge_1_id))

        # Ensure edge exists correctly
        edges = db.get_edges()
        self.assertEqual(len(edges), 1)
        edge_1 = edges[0]
        self.assertEqual(edge_1.db_id, edge_1_id)
        self.assertEqual(edge_1.parent_id, room_1_id)
        self.assertEqual(edge_1.child_id, agent_1_id)
        self.assertEqual(edge_1.built_occurrences, 0)
        self.assertEqual(edge_1.edge_type, DBEdgeType.CONTAINS)
        self.assertEqual(edge_1.status, DBStatus.REVIEW)
        self.assertEqual(edge_1.edge_label, "")
        self.assertIsNone(edge_1.creator_id)
        self.assertIsNotNone(edge_1.create_timestamp)

        # Note no duplicate edge possible
        edge_1_id_2 = db.create_edge(
            parent_id=room_1_id,
            child_id=agent_1_id,
            edge_type=DBEdgeType.CONTAINS,
        )
        self.assertEqual(edge_1_id, edge_1_id_2)
        edges = db.get_edges()
        self.assertEqual(len(edges), 1)
        edge_1 = edges[0]

        # Try expanding edge
        with self.assertRaises(AssertionError):
            _test_child = edge_1.child()
        edge_1.expand_edge(db)
        self.assertIsInstance(edge_1.child, DBAgent)
        self.assertEqual(edge_1.child.db_id, agent_1_id)

        # Create more edges
        edge_2_id = db.create_edge(
            parent_id=room_1_id,
            child_id=agent_2_id,
            edge_type=DBEdgeType.CONTAINS,
        )
        edge_3_id = db.create_edge(
            parent_id=room_1_id,
            child_id=agent_3_id,
            edge_type=DBEdgeType.MAY_CONTAIN,
        )
        edge_4_id = db.create_edge(
            parent_id=agent_1_id,
            child_id=object_2_id,
            edge_type=DBEdgeType.CONTAINS,
        )
        edge_5_id = db.create_edge(
            parent_id=agent_1_id,
            child_id=object_3_id,
            edge_type=DBEdgeType.WEARING,
        )
        edge_6_id = db.create_edge(
            parent_id=room_1_id,
            child_id=object_1_id,
            edge_type=DBEdgeType.MAY_CONTAIN,
        )
        edge_7_id = db.create_edge(
            parent_id=agent_3_id,
            child_id=object_3_id,
            edge_type=DBEdgeType.MAY_WEAR,
        )
        edge_8_id = db.create_edge(
            parent_id=agent_2_id,
            child_id=object_3_id,
            edge_type=DBEdgeType.WIELDING,
        )
        edge_9_id = db.create_edge(
            parent_id=agent_3_id,
            child_id=object_1_id,
            edge_type=DBEdgeType.MAY_WIELD,
            status=DBStatus.REJECTED,
        )
        edge_10_id = db.create_edge(
            parent_id=room_1_id,
            child_id=room_2_id,
            edge_type=DBEdgeType.NEIGHBOR,
            edge_label="a path to",
        )
        edge_11_id = db.create_edge(
            parent_id=room_2_id,
            child_id=room_1_id,
            edge_type=DBEdgeType.MAY_BE_NEIGHBOR,
            creator_id="test",
        )
        edge_12_id = db.create_edge(
            parent_id=object_1_id,
            child_id=object_2_id,
            edge_type=DBEdgeType.MAY_CONTAIN,
        )

        # Try expanding other edges
        edge_2 = db.get_edges(parent_id=room_1_id, child_id=room_2_id)[0]
        edge_2.expand_edge(db)
        self.assertIsInstance(edge_2.child, DBRoom)
        self.assertEqual(edge_2.child.db_id, room_2_id)
        edge_3 = db.get_edges(parent_id=room_1_id, child_id=object_1_id)[0]
        edge_3.expand_edge(db)
        self.assertIsInstance(edge_3.child, DBObject)
        self.assertEqual(edge_3.child.db_id, object_1_id)

        # Query the edges
        edges = db.get_edges()
        self.assertEqual(len(edges), 12)
        no_matching_pair = db.get_edges(parent_id=room_1_id, child_id=object_3_id)
        self.assertEqual(len(no_matching_pair), 0)
        no_matching_type = db.get_edges(
            parent_id=room_1_id,
            child_id=object_1_id,
            edge_type=DBEdgeType.MAY_BE_NEIGHBOR,
        )
        self.assertEqual(len(no_matching_type), 0)
        room_1_edges = db.get_edges(parent_id=room_1_id)
        self.assertEqual(len(room_1_edges), 5)
        agent_1_edges = db.get_edges(parent_id=agent_1_id)
        self.assertEqual(len(agent_1_edges), 2)
        object_1_edges = db.get_edges(parent_id=object_1_id)
        self.assertEqual(len(object_1_edges), 1)
        neighbor_edges = db.get_edges(edge_type=DBEdgeType.NEIGHBOR)
        self.assertEqual(len(neighbor_edges), 1)
        contains_edges = db.get_edges(edge_type=DBEdgeType.CONTAINS)
        self.assertEqual(len(contains_edges), 3)
        matching_edge_label = db.get_edges(edge_label="")
        self.assertEqual(len(matching_edge_label), 11)
        special_edge_label = db.get_edges(edge_label="a path to")
        self.assertEqual(len(special_edge_label), 1)
        no_matching_edge_label = db.get_edges(edge_label="zzzzzz")
        self.assertEqual(len(no_matching_edge_label), 0)
        matching_status = db.get_edges(status=DBStatus.REVIEW)
        self.assertEqual(len(matching_status), 11)
        special_matching_status = db.get_edges(status=DBStatus.REJECTED)
        self.assertEqual(len(special_matching_status), 1)
        no_matching_status = db.get_edges(status=DBStatus.ACCEPTED)
        self.assertEqual(len(no_matching_status), 0)

        # Test edge strength filtering
        room_1 = db.get_room(room_1_id)
        edge_2 = db.get_edges(parent_id=room_1_id, child_id=agent_2_id)[0]
        with Session(db.engine) as session:
            session.add(room_1)
            session.add(edge_1)
            session.add(edge_2)
            room_1.built_occurrences = 3
            edge_1.built_occurrences = 1
            edge_2.built_occurrences = 2
            session.flush()
            session.commit()
            session.expunge_all()
        more_than_quarter = db.get_edges(min_strength=0.25)
        self.assertEqual(len(more_than_quarter), 2)
        more_than_half = db.get_edges(min_strength=0.5)
        self.assertEqual(len(more_than_half), 1)
        more_than_top = db.get_edges(min_strength=0.75)
        self.assertEqual(len(more_than_top), 0)

        # Create first text edge
        text_edge_1_id = db.create_text_edge(
            parent_id=room_1_id,
            child_text="unknown object",
            edge_type=DBEdgeType.MAY_CONTAIN,
        )
        self.assertTrue(DBTextEdge.is_id(text_edge_1_id))

        # Ensure edge exists correctly
        text_edges = db.get_text_edges()
        self.assertEqual(len(text_edges), 1)
        text_edge_1 = text_edges[0]
        self.assertEqual(text_edge_1.db_id, text_edge_1_id)
        self.assertEqual(text_edge_1.parent_id, room_1_id)
        self.assertEqual(text_edge_1.child_text, "unknown object")
        self.assertEqual(text_edge_1.edge_type, DBEdgeType.MAY_CONTAIN)
        self.assertEqual(text_edge_1.status, DBStatus.REVIEW)
        self.assertEqual(text_edge_1.edge_label, "")
        self.assertIsNone(text_edge_1.creator_id)
        self.assertIsNotNone(text_edge_1.create_timestamp)

        # Note no duplicate edge possible
        text_edge_1_id_2 = db.create_text_edge(
            parent_id=room_1_id,
            child_text="unknown object",
            edge_type=DBEdgeType.MAY_CONTAIN,
        )
        self.assertEqual(text_edge_1_id, text_edge_1_id_2)
        text_edges = db.get_text_edges()
        self.assertEqual(len(text_edges), 1)

        # More text edges
        text_edge_2_id = db.create_text_edge(
            parent_id=agent_1_id,
            child_text="unknown room",
            edge_type=DBEdgeType.MAY_BE_CONTAINED_IN,
        )
        text_edge_3_id = db.create_text_edge(
            parent_id=object_1_id,
            child_text="unknown agent",
            edge_type=DBEdgeType.CONTAINED_IN,
        )
        text_edge_4_id = db.create_text_edge(
            parent_id=room_1_id,
            child_text="unknown room",
            edge_type=DBEdgeType.MAY_BE_NEIGHBOR,
            edge_label="a path to",
            creator_id="test",
            status=DBStatus.ACCEPTED,
        )

        # Query text edges
        text_edges = db.get_text_edges()
        self.assertEqual(len(text_edges), 4)
        text_no_matching_pair = db.get_text_edges(
            parent_id=object_1_id, child_text="unknown room"
        )
        self.assertEqual(len(text_no_matching_pair), 0)
        text_no_matching_parent = db.get_text_edges(parent_id=agent_2_id)
        self.assertEqual(len(text_no_matching_parent), 0)
        text_no_matching_child = db.get_text_edges(child_text="something random")
        self.assertEqual(len(text_no_matching_child), 0)
        text_matching_child = db.get_text_edges(child_text="unknown room")
        self.assertEqual(len(text_matching_child), 2)
        text_matching_parent = db.get_text_edges(parent_id=room_1_id)
        self.assertEqual(len(text_matching_parent), 2)
        text_matching_type = db.get_text_edges(edge_type=DBEdgeType.CONTAINED_IN)
        self.assertEqual(len(text_matching_type), 1)
        text_no_matching_type = db.get_text_edges(edge_type=DBEdgeType.NEIGHBOR)
        self.assertEqual(len(text_no_matching_type), 0)
        text_matching_status = db.get_text_edges(status=DBStatus.REVIEW)
        self.assertEqual(len(text_matching_status), 3)
        text_special_status = db.get_text_edges(status=DBStatus.ACCEPTED)
        self.assertEqual(len(text_special_status), 1)
        text_no_matching_status = db.get_text_edges(status=DBStatus.REJECTED)
        self.assertEqual(len(text_no_matching_status), 0)
        text_matching_label = db.get_text_edges(edge_label="")
        self.assertEqual(len(text_matching_label), 3)
        text_special_label = db.get_text_edges(edge_label="a path to")
        self.assertEqual(len(text_special_label), 1)
        text_no_matching_label = db.get_text_edges(edge_label="zzzzzz")
        self.assertEqual(len(text_no_matching_label), 0)

        # Query edges for DBElems
        room_1 = db.get_room(room_1_id)
        agent_1 = db.get_agent(agent_1_id)
        agent_2 = db.get_agent(agent_2_id)
        object_1 = db.get_object(object_1_id)

        # Try expanding edge
        # All edges fail when not loading first
        with self.assertRaises(AssertionError):
            _test_text_edges = room_1.text_edges
        with self.assertRaises(AssertionError):
            _test_text_edges = agent_1.text_edges
        with self.assertRaises(AssertionError):
            _test_text_edges = agent_2.text_edges
        with self.assertRaises(AssertionError):
            _test_text_edges = object_1.text_edges
        with self.assertRaises(AssertionError):
            _test_node_edges = room_1.node_edges
        with self.assertRaises(AssertionError):
            _test_node_edges = agent_1.node_edges
        with self.assertRaises(AssertionError):
            _test_node_edges = agent_2.node_edges
        with self.assertRaises(AssertionError):
            _test_node_edges = object_1.node_edges

        room_1.load_edges(db)
        agent_1.load_edges(db)
        agent_2.load_edges(db)
        object_1.load_edges(db)

        text_edges = db.get_text_edges()
        self.assertEqual(len(text_edges), 4)

        self.assertEqual(len(room_1.node_edges), 5)
        self.assertEqual(len(room_1.text_edges), 2)
        self.assertEqual(len(agent_1.node_edges), 2)
        self.assertEqual(len(agent_1.text_edges), 1)
        self.assertEqual(len(agent_2.node_edges), 1)
        self.assertEqual(len(agent_2.text_edges), 0)
        self.assertEqual(len(object_1.node_edges), 1)
        self.assertEqual(len(object_1.text_edges), 1)

        # Ensure that each of the edges is valid
        for node in [room_1, agent_1, agent_2, object_1]:
            for node_edge in node.node_edges:
                self.assertEqual(node_edge.child.db_id, node_edge.child_id)
            for text_edge in node.text_edges:
                self.assertIsNotNone(text_edge.child_text)

        # Try creating the cache and reloading from that state
        db.create_node_cache()

        # Query edges for DBElems
        room_1 = db.get_room(room_1_id)
        agent_1 = db.get_agent(agent_1_id)
        agent_2 = db.get_agent(agent_2_id)
        object_1 = db.get_object(object_1_id)

        # Cached edges can be directly accessed
        self.assertEqual(len(room_1.node_edges), 5)
        self.assertEqual(len(room_1.text_edges), 2)
        self.assertEqual(len(agent_1.node_edges), 2)
        self.assertEqual(len(agent_1.text_edges), 1)
        self.assertEqual(len(agent_2.node_edges), 1)
        self.assertEqual(len(agent_2.text_edges), 0)
        self.assertEqual(len(object_1.node_edges), 1)
        self.assertEqual(len(object_1.text_edges), 1)

        # Ensure that each of the edges is valid
        for node in [room_1, agent_1, agent_2, object_1]:
            for node_edge in node.node_edges:
                self.assertEqual(node_edge.child.db_id, node_edge.child_id)
            for text_edge in node.text_edges:
                self.assertIsNotNone(text_edge.child_text)

    def test_arbitrary_attributes(self):
        """Ensure the arbitrary attributes are created properly"""
        db = EnvDB(self.config)

        # get some things to use
        agent_ids, room_ids, object_ids = self.set_up_some_nodes(db)
        agent_1_id = agent_ids[0]
        object_1_id = object_ids[0]
        room_1_id = room_ids[0]

        # create first attribute
        attribute_1_id = db.create_arbitrary_attribute(
            target_id=agent_1_id,
            attribute_name="tested",
            attribute_value_string="true",
        )

        self.assertTrue(DBNodeAttribute.is_id(attribute_1_id))
        attributes = db.get_attributes(target_id=agent_1_id)
        self.assertEqual(len(attributes), 1)
        attribute_1 = attributes[0]

        # Make sure it looks right
        self.assertEqual(attribute_1.db_id, attribute_1_id)
        self.assertEqual(attribute_1.target_id, agent_1_id)
        self.assertEqual(attribute_1.attribute_name, "tested")
        self.assertEqual(attribute_1.attribute_value_string, "true")
        self.assertEqual(attribute_1.status, DBStatus.REVIEW)
        self.assertIsNone(attribute_1.creator_id, agent_1_id)

        # Ensure we can't duplicate
        attribute_1_id_2 = db.create_arbitrary_attribute(
            target_id=agent_1_id,
            attribute_name="tested",
            attribute_value_string="true",
        )
        self.assertEqual(attribute_1_id, attribute_1_id_2)
        attributes = db.get_attributes(target_id=agent_1_id)
        self.assertEqual(len(attributes), 1)

        # Create more of them
        attribute_2_id = db.create_arbitrary_attribute(
            target_id=object_1_id,
            attribute_name="tested",
            attribute_value_string="true",
        )
        attribute_3_id = db.create_arbitrary_attribute(
            target_id=room_1_id,
            attribute_name="tested",
            attribute_value_string="true",
            status=DBStatus.ACCEPTED,
            creator_id="test",
        )
        attribute_4_id = db.create_arbitrary_attribute(
            target_id=agent_1_id,
            attribute_name="tried",
            attribute_value_string="false",
        )
        attributes = db.get_attributes()
        self.assertEqual(len(attributes), 4)

        # Query for arbitrary attributes
        target_matches = db.get_attributes(target_id=agent_1_id)
        self.assertEqual(len(target_matches), 2)
        target_no_match = db.get_attributes(target_id="RME-fake")
        self.assertEqual(len(target_no_match), 0)
        attribute_match_3 = db.get_attributes(attribute_name="tested")
        self.assertEqual(len(attribute_match_3), 3)
        attribute_match_1 = db.get_attributes(attribute_name="tried")
        self.assertEqual(len(attribute_match_1), 1)
        attribute_match_0 = db.get_attributes(attribute_name="zzzzz")
        self.assertEqual(len(attribute_match_0), 0)
        value_match_3 = db.get_attributes(attribute_value_string="true")
        self.assertEqual(len(value_match_3), 3)
        value_match_1 = db.get_attributes(attribute_value_string="false")
        self.assertEqual(len(value_match_1), 1)
        value_match_0 = db.get_attributes(attribute_value_string="zzzzz")
        self.assertEqual(len(value_match_0), 0)
        status_match_3 = db.get_attributes(status=DBStatus.REVIEW)
        self.assertEqual(len(status_match_3), 3)
        status_match_1 = db.get_attributes(status=DBStatus.ACCEPTED)
        self.assertEqual(len(status_match_1), 1)
        status_match_0 = db.get_attributes(status=DBStatus.REJECTED)
        self.assertEqual(len(status_match_0), 0)
        creator_match_1 = db.get_attributes(creator_id="test")
        self.assertEqual(len(creator_match_1), 1)
        creator_match_0 = db.get_attributes(creator_id="zzzz")
        self.assertEqual(len(creator_match_0), 0)

        # see if we can load the attributes from the elem
        room_1 = db.get_room(room_1_id)
        agent_1 = db.get_agent(agent_1_id)
        object_1 = db.get_object(object_1_id)

        # Try expanding attributes
        # All attributes fail when not loading first
        with self.assertRaises(AssertionError):
            _test_attributes = room_1.attributes
        with self.assertRaises(AssertionError):
            _test_attributes = agent_1.attributes
        with self.assertRaises(AssertionError):
            _test_attributes = object_1.attributes

        room_1.load_attributes(db)
        agent_1.load_attributes(db)
        object_1.load_attributes(db)

        self.assertEqual(len(room_1.attributes), 1)
        self.assertEqual(len(agent_1.attributes), 2)
        self.assertEqual(len(object_1.attributes), 1)

        # Ensure that each of the attributes is valid
        for node in [room_1, agent_1, object_1]:
            for attribute in node.attributes:
                self.assertIsNotNone(attribute.attribute_value_string)
                self.assertEqual(attribute.target_id, node.db_id)

        # Try creating the cache and reloading from that state
        db.create_node_cache()

        # Query edges for DBElems
        room_1 = db.get_room(room_1_id)
        agent_1 = db.get_agent(agent_1_id)
        object_1 = db.get_object(object_1_id)

        # Cached attributes should load no problem
        self.assertEqual(len(room_1.attributes), 1)
        self.assertEqual(len(agent_1.attributes), 2)
        self.assertEqual(len(object_1.attributes), 1)

        # Ensure that each of the attributes is valid
        for node in [room_1, agent_1, object_1]:
            for attribute in node.attributes:
                self.assertIsNotNone(attribute.attribute_value_string)
                self.assertEqual(attribute.target_id, node.db_id)

    def test_create_load_edits(self):
        """Ensure it's possible to create, load, and reject edits"""
        db = EnvDB(self.config)

        # get some things to use
        agent_ids, room_ids, object_ids = self.set_up_some_nodes(db)
        agent_1_id = agent_ids[0]

        # Create an edit
        edit_1_id = db.create_edit(
            editor_id="test_editor",
            node_id=agent_1_id,
            field="persona",
            old_value="agent_persona",
            new_value="edited_agent_persona",
        )
        self.assertTrue(DBEdit.is_id(edit_1_id))

        # load the edit
        edits = db.get_edits()
        self.assertEqual(len(edits), 1)
        edit_1 = edits[0]

        # Assert fields are set
        self.assertEqual(edit_1.db_id, edit_1_id)
        self.assertEqual(edit_1.editor_id, "test_editor")
        self.assertEqual(edit_1.node_id, agent_1_id)
        self.assertEqual(edit_1.field, "persona")
        self.assertEqual(edit_1.old_value, "agent_persona")
        self.assertEqual(edit_1.new_value, "edited_agent_persona")
        self.assertEqual(edit_1.status, DBStatus.REVIEW)
        self.assertIsNotNone(edit_1.create_timestamp)

        # reject the edit
        edit_1.reject_edit(db)
        edits = db.get_edits()
        self.assertEqual(len(edits), 1)
        edit_1 = edits[0]
        self.assertEqual(edit_1.status, DBStatus.REJECTED)

        # create two more edits
        edit_2_id = db.create_edit(
            editor_id="test_editor",
            node_id=agent_1_id,
            field="name",
            old_value="test_agent_1",
            new_value="test_agent_0",
            status=DBStatus.QUESTIONABLE,
        )
        edit_3_id = db.create_edit(
            editor_id="test_editor_2",
            node_id=agent_1_id,
            field="persona",
            old_value="agent_persona",
            new_value="edited_agent_persona_2",
        )
        edits = db.get_edits()
        self.assertEqual(len(edits), 3)

        # query the various edits
        match_editor_2 = db.get_edits(editor_id="test_editor")
        self.assertEqual(len(match_editor_2), 2)
        match_editor_1 = db.get_edits(editor_id="test_editor_2")
        self.assertEqual(len(match_editor_1), 1)
        match_editor_0 = db.get_edits(editor_id="test_editor_3")
        self.assertEqual(len(match_editor_0), 0)
        match_node_id_3 = db.get_edits(node_id=agent_1_id)
        self.assertEqual(len(match_node_id_3), 3)
        match_node_id_0 = db.get_edits(node_id="test")
        self.assertEqual(len(match_node_id_0), 0)
        match_field_2 = db.get_edits(field="persona")
        self.assertEqual(len(match_field_2), 2)
        match_field_1 = db.get_edits(field="name")
        self.assertEqual(len(match_field_1), 1)
        match_field_0 = db.get_edits(field="physical_description")
        self.assertEqual(len(match_field_0), 0)
        match_old_value_2 = db.get_edits(old_value="agent_persona")
        self.assertEqual(len(match_old_value_2), 2)
        match_old_value_1 = db.get_edits(old_value="test_agent_1")
        self.assertEqual(len(match_old_value_1), 1)
        match_old_value_0 = db.get_edits(old_value="zzzzz")
        self.assertEqual(len(match_old_value_0), 0)
        match_new_value = db.get_edits(new_value="test_agent_0")
        self.assertEqual(len(match_new_value), 1)
        no_match_new_value = db.get_edits(new_value="zzzzz")
        self.assertEqual(len(no_match_new_value), 0)
        match_status_standard = db.get_edits(status=DBStatus.REVIEW)
        self.assertEqual(len(match_status_standard), 1)
        match_status_reject = db.get_edits(status=DBStatus.REJECTED)
        self.assertEqual(len(match_status_reject), 1)
        match_status_special = db.get_edits(status=DBStatus.QUESTIONABLE)
        self.assertEqual(len(match_status_special), 1)
        match_status_0 = db.get_edits(status=DBStatus.ACCEPTED)
        self.assertEqual(len(match_status_0), 0)

        # TODO accept an edit

    def test_create_load_flags(self):
        """Ensure it's possible to create and load flags"""
        db = EnvDB(self.config)

        # get some things to use
        agent_ids, room_ids, object_ids = self.set_up_some_nodes(db)
        agent_1_id = agent_ids[0]

        # Create a flag
        flag_1_id = db.flag_entry(
            user_id="flagger_id",
            flag_type=DBFlagTargetType.FLAG_USER,
            target_id="bad_user",
            reason="some_reason",
        )
        self.assertTrue(DBFlag.is_id(flag_1_id))

        # load the flag
        flags = db.get_flags()
        self.assertEqual(len(flags), 1)
        flag_1 = flags[0]
        self.assertEqual(flag_1.db_id, flag_1_id)
        self.assertEqual(flag_1.user_id, "flagger_id")
        self.assertEqual(flag_1.flag_type, DBFlagTargetType.FLAG_USER)
        self.assertEqual(flag_1.target_id, "bad_user")
        self.assertEqual(flag_1.reason, "some_reason")
        self.assertEqual(flag_1.status, DBStatus.REVIEW)
        self.assertIsNotNone(flag_1.create_timestamp)

        # create two more flags
        flag_2_id = db.flag_entry(
            user_id="flagger_id",
            flag_type=DBFlagTargetType.FLAG_ENVIRONMENT,
            target_id=agent_ids[0],
            reason="some_other_reason",
        )
        flag_3_id = db.flag_entry(
            user_id="flagger_id",
            flag_type=DBFlagTargetType.FLAG_UTTERANCE,
            target_id="model_id",
            reason="some_reason",
            status=DBStatus.ACCEPTED,
        )
        flags = db.get_flags()
        self.assertEqual(len(flags), 3)

        # query the various flags
        match_user = db.get_flags(user_id="flagger_id")
        self.assertEqual(len(match_user), 3)
        no_match_user = db.get_flags(user_id="random_id")
        self.assertEqual(len(no_match_user), 0)
        match_type_env = db.get_flags(flag_type=DBFlagTargetType.FLAG_ENVIRONMENT)
        self.assertEqual(len(match_type_env), 1)
        match_type_utt = db.get_flags(flag_type=DBFlagTargetType.FLAG_UTTERANCE)
        self.assertEqual(len(match_type_utt), 1)
        match_type_user = db.get_flags(flag_type=DBFlagTargetType.FLAG_USER)
        self.assertEqual(len(match_type_user), 1)
        match_target = db.get_flags(target_id=agent_ids[0])
        self.assertEqual(len(match_target), 1)
        no_match_target = db.get_flags(target_id=agent_ids[1])
        self.assertEqual(len(no_match_target), 0)
        match_reason = db.get_flags(reason="some_reason")
        self.assertEqual(len(match_reason), 2)
        no_match_reason = db.get_flags(reason="fake_reason")
        self.assertEqual(len(no_match_reason), 0)
        match_status = db.get_flags(status=DBStatus.REVIEW)
        self.assertEqual(len(match_status), 2)
        match_other_status = db.get_flags(status=DBStatus.ACCEPTED)
        self.assertEqual(len(match_other_status), 1)
        no_match_status = db.get_flags(status=DBStatus.QUESTIONABLE)
        self.assertEqual(len(no_match_status), 0)

    def test_create_load_link_quests(self):
        """Ensure that quests are saving and loading as expected"""
        db = EnvDB(self.config)

        # get some things to use
        agent_ids, room_ids, object_ids = self.set_up_some_nodes(db)

        # Create first quest
        quest_1_id = db.create_quest(
            agent_id=agent_ids[0],
            text_motivation="top_text_motivation",
            target_type=DBQuestTargetType.TEXT_ONLY,
            target="",
        )
        self.assertTrue(DBQuest.is_id(quest_1_id))

        # Ensure init looks good
        quests = db.find_quests()
        self.assertEqual(len(quests), 1)
        quest_1 = quests[0]
        self.assertEqual(quest_1.db_id, quest_1_id)
        self.assertEqual(quest_1.agent_id, agent_ids[0])
        self.assertEqual(quest_1.text_motivation, "top_text_motivation")
        self.assertEqual(quest_1.target_type, DBQuestTargetType.TEXT_ONLY)
        self.assertEqual(quest_1.target, "")
        self.assertEqual(quest_1.status, DBStatus.REVIEW)
        self.assertEqual(quest_1.position, 0)
        self.assertIsNone(quest_1.parent_id)
        self.assertIsNone(quest_1.origin_filepath)
        self.assertIsNone(quest_1.creator_id)
        self.assertIsNotNone(quest_1.create_timestamp)

        # Create quest tree
        quest_2_id = db.create_quest(
            agent_id=agent_ids[0],
            text_motivation="big_text_motivation",
            target_type=DBQuestTargetType.TEXT_ONLY,
            target="",
            parent_id=quest_1_id,
        )
        quest_3_id = db.create_quest(
            agent_id=agent_ids[0],
            text_motivation="mid_text_motivation",
            target_type=DBQuestTargetType.TEXT_ONLY,
            target="",
            parent_id=quest_2_id,
        )
        quest_4_id = db.create_quest(
            agent_id=agent_ids[0],
            text_motivation="mid_text_motivation",
            target_type=DBQuestTargetType.TEXT_ONLY,
            target="",
            parent_id=quest_2_id,
            position=1,
        )
        quest_5_id = db.create_quest(
            agent_id=agent_ids[0],
            text_motivation="low_goal_1",
            target_type=DBQuestTargetType.TARGET_ACTION,
            target="get thing",
            parent_id=quest_3_id,
            position=1,
        )
        quest_6_id = db.create_quest(
            agent_id=agent_ids[0],
            text_motivation="low_goal_2",
            target_type=DBQuestTargetType.TARGET_ACTION,
            target="do something",
            origin_filepath="test/file/path.json",
            status=DBStatus.REJECTED,
            creator_id="bad_creator",
            parent_id=quest_3_id,
        )
        quests = db.find_quests()
        self.assertEqual(len(quests), 6)

        # Query more elements
        agent_match_6 = db.find_quests(agent_id=agent_ids[0])
        self.assertEqual(len(agent_match_6), 6)
        agent_match_0 = db.find_quests(agent_id=agent_ids[1])
        self.assertEqual(len(agent_match_0), 0)
        motivation_match_2 = db.find_quests(text_motivation="mid_text_motivation")
        self.assertEqual(len(motivation_match_2), 2)
        motivation_match_1 = db.find_quests(text_motivation="low_goal_1")
        self.assertEqual(len(motivation_match_1), 1)
        motivation_match_0 = db.find_quests(text_motivation="fake_goal")
        self.assertEqual(len(motivation_match_0), 0)
        target_type_match_4 = db.find_quests(target_type=DBQuestTargetType.TEXT_ONLY)
        self.assertEqual(len(target_type_match_4), 4)
        target_type_match_2 = db.find_quests(
            target_type=DBQuestTargetType.TARGET_ACTION
        )
        self.assertEqual(len(target_type_match_2), 2)
        target_match_4 = db.find_quests(target="")
        self.assertEqual(len(target_match_4), 4)
        target_match_1 = db.find_quests(target="get thing")
        self.assertEqual(len(target_match_1), 1)
        target_match_0 = db.find_quests(target="sleep")
        self.assertEqual(len(target_match_0), 0)
        parent_id_match_2 = db.find_quests(parent_id=quest_2_id)
        self.assertEqual(len(parent_id_match_2), 2)
        parent_id_match_1 = db.find_quests(parent_id=quest_1_id)
        self.assertEqual(len(parent_id_match_1), 1)
        parent_id_match_0 = db.find_quests(parent_id=quest_6_id)
        self.assertEqual(len(parent_id_match_0), 0)
        creator_id_match_1 = db.find_quests(creator_id="bad_creator")
        self.assertEqual(len(creator_id_match_1), 1)
        creator_id_match_0 = db.find_quests(creator_id="test")
        self.assertEqual(len(creator_id_match_0), 0)
        origin_filepath_match_1 = db.find_quests(origin_filepath="test/file/path.json")
        self.assertEqual(len(origin_filepath_match_1), 1)
        origin_filepath_match_0 = db.find_quests(origin_filepath="fake/file/path.json")
        self.assertEqual(len(origin_filepath_match_0), 0)
        status_match_5 = db.find_quests(status=DBStatus.REVIEW)
        self.assertEqual(len(status_match_5), 5)
        status_match_1 = db.find_quests(status=DBStatus.REJECTED)
        self.assertEqual(len(status_match_1), 1)
        status_match_0 = db.find_quests(status=DBStatus.QUESTIONABLE)
        self.assertEqual(len(status_match_0), 0)

        # Check that inter-node references work
        with Session(db.engine) as session:
            quest_6 = session.query(DBQuest).get(quest_6_id)
            session.expunge_all()

        # Loads should fail outside of session
        with self.assertRaises(AssertionError):
            _test_parent_chain = quest_1.parent_chain
        with self.assertRaises(AssertionError):
            _test_parent_chain = quest_6.parent_chain
        with self.assertRaises(AssertionError):
            _test_subgoals = quest_1.subgoals
        with self.assertRaises(AssertionError):
            _test_subgoals = quest_6.subgoals

        quest_1.load_relations(db)
        quest_6.load_relations(db)

        # Subgoals are correct length
        self.assertEqual(len(quest_1.subgoals), 1)
        self.assertEqual(len(quest_6.subgoals), 0)

        # Parent chains are correct
        self.assertEqual(len(quest_1.parent_chain), 1)
        self.assertEqual(len(quest_6.parent_chain), 4)

        # Subgoals are all loaded
        quest_2 = quest_1.subgoals[0]
        self.assertEqual(quest_2.db_id, quest_2_id)
        self.assertEqual(len(quest_2.subgoals), 2)
        quest_4 = quest_2.subgoals[1]
        self.assertEqual(quest_4.db_id, quest_4_id)
        self.assertEqual(len(quest_4.subgoals), 0)
        quest_3 = quest_2.subgoals[0]
        self.assertEqual(quest_3.db_id, quest_3_id)
        self.assertEqual(len(quest_3.subgoals), 2)
        quest_5 = quest_3.subgoals[1]  # test order swap by position
        quest_6 = quest_3.subgoals[0]
        self.assertEqual(quest_5.db_id, quest_5_id)
        self.assertEqual(len(quest_5.subgoals), 0)
        self.assertEqual(quest_6.db_id, quest_6_id)
        self.assertEqual(len(quest_6.subgoals), 0)

    def test_create_load_graphs(self):
        """Ensure that graph loading is functioning as expected"""

        db = EnvDB(self.config)

        # Create a test graph
        test_graph_1 = OOGraph({})
        agent_node = test_graph_1.add_agent("My test agent", {})
        room_node = test_graph_1.add_room("test room", {})
        agent_node.force_move_to(room_node)

        # Save the test graph
        graph_id_1 = db.save_graph(test_graph_1, creator_id="tester")
        self.assertTrue(DBGraph.is_id(graph_id_1))
        self.assertEqual(test_graph_1.db_id, graph_id_1)

        # Ensure that the graph is set up as expected
        graphs = db.find_graphs()
        self.assertEqual(len(graphs), 1)
        db_graph_1 = graphs[0]
        self.assertEqual(db_graph_1.db_id, graph_id_1)
        self.assertEqual(db_graph_1.graph_name, "untitled")
        self.assertEqual(db_graph_1.creator_id, "tester")
        self.assertTrue(
            db.file_path_exists(db_graph_1.file_path),
            f"Output path {db_graph_1.file_path} doesn't seem to exist in the db",
        )
        self.assertEqual(db_graph_1.status, DBStatus.REVIEW)
        self.assertIsNotNone(db_graph_1.create_timestamp)

        # Make changes to the graph, then re-save
        room_node_2 = test_graph_1.add_room("test room 2", {})
        # Assert same graph, not new
        graph_id_1_2 = db.save_graph(test_graph_1, creator_id="tester")
        self.assertEqual(graph_id_1, graph_id_1_2)
        graphs = db.find_graphs()
        self.assertEqual(len(graphs), 1)

        # Load the graph directly
        db_graph_1 = db.load_graph(graph_id_1)

        # Try to pull the underlying graph from file
        oo_graph = db_graph_1.get_graph(db)
        self.assertEqual(
            oo_graph.to_json(), test_graph_1.to_json(), "Graphs are not equal!"
        )

        # Save a second graph, this time titled with an ID too
        test_graph_2 = OOGraph({"title": "Test Graph", "db_id": "UGR-TEST"})
        agent_node = test_graph_2.add_agent("My test agent", {})
        room_node = test_graph_2.add_room("test room", {})
        agent_node.force_move_to(room_node)

        # Save the second graph
        graph_id_2 = db.save_graph(test_graph_2, creator_id="tester")
        self.assertTrue(DBGraph.is_id(graph_id_2))
        self.assertEqual(test_graph_2.db_id, graph_id_2)
        self.assertEqual(test_graph_2.db_id, "UGR-TEST")

        # Do some queries
        graphs = db.find_graphs()
        self.assertEqual(len(graphs), 2)
        graph_default_name_1 = db.find_graphs(graph_name="untitled")
        self.assertEqual(len(graph_default_name_1), 1)
        graph_custom_name_1 = db.find_graphs(graph_name="Test Graph")
        self.assertEqual(len(graph_custom_name_1), 1)
        graph_name_0 = db.find_graphs(graph_name="nonexisting")
        self.assertEqual(len(graph_name_0), 0)
        graph_creator_2 = db.find_graphs(creator_id="tester")
        self.assertEqual(len(graph_creator_2), 2)
        graph_creator_0 = db.find_graphs(creator_id="nonexisting")
        self.assertEqual(len(graph_creator_0), 0)

        # Ensure main graph save failures
        with self.assertRaises(AssertionError):
            # Can't save one graph as a different creator
            _graph_id_1_3 = db.save_graph(test_graph_1, creator_id="not_tester")
        test_graph_1.db_id = "bad-db-id"
        with self.assertRaises(AssertionError):
            # Can't save a graph with an invalid DBGraph ID
            _graph_id_1_3 = db.save_graph(test_graph_1, creator_id="not_tester")

    def _get_all_dbid_mixin(self):
        """Pull all the dbid mixin classes"""
        check_classes = [HasDBIDMixin]
        has_dbid_subclasses = set()
        while len(check_classes) > 0:
            curr_class = check_classes.pop()
            subclasses = curr_class.__subclasses__()
            filtered_subclasses = [
                c for c in subclasses if c not in has_dbid_subclasses
            ]
            check_classes += filtered_subclasses
            has_dbid_subclasses = has_dbid_subclasses.union(filtered_subclasses)

        return [dbsc for dbsc in has_dbid_subclasses if hasattr(dbsc, "ID_PREFIX")]

    def test_dbid_mixin(self):
        """Ensure that all dbid mixin subclasses are valid"""
        has_dbid_subclasses = self._get_all_dbid_mixin()
        assert DBObject in has_dbid_subclasses

        for idx in range(len(has_dbid_subclasses)):
            # Assert has correct key length
            curr_class = has_dbid_subclasses[idx]
            self.assertLessEqual(
                len(curr_class.ID_PREFIX),
                3,
                f"{curr_class} prefix {curr_class.ID_PREFIX} greater than 3 characters",
            )
            # Assert creation passes self but fails others
            for idx_2 in range(len(has_dbid_subclasses)):
                test_id = curr_class.get_id()
                if idx == idx_2:
                    self.assertTrue(
                        curr_class.is_id(test_id),
                        f"ID {test_id} generated by {curr_class} get_id not accepted by is_id",
                    )
                else:
                    other_class = has_dbid_subclasses[idx_2]
                    self.assertFalse(
                        other_class.is_id(test_id),
                        f"ID {test_id} generated by {curr_class} wrongly passes is_id of {other_class}",
                    )
