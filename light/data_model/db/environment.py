#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from light.data_model.db.base import BaseDB, DBStatus, DBSplitType
from light.graph.structured_graph import OOGraph
from omegaconf import MISSING, DictConfig
from typing import Optional, List, Tuple, Union, Dict, Any, Set, TYPE_CHECKING
from sqlalchemy import (
    insert,
    select,
    Enum,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import declarative_base, relationship, Session

import enum
import os

SQLBase = declarative_base()

BASE_NAME_LENGTH_CAP = 96
WORLD_NAME_LENGTH_CAP = 128
EDGE_LABEL_LENGTH_CAP = 64
PERSONA_LENGTH_CAP = 512
DESCRIPTION_LENGTH_CAP = 512
NAME_PREFIX_LENGTH = 32
ID_STRING_LENGTH = 32
QUEST_MOTIVATION_LENGTH = 128
REPORT_REASON_LENGTH = 1024
FILE_PATH_LENGTH_CAP = 96


# Name Key Components - Should be text searchable


class DBNameKey:
    """
    Class for the shared db base components, as all have just an
    id and a name
    """

    db_id = Column(Integer, primary_key=True)
    name = Column(String(BASE_NAME_LENGTH_CAP), nullable=False, index=True)
    status = Column(Enum(DBStatus), nullable=False, index=True)
    split = Column(Enum(DBSplitType), nullable=False, index=True)
    create_timestamp = Column(Float, nullable=False)
    creator_id = Column(
        String(ID_STRING_LENGTH)
    )  # temp retain the creator ID for new things


class DBAgentName(DBNameKey, SQLBase):
    """
    Class containing the expected elements for an agent name,
    with any supporting methods
    """

    __tablename__ = "agent_names"

    def __repr__(self):
        return f"DBAgentName({self.db_id!r}| {self.name})"


class DBObjectName(DBNameKey, SQLBase):
    """
    Class containing the expected elements for an object name,
    with any supporting methods
    """

    __tablename__ = "object_names"

    def __repr__(self):
        return f"DBObjectName({self.db_id!r}| {self.name})"


class DBRoomName(DBNameKey, SQLBase):
    """
    Class containing the expected elements for a room name,
    with any supporting methods
    """

    __tablename__ = "room_names"

    def __repr__(self):
        return f"DBRoomName({self.db_id!r}| {self.name})"


# Graph nodes


class DBElem:
    """Class for shared attributes for all graph model components"""

    db_id = Column(Integer, primary_key=True)
    full_name = Column(String(BASE_NAME_LENGTH_CAP), nullable=False, index=True)
    built_occurrences = Column(Integer, nullable=False, default=0)


class DBAgent(DBElem, SQLBase):
    """
    Class containing the expected elements for an agent,
    with any supporting methods
    """

    __tablename__ = "agents"

    base_id = Column(ForeignKey("agent_names.db_id"), nullable=False)
    persona = Column(String(PERSONA_LENGTH_CAP), nullable=False, index=True)
    physical_description = Column(
        String(DESCRIPTION_LENGTH_CAP), nullable=False, index=True
    )
    name_prefix = Column(String(NAME_PREFIX_LENGTH), nullable=False)
    is_plural = Column(Boolean)
    size = Column(Integer)
    contain_size = Column(Integer)
    constitution = Column(Float)
    charisma = Column(Float)
    strength = Column(Float)
    dexterity = Column(Float)
    intelligence = Column(Float)
    wisdom = Column(Float)

    def __repr__(self):
        return f"DBAgent({self.db_id!r}| {self.full_name})"


class DBObject(DBElem, SQLBase):
    """
    Class containing the expected elements for an object,
    with any supporting methods
    """

    __tablename__ = "objects"

    base_id = Column(ForeignKey("object_names.db_id"), nullable=False)
    physical_description = Column(
        String(DESCRIPTION_LENGTH_CAP), nullable=False, index=True
    )
    is_container = Column(Float)
    is_drink = Column(Float)
    is_food = Column(Float)
    is_gettable = Column(Float)
    is_surface = Column(Float)
    is_wearable = Column(Float)
    is_weapon = Column(Float)
    name_prefix = Column(String(NAME_PREFIX_LENGTH), nullable=False)
    is_plural = Column(Boolean)
    size = Column(Integer)
    contain_size = Column(Integer)
    value = Column(Float)
    rarity = Column(Float)

    def __repr__(self):
        return f"DBObject({self.db_id!r}| {self.full_name})"


class DBRoomInsideType(enum.Enum):
    """Types of indoor or outdoor statuses for rooms"""

    INDOORS = "indoors"
    ENCLOSED = "enclosed"
    COVERED = "covered"
    OUTSIDE = "outside"
    HYBRID = "hybrid"
    MULTI_ROOM = "multi_room"
    OTHER = "other"
    UNKNOWN = "unknown"


class DBRoom(DBElem, SQLBase):
    """
    Class containing the expected elements for a room,
    with any supporting methods
    """

    __tablename__ = "rooms"

    base_id = Column(ForeignKey("room_names.db_id"), nullable=False)
    description = Column(String(DESCRIPTION_LENGTH_CAP), nullable=False, index=True)
    backstory = Column(String(DESCRIPTION_LENGTH_CAP), nullable=False, index=True)
    size = Column(Integer)
    indoor_status = Column(Enum(DBRoomInsideType), nullable=False)

    def __repr__(self):
        return f"DBRoom({self.db_id!r}| {self.full_name})"


# Graph edges and attributes


class DBEdgeType(enum.Enum):
    """Edges in the LIGHT Environment DB"""

    CONTAINS = "contains"
    MAY_CONTAIN = "may_contain"
    WEARING = "wearing"
    MAY_WEAR = "may_wear"
    WIELDING = "wielding"
    MAY_WIELD = "may_wield"
    CONTAINED_IN = "contained_in"
    MAY_BE_CONTAINED_IN = "may_be_contained_in"


class DBEdgeBase:
    """Base attributes for an edge as stored in the environment DB"""

    db_id = Column(Integer, primary_key=True)
    parent_id = Column(String(ID_STRING_LENGTH))
    edge_type = Column(Enum(DBEdgeType), nullable=False)
    built_occurrences = Column(Integer, nullable=False, default=0)
    status = Column(Enum(DBStatus), nullable=False, index=True)
    edge_label = Column(String(EDGE_LABEL_LENGTH_CAP), nullable=False)
    create_timestamp = Column(Float, nullable=False)
    creator_id = Column(
        String(ID_STRING_LENGTH)
    )  # temp retain the creator ID for new things


class DBEdge(DBEdgeBase, SQLBase):
    """Class for edges between two GraphNodes registered in the DB"""

    __tablename__ = "edges"

    # TODO function that executes this edge and gets the child
    child_id = Column(String(ID_STRING_LENGTH))

    def __repr__(self):
        return (
            f"DBEdge({self.db_id!r}| {self.parent_id}-{self.edge_type}-{self.child_id})"
        )


class DBTextEdge(DBEdgeBase, SQLBase):
    """Class for edges between a GraphNodes and a new entity in the DB"""

    __tablename__ = "text_edges"

    child_text = Column(String(BASE_NAME_LENGTH_CAP), nullable=False, index=True)

    def __repr__(self):
        return f"DBTextEdge({self.db_id!r}| {self.parent_id}-{self.edge_type}-{self.child_text})"


# Other


class DBEdit(SQLBase):
    """Suggested change to some DB content"""

    __tablename__ = "edits"

    edit_id = Column(Integer, primary_key=True)
    editor_id = Column(String(ID_STRING_LENGTH))  # temp retain the associated user ID
    node_id = Column(
        String(ID_STRING_LENGTH), nullable=False, index=True
    )  # Id of entry in table
    field = Column(String(ID_STRING_LENGTH), nullable=False)  # name of field in table
    status = Column(Enum(DBStatus), nullable=False, index=True)
    old_value = Column(String(DESCRIPTION_LENGTH_CAP), nullable=False, index=True)
    new_value = Column(String(DESCRIPTION_LENGTH_CAP), nullable=False, index=True)
    create_timestamp = Column(Float, nullable=False)

    # TODO helper method for executing/accepting/rejecting an edit

    def __repr__(self):
        return f"DBEdit({self.edit_id!r}| {self.node_id}-{self.field}-{self.status})"


class DBFlagTargetType(enum.Enum):
    """Types of flags"""

    FLAG_USER = "user_flag"  # Something wrong about a user's behavior
    FLAG_UTTERANCE = "utterance_flag"  # Something specifically wrong about
    FLAG_ENVIRONMENT = "env_flag"  # Flag something inappropriate in the environment


class DBFlag(SQLBase):
    """User-flagged content of some type"""

    __tablename__ = "flags"

    flag_id = Column(Integer, primary_key=True)
    flag_type = Column(Enum(DBFlagTargetType), nullable=False)
    target_id = Column(String(ID_STRING_LENGTH), nullable=False, index=True)
    reason = Column(String(REPORT_REASON_LENGTH))
    create_timestamp = Column(Float, nullable=False)

    def __repr__(self):
        return f"DBFlag({self.flag_id!r}| {self.target_id}-{self.flag_type})"


class DBQuestTargetType(enum.Enum):
    """Types of quest targets"""

    TEXT_ONLY = "text_only"  # only a map from character to motivation
    SUBGOAL = "subgoal"  # Map from motivation to subgoal of motivation
    TARGET_ACTION = "target_action"  # map from motivation to target action


class DBQuest(SQLBase):
    """Stores quest information for breaking down motivations"""

    __tablename__ = "edges"

    quest_id = Column(Integer, primary_key=True)
    agent_id = Column(ForeignKey("agents.db_id"), nullable=False)
    text_motivation = Column(String(QUEST_MOTIVATION_LENGTH), nullable=False)
    target_type = Column(Enum(DBQuestTargetType), nullable=False)
    target = Column(String(QUEST_MOTIVATION_LENGTH))
    status = Column(Enum(DBStatus), nullable=False, index=True)
    origin_filepath = Column(String(FILE_PATH_LENGTH_CAP))
    creator_id = Column(
        String(ID_STRING_LENGTH)
    )  # temp retain the creator ID for new things
    create_timestamp = Column(Float, nullable=False)

    # TODO function to collect all subgoals

    # TODO function to traverse through to parent

    def __repr__(self):
        return f"DBQuest({self.quest_id!r}| {self.agent_id}-{self.target_type})"


class DBGraph(SQLBase):
    """Manifest entry for a user-saved or created graph"""

    __tablename__ = "saved_graphs"

    graph_id = Column(Integer, primary_key=True)
    graph_name = Column(String(WORLD_NAME_LENGTH_CAP), nulable=False, index=True)
    creator_id = Column(
        String(ID_STRING_LENGTH), nulable=False, index=True
    )  # retain the creator ID, they own this
    file_path = Column(String(FILE_PATH_LENGTH_CAP), nulable=False)
    create_timestamp = Column(Float, nullable=False)

    # TODO implement method to retrieve this graph

    # TODO implement method to write this graph to the file

    def __repr__(self):
        return f"DBGraph({self.graph_id!r}| {self.graph_name})"


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

    def create_agent_name(self, name: str) -> str:
        """Create a new agent name in the database"""
        # Return agent name_id

    def get_agent_name(
        self, name: Optional[str] = None, id: Optional[str] = None
    ) -> "DBAgentName":
        """Get a specific agent name, assert that it exists"""

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
        """Create this agent, making an agent name first if required"""
        # Return agent_id

    def find_agents(
        self,
        name_id: Optional[str] = None,
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

    def create_object_name(self, name: str) -> str:
        """Create a new object name in the database"""
        # Return object name_id

    def get_object_name(
        self, name: Optional[str] = None, id: Optional[str] = None
    ) -> "DBObjectName":
        """Get a specific object name, assert that it exists"""

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
        """Create a new object, making a object_name first if required"""
        # Return object_id

    def find_objects(
        self,
        name_id: Optional[str] = None,
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

    def create_room_name(self, name: str) -> str:
        """Create a new room name in the database"""
        # Return room name_id

    def get_room_name(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> "DBRoomName":
        """Return all room names matching the given parameters"""

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
        """Create a new room, making a room name first if required"""
        # Return room_id

    def find_rooms(
        self,
        name_id: Optional[str] = None,
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
