#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from light.data_model.db.base import BaseDB, DBStatus, DBSplitType
from light.graph.structured_graph import OOGraph
from omegaconf import MISSING, DictConfig
from typing import Optional, Union, Dict, Any
from dataclasses import dataclass
from enum import Enum


class DBEdgeType(Enum):
    """Edges in the LIGHT Environment DB"""

    CONTAINS = "contains"
    MAY_CONTAIN = "may_contain"
    WEARING = "wearing"
    MAY_WEAR = "may_wear"
    WIELDING = "wielding"
    MAY_WIELD = "may_wield"
    CONTAINED_IN = "contained_in"
    MAY_BE_INSIDE = "may_contained_in"


# Base Components


@dataclass
class DBBaseElem:
    """
    Class for the shared db base components, as all have just an
    id and a name
    """

    db_id: str
    name: str


@dataclass
class DBBaseAgent(DBBaseElem):
    """
    Class containing the expected elements for a base agent,
    with any supporting methods
    """


@dataclass
class DBBaseObject(DBBaseElem):
    """
    Class containing the expected elements for a base object,
    with any supporting methods
    """


@dataclass
class DBBaseRoom(DBBaseElem):
    """
    Class containing the expected elements for a base room,
    with any supporting methods
    """


# Graph nodes


@dataclass
class DBElem:
    """Class for shared attributes for all graph model components"""

    db_id: str
    base_id: str
    name: str
    status: DBStatus
    split: DBSplitType
    creator_id: Optional[str]


@dataclass
class DBAgent(DBElem):
    """
    Class containing the expected elements for an agent,
    with any supporting methods
    """

    persona: str
    physical_description: str
    name_prefix: Optional[str] = None
    is_plural: Optional[str] = None
    size: Optional[int] = None
    contain_size: Optional[int] = None
    constitution: Optional[int] = None
    charisma: Optional[int] = None
    strength: Optional[int] = None
    dexterity: Optional[int] = None
    intelligence: Optional[int] = None
    wisdom: Optional[int] = None


@dataclass
class DBObject(DBElem):
    """
    Class containing the expected elements for an object,
    with any supporting methods
    """

    name: str
    physical_description: str
    is_container: float
    is_drink: float
    is_food: float
    is_gettable: float
    is_surface: float
    is_wearable: float
    is_weapon: float
    name_prefix: Optional[str] = None
    is_plural: Optional[str] = None
    size: Optional[int] = None
    contain_size: Optional[int] = None
    value: Optional[float] = None
    rarity: Optional[float] = None


@dataclass
class DBRoom(DBElem):
    """
    Class containing the expected elements for a room,
    with any supporting methods
    """

    name: str
    description: str
    backstory: str
    size: Optional[int] = None
    indoor_status: Optional[str] = None


# Graph edges and attributes


@dataclass
class DBEdgeBase:
    """Base attributes for an edge as stored in the environment DB"""

    parent_id: str
    edge_type: str
    edge_strength: int = 1
    status: DBStatus
    edge_label: Optional[str] = None
    creator_id: Optional[str] = None


@dataclass
class DBEdge(DBEdgeBase):
    child_id: str


@dataclass
class DBTextEdge(DBEdgeBase):
    child_text: str


# Other


@dataclass
class DBEdit:
    edit_id: str
    user_id: str
    table: str
    node_id: str
    field: str
    value: Any


@dataclass
class DBFlag:
    flag_id: str
    user_id: str
    table: str
    node_id: str
    reason: str


@dataclass
class DBQuest:
    quest_id: str
    agent_id: str
    text_motivation: str
    target_type: str
    target: str
    status: DBStatus
    creator_id: Optional[str] = None


@dataclass
class DBGraph:
    graph_id: str
    graph_name: str
    creator_id: str
    file_path: str


