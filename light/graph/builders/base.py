#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import random
from dataclasses import dataclass
from light.data_model.db.base import DBStatus

from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from light.data_model.db.environment import EnvDB, DBRoom, DBAgent, DBObject
    from light.registry.model_pool import ModelPool
    from parlai.core.message import Message  # type: ignore
    from parlai.core.agents import Agent as ParlAIAgent  # type: ignore

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

    _builder: str = "base"


class GraphBuilder(object):
    """Abstract class that defines a method for building and populating a
    graph. Used to standardize the ways that we've build maps in the past
    and to develop new ways, all adhering to a standard interface for
    making graphs"""

    def __init__(self, builder_config: GraphBuilderConfig):
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

    def __init__(
        self,
        builder_config: GraphBuilderConfig,
        db: "EnvDB",
        allow_blocked: bool = False,
    ):
        """Initialize a GraphBuilder with access to an EnvDB class"""
        self.config = builder_config
        self.allow_blocked = allow_blocked
        self.db = db
        self.db.create_node_cache()
        self.__usable_rooms = None
        self.__usable_chars = None
        self.__usable_objects = None

    def get_usable_rooms(self) -> List[str]:
        """
        Return all rooms that are currently usable,
        caching the result
        """
        if self.__usable_rooms is None:
            rooms = self.db.find_rooms()
            if not self.allow_blocked:
                rooms = [r for r in rooms if r.status == DBStatus.PRODUCTION]
            self.__usable_rooms = [r.db_id for r in rooms]
        return self.__usable_rooms.copy()

    def get_usable_chars(self) -> List[str]:
        """
        Return all chars that are currently usable,
        caching the result
        """
        if self.__usable_chars is None:
            chars = self.db.find_agents()
            if not self.allow_blocked:
                chars = [c for c in chars if c.status == DBStatus.PRODUCTION]
            self.__usable_chars = [c.db_id for c in chars]
        return self.__usable_chars.copy()

    def get_usable_objects(self) -> List[str]:
        """
        Return all objects that are currently usable,
        caching the result
        """
        if self.__usable_objects is None:
            objs = self.db.find_objects()
            if not self.allow_blocked:
                objs = [o for o in objs if o.status == DBStatus.PRODUCTION]
            self.__usable_objects = [o.db_id for o in objs]
        return self.__usable_objects.copy()

    def get_room_from_id(self, room_id: str) -> Optional["DBRoom"]:
        """Get a DBRoom representation for a room in the database by that
        room's database id. Return None if no match
        """
        if not room_id in self.get_usable_rooms():
            return None
        return self.db.get_room(room_id)

    def get_obj_from_id(self, object_id) -> Optional["DBObject"]:
        """Get a DBObject representation for an object in the database by that
        object's database id. Return None if no match
        """
        if not object_id in self.get_usable_objects():
            return None
        return self.db.get_object(object_id)

    def get_char_from_id(self, char_id) -> Optional["DBAgent"]:
        """Get a DBAgent representation for a char in the database by that
        char's database id. Return None if no match
        """
        if not char_id in self.get_usable_chars():
            return None
        return self.db.get_agent(char_id)

    def get_random_room(self) -> Optional["DBRoom"]:
        """Get a random room from the database."""
        room_ids = self.get_usable_rooms()
        if not len(room_ids):
            return None  # Returning none if the list is empty
        room_id = random.choice(room_ids)
        room = self.get_room_from_id(room_id)
        return room

    def get_random_char(self) -> Optional["DBAgent"]:
        """Get a random char from the database."""
        char_ids = self.get_usable_chars()
        if not len(char_ids):
            return None
        char_id = random.choice(char_ids)
        char = self.get_char_from_id(char_id)
        return char

    def get_random_obj(self) -> Optional["DBObject"]:
        """Get a random obj from the database."""
        obj_ids = self.get_usable_objects()
        if not len(obj_ids):
            return None
        obj_id = random.choice(obj_ids)
        obj = self.get_obj_from_id(obj_id)
        return obj

    def get_room_categories(self) -> List[str]:
        """Return a list of the possible categories that rooms can be"""
        room_name_list = self.db.find_room_names()
        if not self.allow_blocked:
            room_name_list = [
                r for r in room_name_list if r.status == DBStatus.PRODUCTION
            ]
        return [r.name for r in room_name_list]

    def roomfeats_to_id(self, text_feats) -> Optional[str]:
        """Return db_id of a room from text features"""
        features = text_feats.split(". ")
        rooms = self.db.find_rooms(name=features[0])
        if len(rooms) == 0:
            return None
        if self.allow_blocked or rooms[0].status == DBStatus.PRODUCTION:
            return rooms[0].db_id
        return None

    def objfeats_to_id(self, text_feats) -> Optional[str]:
        """Return db_id of an object from text features"""
        features = text_feats.split(". ", 1)
        objs = self.db.find_objects(
            name=features[0].strip(),
            physical_description=features[1].strip(),
        )
        if len(objs) == 0:
            return None
        if self.allow_blocked or objs[0].status == DBStatus.PRODUCTION:
            return objs[0].db_id
        return None

    def charfeats_to_id(self, text_feats) -> Optional[str]:
        """Return db_id of character from text features"""
        features = text_feats.split(". ", 1)
        agents = self.db.find_agents(
            name=features[0].strip(),
            persona=features[1].strip(),
        )
        if len(agents) == 0:
            return None
        if self.allow_blocked or agents[0].status == DBStatus.PRODUCTION:
            return agents[0].db_id
        return None


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

    async def agent_recommend(self, observation: str, agent_type: str) -> "Message":
        """Return a response when querying a specific
        type of agent and return the model response"""
        assert agent_type in self.agents, "Agent type not found in existing agents"
        self.agents[agent_type].reset()
        msg = {"text": observation, "episode_done": True}
        self.agents[agent_type].observe(msg)
        response = self.agents[agent_type].act()
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
