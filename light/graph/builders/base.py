#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import asyncio
import random, copy
from dataclasses import dataclass
from light.graph.builders.db_utils import id_is_usable
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

from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from light.registry.model_pool import ModelPool
    from parlai.core.message import Message
    from parlai.core.agents import Agent as ParlAIAgent

# Possible new entrances for add_new_random_agent
POSSIBLE_NEW_ENTRANCES = [
    "somewhere you can't see",
    "an undiscernable place",
    "a puff of smoke",
    "behind the shadows",
    "nowhere in particular",
    "a flash of light",
]


@dataclass
class GraphBuilderConfig(object):
    """Configuration options for a specific graph builder"""

    pass


class GraphBuilder(object):
    """Abstract class that defines a method for building and populating a
    graph. Used to standardize the ways that we've build maps in the past
    and to develop new ways, all adhering to a standard interface for
    making graphs"""

    def __init__(self):
        """Initialize any required models you might need, parse arguments, and
        set other parameters as required to build graphs using this builder"""
        raise NotImplementedError

    async def add_random_new_agent_to_graph(self, target_graph):
        """Add an agent to the graph in a random room somewhere"""
        raise NotImplementedError

    async def get_graph(self):
        """Return an OOGraph built by this builder"""
        raise NotImplementedError


class DBGraphBuilder(GraphBuilder):
    """Abstract GraphBuilder that has convenience functions for accessing
    the light db to find content
    """

    def __init__(self, ldb, allow_blocked=False):
        """Initialize a GraphBuilder with access to a LIGHTDatabase class"""
        self.allow_blocked = allow_blocked
        self.db = ldb
        with self.db as open_db:
            open_db.create_cache()
        self.__usable_rooms = None
        self.__usable_chars = None
        self.__usable_objects = None

    def get_usable_rooms(self):
        """
        Return all rooms that are currently usable,
        caching the result
        """
        if self.__usable_rooms is None:
            with self.db as ldb:
                room_ids = [
                    room["id"]
                    for room in ldb.get_room()
                    if id_is_usable(ldb, room["id"])
                ]
                self.__usable_rooms = room_ids
        return self.__usable_rooms.copy()

    def get_usable_chars(self):
        """
        Return all chars that are currently usable,
        caching the result
        """
        if self.__usable_chars is None:
            with self.db as ldb:
                char_ids = [
                    char["id"]
                    for char in ldb.get_character()
                    if id_is_usable(ldb, char["id"])
                ]
                self.__usable_chars = char_ids
        return self.__usable_chars.copy()

    def get_usable_objects(self):
        """
        Return all objects that are currently usable,
        caching the result
        """
        if self.__usable_objects is None:
            with self.db as ldb:
                obj_ids = [
                    obj["id"]
                    for obj in ldb.get_object()
                    if id_is_usable(ldb, obj["id"])
                ]
                self.__usable_objects = obj_ids
        return self.__usable_objects.copy()

    def get_room_from_id(self, room_id):
        """Get a DBRoom representation for a room in the database by that
        room's database id. Return None if no match
        """
        if not room_id in self.get_usable_rooms():
            return None
        room = DBRoom(self.db, room_id, cache=self.db.cache)
        return room

    def get_obj_from_id(self, object_id):
        """Get a DBObject representation for an object in the database by that
        object's database id. Return None if no match
        """
        if not object_id in self.get_usable_objects():
            return None
        obj = DBObject(self.db, object_id, cache=self.db.cache)
        return obj

    def get_char_from_id(self, char_id):
        """Get a DBCharacter representation for a char in the database by that
        char's database id. Return None if no match
        """
        if not char_id in self.get_usable_chars():
            return None
        char = DBCharacter(self.db, char_id, cache=self.db.cache)
        return char

    def get_random_room(self):
        """Get a random room from the database."""
        room_ids = self.get_usable_rooms()
        if not len(room_ids):
            return None  # Returning none if the list is empty
        room_id = random.choice(room_ids)
        room = self.get_room_from_id(room_id)
        return room

    def get_random_char(self):
        """Get a random char from the database."""
        char_ids = self.get_usable_chars()
        if not len(char_ids):
            return None
        char_id = random.choice(char_ids)
        char = self.get_char_from_id(char_id)
        return char

    def get_random_obj(self):
        """Get a random obj from the database."""
        obj_ids = self.get_usable_objects()
        if not len(obj_ids):
            return None
        obj_id = random.choice(obj_ids)
        obj = self.get_obj_from_id(obj_id)
        return obj

    def get_room_categories(self):
        """Return a list of the possible categories that rooms can be"""
        with self.db as ldb:
            base_room_name_list = [
                br["name"] for br in ldb.get_base_room() if id_is_usable(ldb, br["id"])
            ]
        return base_room_name_list

    def roomfeats_to_id(self, text_feats):
        """Return db_id of a room from text features"""
        features = text_feats.split(".")
        with self.db as ldb:
            id = ldb.get_room(name=features[0])[0]["id"]
            return id if id_is_usable(ldb, id) else None

    def objfeats_to_id(self, text_feats):
        """Return db_id of an object from text features"""
        features = text_feats.split(".")
        with self.db as ldb:
            objs = ldb.get_object(name=features[0])
            if len(objs) > 0:
                id = objs[0]["id"]
            else:
                return None
            return id if id_is_usable(ldb, id) else None

    def charfeats_to_id(self, text_feats):
        """Return db_id of character from text features"""
        features = text_feats.split(".")
        with self.db as ldb:
            chars = ldb.get_character(name=features[0])
            if len(chars) > 0:  # Catching for failed query
                id = chars[0]["id"]
            else:
                return None
            return id if id_is_usable(ldb, id) else None


class SingleSuggestionGraphBuilder(object):
    """Abstract class that defines methods to obtain suggestions from models
    for building LIGHT worlds and related graphs"""

    def __init__(self, model_pool: "ModelPool"):
        """Initalize  SingleSuggestionGraphBuilder to access suggestion models"""
        self.agents: Dict[str, "ParlAIAgent"] = {}
        self.model_pool = model_pool

    def load_models(self) -> None:
        """abstract method for loading models for suggestions"""
        raise NotImplementedError

    async def agent_recommend(self, observation, agent_type) -> "Message":
        """Return a response when querying a specific
        type of agent and return the model response"""
        assert agent_type in self.agents, "Agent type not found in existing agents"
        self.agents[agent_type].reset()
        msg = {"text": observation, "episode_done": True}
        self.agents[agent_type].observe(msg)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, self.agents[agent_type].act)
        return response

    def get_description(self, txt_feat, element_type, num_results=5):
        """Abstract method for getting a desired description given a title
        of a given element"""
        raise NotImplementedError

    def get_element_relationship(
        self,
        element_txt,
        element_type,
        relationship_type,
        context=None,
        num_results=5,
        banned_items=[],
    ):
        """abstract method for getting desired relationship given a non-graph
        element and a type of relationship"""
        raise NotImplementedError

    def get_similar_element(self, txt_feats, element_type):
        """abstract method for getting a corresponding element that already
        exists in the in the model"""
        raise NotImplementedError