class EnvDB(BaseDB):
    """
    Environment database for LIGHT, containing accessors for the
    LIGHT environment, nodes, attributes, additional annotations,
    quests, world-interactions, and more.
    """

    def _complete_init(self, config: "DictConfig"):
        """
        Initialize any specific environment-related paths
        """
        raise NotImplementedError()

    def _validate_init(self):
        """
        Ensure that the environment manifest exists, and that key
        paths are properly initialized
        """
        raise NotImplementedError()

    def _first_init_tables(self):
        """If the tables don't exist at all, create them."""

    def create_node_cache(self) -> None:
        """
        Create a local cached version of the environment nodes and
        relationships, to use for rapid construction of things
        without needing repeated queries
        """

    # Agents

    def create_base_agent(self, name: str) -> str:
        """Create a new agent name in the database"""
        # Return base_char_id

    def get_base_agent(
        self, name: Optional[str] = None, id: Optional[str] = None
    ) -> "DBBaseAgent":
        """Get a specific base agent, assert that it exists"""

    def create_agent_entry(
        self,
        name: str,
        persona: str,
        physical_description: str,
        name_prefix: Optional[str] = None,
        is_plural: Optional[str] = None,
        size: Optional[int] = None,
        contain_size: Optional[int] = None,
        constitution: Optional[int] = None,
        charisma: Optional[int] = None,
        strength: Optional[int] = None,
        dexterity: Optional[int] = None,
        intelligence: Optional[int] = None,
        wisdom: Optional[int] = None,
        status: DBStatus = DBStatus.REVIEW,
        split: DBSplitType = DBSplitType.UNSET,
        creator_id: Optional[str] = None,
    ) -> str:
        """Create this agent, making a base_agent first if required"""
        # Return agent_id

    def find_agents(
        self,
        base_id: Optional[str] = None,
        name: Optional[str] = None,
        persona: Optional[str] = None,
        physical_description: Optional[str] = None,
        name_prefix: Optional[str] = None,
        is_plural: Optional[str] = None,
        status: Optional[DBStatus] = None,
        split: Optional[DBSplitType] = None,
        creator_id: Optional[str] = None,
    ) -> List["DBAgent"]:
        """Return all agents matching the given parameters"""

    def get_agent(self, id: str) -> "DBAgent":
        """Return the given agent, raise an exception if non-existing"""

    # Objects

    def create_base_object(self, name: str) -> str:
        """Create a new object name in the database"""
        # Return base_obj_id

    def get_base_object(
        self, name: Optional[str] = None, id: Optional[str] = None
    ) -> "DBBaseObject":
        """Get a specific base object, assert that it exists"""

    def create_object_entry(
        self,
        name: str,
        physical_description: str,
        is_container: float,
        is_drink: float,
        is_food: float,
        is_gettable: float,
        is_surface: float,
        is_wearable: float,
        is_weapon: float,
        name_prefix: Optional[str] = None,
        is_plural: Optional[str] = None,
        size: Optional[int] = None,
        contain_size: Optional[int] = None,
        value: Optional[float] = None,
        rarity: Optional[float] = None,
        status: DBStatus = DBStatus.REVIEW,
        split: DBSplitType = DBSplitType.UNSET,
        creator_id: Optional[str] = None,
    ) -> str:
        """Create a new object, making a base_object first if required"""
        # Return object_id

    def find_objects(
        self,
        base_id: Optional[str] = None,
        name: Optional[str] = None,
        physical_description: Optional[str] = None,
        is_container: Optional[bool] = None,
        is_drink: Optional[bool] = None,
        is_food: Optional[bool] = None,
        is_gettable: Optional[bool] = None,
        is_surface: Optional[bool] = None,
        is_wearable: Optional[bool] = None,
        is_weapon: Optional[bool] = None,
        name_prefix: Optional[str] = None,
        is_plural: Optional[str] = None,
        status: Optional[DBStatus] = None,
        split: Optional[DBSplitType] = None,
        creator_id: Optional[str] = None,
    ) -> List["DBObject"]:
        """Return all objects matching the given parameters"""

    def get_object(self, id: str) -> "DBObject":
        """Return the given object, raise exception if non-existing"""

    # Rooms

    def create_base_room(self, name: str) -> str:
        """Create a new room name in the database"""
        # Return base_room_id

    def get_base_room(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> "DBBaseRoom":
        """Return all base rooms matching the given parameters"""

    def create_room_entry(
        self,
        name: str,
        description: str,
        backstory: str,
        size: Optional[int] = None,
        indoor_status: Optional[str] = None,
        rarity: Optional[float] = None,
        status: DBStatus = DBStatus.REVIEW,
        split: DBSplitType = DBSplitType.UNSET,
        creator_id: Optional[str] = None,
    ) -> str:
        """Create a new room, making a base_room first if required"""
        # Return room_id

    def find_rooms(
        self,
        base_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        backstory: Optional[str] = None,
        indoor_status: Optional[str] = None,
        status: Optional[DBStatus] = None,
        split: Optional[DBSplitType] = None,
        creator_id: Optional[str] = None,
    ) -> List["DBRoom"]:
        """Return all rooms matching the given parameters"""

    def get_room(self, id: str) -> "DBRoom":
        """Get a specific room, assert that it exists"""

    # Attributes

    def create_arbitrary_attribute(
        self,
        target_id: str,
        attribute_name: str,
        attribute_value_string: str,
        status: DBStatus = DBStatus.REVIEW,
        creator_id: Optional[str] = None,
    ) -> None:
        """Create an arbitrary attribute entry for the target node"""

    # Edges

    def create_edge(
        self,
        parent_id: str,
        child_id: str,
        edge_type: str,
        edge_strength: int = 1,
        edge_label: Optional[str] = None,
        status: DBStatus = DBStatus.REVIEW,
        creator_id: Optional[str] = None,
    ) -> str:
        """Create an edge between two nodes"""

    def get_edges(
        self,
        parent_id: Optional[str] = None,
        child_id: Optional[str] = None,
        edge_type: Optional[str] = None,
        status: Optional[DBStatus] = None,
        creator_id: Optional[str] = None,
        min_strength: Optional[int] = 0,
    ) -> List["DBEdge"]:
        """Return all edges matching the given parameters"""

    def create_text_edge(
        self,
        parent_id: str,
        child_text: str,
        edge_type: str,
        edge_strength: int = 1,
        edge_label: Optional[str] = None,
        status: DBStatus = DBStatus.REVIEW,
        creator_id: Optional[str] = None,
    ) -> str:
        """Create an edge between a node and the name of a possible leaf"""

    def get_text_edges(
        self,
        parent_id: Optional[str] = None,
        child_text: Optional[str] = None,
        edge_type: Optional[str] = None,
        status: Optional[DBStatus] = None,
        creator_id: Optional[str] = None,
        min_strength: Optional[int] = 0,
    ) -> List["DBTextEdge"]:
        """Return all text edges matching the given parameters"""

    # Flags and edits

    def create_edit(
        self,
        user_id: str,
        table: str,
        node_id: str,
        field: str,
        value: Any,
    ) -> str:
        """Write a potential edit to file. Return the edit filename"""

    def get_edits(
        self,
        user_id: Optional[str] = None,
        table: Optional[str] = None,
        node_id: Optional[str] = None,
        field: Optional[str] = None,
        status: Optional[DBStatus] = None,
    ) -> List["DBEdit"]:
        """Return all edits matching the given parameters"""

    def flag_entry(
        self,
        user_id: str,
        table: str,
        node_id: str,
        reason: str,
    ) -> str:
        """
        Write a potential flag to file, update the node's status,
        return the flag filename
        """

    def get_flags(
        self,
        user_id: str,
        table: str,
        node_id: str,
        status: Optional[DBStatus] = None,
    ) -> List["DBFlag"]:
        """Return all flags matching the given parameters"""

    # Quests

    def create_quest(
        self,
        agent_id: str,
        text_motivation: str,
        target_type: str,
        target: str,
        status: DBStatus = DBStatus.REVIEW,
        creator_id: Optional[str] = None,
    ) -> str:
        """
        Creates a Quest, which is a mapping from character and motivation
        text to a desired action or list of subquests
        """

    def find_quests(
        self,
        agent_id: Optional[str] = None,
        text_motivation: Optional[str] = None,
        target_type: Optional[str] = None,
        target: Optional[str] = None,
        status: Optional[DBStatus] = None,
        creator_id: Optional[str] = None,
    ) -> List["DBQuest"]:
        """Return all text edges matching the given parameters"""

    # Graphs

    def save_graph(self, graph: "OOGraph", creator_id: str) -> str:
        """Save this graph to a file for the given user"""

    def load_graph(self, graph_id: str) -> "DBGraph":
        """Return the queried graph, raising if nonexistent"""

    def find_graphs(
        self,
        graph_name: Optional[str] = None,
        creator_id: Optional[str] = None,
        # ... TODO can add other search attributes?
    ) -> List["DBGraph"]:
        """Return all graphs matching the provided parameters"""
