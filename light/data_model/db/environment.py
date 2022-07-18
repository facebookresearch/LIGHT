#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from light.data_model.db.base import BaseDB, DBStatus, DBSplitType
from light.graph.structured_graph import OOGraph
from omegaconf import MISSING, DictConfig
from typing import (
    Optional,
    List,
    Tuple,
    Union,
    Dict,
    Any,
    Set,
    Type,
    cast,
    TYPE_CHECKING,
)
from uuid import uuid4
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
from sqlalchemy.orm import declarative_base, relationship, Session, join

import enum
import os

SQLBase = declarative_base()

BASE_NAME_LENGTH_CAP = 96
WORLD_NAME_LENGTH_CAP = 128
EDGE_LABEL_LENGTH_CAP = 64
PERSONA_LENGTH_CAP = 512
DESCRIPTION_LENGTH_CAP = 512
NAME_PREFIX_LENGTH = 32
ID_STRING_LENGTH = 40
QUEST_MOTIVATION_LENGTH = 128
REPORT_REASON_LENGTH = 1024
FILE_PATH_LENGTH_CAP = 96


class HasDBIDMixin:
    """Simple mixin for classes that define their own DBID schema"""

    # ID prefix should be 3 characters max.
    ID_PREFIX: int = "ZZZ"

    @classmethod
    def get_id(cls: Type["HasDBIDMixin"]) -> str:
        """Create an ID for this class"""
        return f"{cls.ID_PREFIX}-{uuid4()}"

    @classmethod
    def is_id(cls: Type["HasDBIDMixin"], test_id: str) -> str:
        """Check if a given ID refers to this class"""
        return test_id.startswith(f"{cls.ID_PREFIX}-")


# Name Key Components - Should be text searchable


class DBNameKey(HasDBIDMixin):
    """
    Class for the shared db base components, as all have just an
    id and a name
    """

    db_id = Column(String(ID_STRING_LENGTH), primary_key=True)
    name = Column(String(BASE_NAME_LENGTH_CAP), nullable=False, index=True, unique=True)
    status = Column(Enum(DBStatus), nullable=False, index=True)
    split = Column(Enum(DBSplitType), nullable=False, index=True)


class DBAgentName(DBNameKey, SQLBase):
    """
    Class containing the expected elements for an agent name,
    with any supporting methods
    """

    __tablename__ = "agent_names"
    ID_PREFIX = "AGN"

    def __repr__(self):
        return f"DBAgentName({self.db_id!r}| {self.name})"


class DBObjectName(DBNameKey, SQLBase):
    """
    Class containing the expected elements for an object name,
    with any supporting methods
    """

    __tablename__ = "object_names"
    ID_PREFIX = "OBN"

    def __repr__(self):
        return f"DBObjectName({self.db_id!r}| {self.name})"


class DBRoomName(DBNameKey, SQLBase):
    """
    Class containing the expected elements for a room name,
    with any supporting methods
    """

    __tablename__ = "room_names"
    ID_PREFIX = "RMN"

    def __repr__(self):
        return f"DBRoomName({self.db_id!r}| {self.name})"


# Graph nodes


class DBElem(HasDBIDMixin):
    """Class for shared attributes for all graph model components"""

    db_id = Column(String(ID_STRING_LENGTH), primary_key=True)
    name = Column(String(BASE_NAME_LENGTH_CAP), nullable=False, index=True)
    built_occurrences = Column(Integer, nullable=False, default=0)
    status = Column(Enum(DBStatus), nullable=False, index=True)
    create_timestamp = Column(Float, nullable=False)
    creator_id = Column(
        String(ID_STRING_LENGTH)
    )  # temp retain the creator ID for new things

    @property
    def text_edges(self) -> List[DBTextEdge]:
        """Return the cached text edges, if available"""
        if hasattr(self, "_text_edges") and self._text_edges is not None:
            return self._text_edges

        use_session = Session.object_session(self)
        assert (
            use_session is not None
        ), "Must be in-session if not cached. Otherwise call `load_edges` first"
        stmt = select(DBTextEdge).where(DBEdge.parent_id == self.db_id)
        text_edges = session.query(stmt).all()
        self._text_edges = text_edges
        return text_edges

    @property
    def node_edges(self) -> List[DBEdge]:
        """Return the cached node edges, if available"""
        if hasattr(self, "_node_edges") and self._node_edges is not None:
            return self._node_edges

        use_session = Session.object_session(self)
        assert (
            use_session is not None
        ), "Must be in-session if not cached. Otherwise call `load_edges` first"
        stmt = select(DBEdge).where(DBEdge.parent_id == self.db_id)
        text_edges = session.query(stmt).all()
        self._node_edges = node_edges
        for node_edge in node_edges:
            # Force load the children
            assert node_edge.child is not None
        return node_edges

    def load_edges(self, db: "EnvDB", skip_cache=False) -> None:
        """Expand the node and text edges for this entity"""
        if db._cache is not None and not skip_cache:
            # Load the edges from the cache
            node = db._cache["all"][self.db_id]
            self._text_edges = node.text_edges.copy()
            self._node_edges = node.node_edges.copy()
        else:
            # Load everything in a session
            with Session(db.engine) as session:
                assert self.text_edges is not None
                assert self.node_edges is not None
                session.expunge_all()


class DBAgent(DBElem, SQLBase):
    """
    Class containing the expected elements for an agent,
    with any supporting methods
    """

    __tablename__ = "agents"
    ID_PREFIX = "AGE"

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
    base_name = relationship("DBAgentName", backref="agents", foreign_keys=[base_id])

    def __repr__(self):
        return f"DBAgent({self.db_id!r}| {self.name})"


class DBObject(DBElem, SQLBase):
    """
    Class containing the expected elements for an object,
    with any supporting methods
    """

    __tablename__ = "objects"
    ID_PREFIX = "OBE"

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
    base_name = relationship("DBObjectName", backref="agents", foreign_keys=[base_id])

    def __repr__(self):
        return f"DBObject({self.db_id!r}| {self.name})"


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
    ID_PREFIX = "RME"

    base_id = Column(ForeignKey("room_names.db_id"), nullable=False)
    description = Column(String(DESCRIPTION_LENGTH_CAP), nullable=False, index=True)
    backstory = Column(String(DESCRIPTION_LENGTH_CAP), nullable=False, index=True)
    size = Column(Integer)
    indoor_status = Column(Enum(DBRoomInsideType), nullable=False)
    base_name = relationship("DBRoomName", backref="agents", foreign_keys=[base_id])

    def __repr__(self):
        return f"DBRoom({self.db_id!r}| {self.name})"


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


class DBEdgeBase(HasDBIDMixin):
    """Base attributes for an edge as stored in the environment DB"""

    db_id = Column(String(ID_STRING_LENGTH), primary_key=True)
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
    ID_PREFIX = "NED"

    # TODO function that executes this edge and gets the child
    child_id = Column(String(ID_STRING_LENGTH))

    @property
    def child(self) -> DBElem:
        """Follow this edge and load the child node"""
        if hasattr(self, "_child") and self._child is not None:
            return self.child

        use_session = Session.object_session(self)
        assert (
            use_session is not None
        ), "Must be in-session if not cached. Otherwise call `expand_edge` first"
        # Determine return type
        if DBAgent.is_id(self.child_id):
            TargetClass = DBAgent
            stmt = select(DBAgent)
        elif DBObject.is_id(self.child_id):
            TargetClass = DBObject
            stmt = select(DBObject)
        elif DBRoom.is_id(self.child_id):
            TargetClass = DBRoom
            stmt = select(DBRoom)
        else:
            raise AssertionError("Edge type was none of Agent, room, or object")
        stmt = select(TargetClass).where(TargetClass.db_id == self.child_id)
        child = session.query(stmt).one()
        self._child = child
        return child

    def expand_edge(self, db: "EnvDB") -> None:
        """Expand the node and text edges for this entity"""
        if db._cache is not None:
            # Load the edges from the cache
            node = db._cache["all"][self.child_id]
            self._child = node
        else:
            # Load everything in a session
            with Session(db.engine) as session:
                assert self.child is not None
                session.expunge_all()

    def __repr__(self):
        return (
            f"DBEdge({self.db_id!r}| {self.parent_id}-{self.edge_type}-{self.child_id})"
        )


class DBTextEdge(DBEdgeBase, SQLBase):
    """Class for edges between a GraphNodes and a new entity in the DB"""

    __tablename__ = "text_edges"
    ID_PREFIX = "TED"

    child_text = Column(String(BASE_NAME_LENGTH_CAP), nullable=False, index=True)

    def __repr__(self):
        return f"DBTextEdge({self.db_id!r}| {self.parent_id}-{self.edge_type}-{self.child_text})"


# Other


class DBEdit(SQLBase, HasDBIDMixin):
    """Suggested change to some DB content"""

    __tablename__ = "edits"
    ID_PREFIX = "EDT"

    db_id = Column(String(ID_STRING_LENGTH), primary_key=True)
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
        return f"DBEdit({self.db_id!r}| {self.node_id}-{self.field}-{self.status})"


class DBFlagTargetType(enum.Enum):
    """Types of flags"""

    FLAG_USER = "user_flag"  # Something wrong about a user's behavior
    FLAG_UTTERANCE = "utterance_flag"  # Something specifically wrong about
    FLAG_ENVIRONMENT = "env_flag"  # Flag something inappropriate in the environment


class DBFlag(SQLBase, HasDBIDMixin):
    """User-flagged content of some type"""

    __tablename__ = "flags"
    ID_PREFIX = "FLG"

    db_id = Column(String(ID_STRING_LENGTH), primary_key=True)
    flag_type = Column(Enum(DBFlagTargetType), nullable=False)
    target_id = Column(String(ID_STRING_LENGTH), nullable=False, index=True)
    reason = Column(String(REPORT_REASON_LENGTH))
    create_timestamp = Column(Float, nullable=False)

    def __repr__(self):
        return f"DBFlag({self.db_id!r}| {self.target_id}-{self.flag_type})"


class DBQuestTargetType(enum.Enum):
    """Types of quest targets"""

    TEXT_ONLY = "text_only"  # only a map from character to motivation
    SUBGOAL = "subgoal"  # Map from motivation to subgoal of motivation
    TARGET_ACTION = "target_action"  # map from motivation to target action


class DBQuest(SQLBase, HasDBIDMixin):
    """Stores quest information for breaking down motivations"""

    __tablename__ = "quests"
    ID_PREFIX = "QST"

    db_id = Column(String(ID_STRING_LENGTH), primary_key=True)
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
        return f"DBQuest({self.db_id!r}| {self.agent_id}-{self.target_type})"


class DBGraph(SQLBase, HasDBIDMixin):
    """Manifest entry for a user-saved or created graph"""

    __tablename__ = "saved_graphs"
    ID_PREFIX = "UGR"

    db_id = Column(String(ID_STRING_LENGTH), primary_key=True)
    graph_name = Column(String(WORLD_NAME_LENGTH_CAP), nulable=False, index=True)
    creator_id = Column(
        String(ID_STRING_LENGTH), nulable=False, index=True
    )  # retain the creator ID, they own this
    file_path = Column(String(FILE_PATH_LENGTH_CAP), nulable=False)
    create_timestamp = Column(Float, nullable=False)

    # TODO implement method to retrieve this graph

    # TODO implement method to write this graph to the file

    def __repr__(self):
        return f"DBGraph({self.db_id!r}| {self.graph_name})"


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
        SQLBase.metadata.create_all(self.engine)
        self._cache: Optional[Dict[str, Dict[str, Any]]] = None

    def _validate_init(self):
        """
        Ensure that the environment manifest exists, and that key
        paths are properly initialized
        """
        # TODO Check the table for any possible consistency issues
        # and ensure that all listed files actually exist

    def create_node_cache(self) -> None:
        """
        Create a local cached version of the environment nodes and
        relationships, to use for rapid construction of things
        without needing repeated queries
        """
        all_rooms = self.find_rooms()
        all_agents = self.find_agents()
        all_objects = self.find_objects()
        all_nodes = all_rooms + all_agents + all_nodes
        all_node_edges = self.get_edges()
        all_text_edges = self.get_text_edges()
        all_entities = all_nodes + all_node_edges + all_text_edges
        self._cache = {
            "rooms": {r.db_id: r for r in all_rooms},
            "nodes": {a.db_id: a for a in all_agents},
            "objects": {o.db_id: o for o in all_objects},
            "node_edges": {ne.db_id: ne for ne in all_node_edges},
            "text_edges": {te.db_id: te for te in all_text_edges},
            "all": {a.db_id: a for a in all_entities},
        }
        for node in all_nodes:
            # Load the edges skipping the cache, then resolving
            # children from the cache
            node.load_edges(self, skip_cache=True)

    def _create_name_key(
        self,
        KeyClass: Type[DBNameKey],
        name: str,
    ) -> str:
        """Idempotently create a name key for the given class"""
        with Session(self.engine) as session:
            db_id = KeyClass.get_id()
            name_key = KeyClass(
                db_id=db_id,
                name=name,
                status=DBStatus.REVIEW,
                split=DBSplitType.UNSET,
            )
            session.add(name_key)
            session.flush()
            session.commit()
        return db_id

    def _get_name_key(
        self,
        KeyClass: Type[DBNameKey],
        name: Optional[str] = None,
        db_id: Optional[str] = None,
        status: Optional[DBStatus] = None,
        split: Optional[DBSplitType] = None,
    ) -> DBNameKey:
        """Get a specific agent name, assert that it exists"""
        assert (
            name is not None or db_id is not None
        ), "Must provide one of name or db_id"
        stmt = select(KeyClass)
        if name is not None:
            stmt = stmt.where(KeyClass.name == name)
        if db_id is not None:
            assert KeyClass.is_id(db_id), "Provided ID is not for this key type"
            stmt = stmt.where(KeyClass.db_id == db_id)
        if status is not None:
            stmt = stmt.where(KeyClass.status == status)
        if split is not None:
            stmt = stmt.where(KeyClass.split == split)
        with Session(self.engine) as session:
            db_name_key = self._enforce_get_first(
                session, stmt, "Matching key didn't exist."
            )
            session.expunge_all()
            return db_name_key

    def _get_elem_by_db_id(
        self,
        ElemClass: Type[DBElem],
        db_id: str,
    ) -> DBElem:
        """Get a specific element by ID, asserting that it exists"""
        assert ElemClass.is_id(db_id), f"Given id {db_id} not for {ElemClass}"
        stmt = select(ElemClass).where(ElemClass.db_id == db_id)
        with Session(self.engine) as session:
            db_elem = self._enforce_get_first(
                session, stmt, f"No {ElemClass} by given key {db_id}"
            )
            session.expunge_all()
            return db_elem

    # Agents

    def create_agent_name(self, name: str) -> str:
        """Create a new agent name in the database"""
        return self._create_name_key(DBAgentName, name)

    def get_agent_name(
        self,
        name: Optional[str] = None,
        db_id: Optional[str] = None,
        status: Optional[DBStatus] = None,
        split: Optional[DBSplitType] = None,
    ) -> DBAgentName:
        """Get a specific agent name, assert that it exists"""
        return cast(
            DBAgentName,
            self._get_name_key(
                KeyClass=DBAgentName,
                name=name,
                db_id=db_id,
                status=status,
                split=split,
            ),
        )

    def create_agent_entry(
        self,
        name: str,
        base_name: str,
        persona: str,
        physical_description: str,
        name_prefix: str = "a",
        is_plural: Optional[bool] = None,
        size: Optional[int] = None,
        contain_size: Optional[int] = None,
        constitution: Optional[int] = None,
        charisma: Optional[int] = None,
        strength: Optional[int] = None,
        dexterity: Optional[int] = None,
        intelligence: Optional[int] = None,
        wisdom: Optional[int] = None,
        status: DBStatus = DBStatus.REVIEW,
        creator_id: Optional[str] = None,
    ) -> str:
        """Create this agent, making an agent name first if required"""
        base_id = self.create_agent_name(base_name, creator_id)
        with Session(self.engine) as session:
            db_id = DBAgent.get_id()
            agent = DBAgent(
                db_id=db_id,
                base_id=base_id,
                status=status,
                creator_id=creator_id,
                create_timestamp=time.time(),
                name=name,
                persona=persona,
                physical_description=physical_description,
                name_prefix=name_prefix,
                is_plural=is_plural,
                size=size,
                contain_size=contain_size,
                constitution=constitution,
                charisma=charisma,
                dexterity=dexterity,
                intelligence=intelligence,
                wisdom=wisdom,
            )
            session.add(agent)
            session.flush()
            session.commit()
        return db_id

    def find_agents(
        self,
        base_id: Optional[str] = None,
        name: Optional[str] = None,
        persona: Optional[str] = None,
        physical_description: Optional[str] = None,
        name_prefix: Optional[str] = None,
        is_plural: Optional[bool] = None,
        status: Optional[DBStatus] = None,
        split: Optional[DBSplitType] = None,
        creator_id: Optional[str] = None,
    ) -> List[DBAgent]:
        """Return all agents matching the given parameters"""
        # Construct query
        stmt = select(DBAgent)
        if base_id is not None:
            stmt = stmt.where(DBAgent.base_id == base_id)
        if name is not None:
            stmt = stmt.where(DBAgent.name == name)
        if persona is not None:
            stmt = stmt.where(DBAgent.persona == persona)
        if physical_description is not None:
            stmt = stmt.where(DBAgent.physical_description == physical_description)
        if name_prefix is not None:
            stmt = stmt.where(DBAgent.name_prefix == name_prefix)
        if is_plural is not None:
            stmt = stmt.where(DBAgent.is_plural == is_plural)
        if status is not None:
            stmt = stmt.where(DBAgent.status == status)
        if split is not None:
            # Need to join up to parent for split query
            stmt = stmt.select_from(join(DBAgent, DBAgentName, DBAgent.base_id)).where(
                DBAgentName.split == split
            )
        if creator_id is not None:
            stmt = stmt.where(DBAgent.creator_id == creator_id)
        # Do query
        with Session(self.engine) as session:
            agents = session.query(stmt).all()
            session.expunge_all()
            return agents

    def get_agent(self, db_id: str) -> DBAgent:
        """Return the given agent, raise an exception if non-existing"""
        return cast(DBAgent, self._get_elem_by_db_id(DBAgent, db_id))

    # Objects

    def create_object_name(self, name: str) -> str:
        """Create a new object name in the database"""
        return self._create_name_key(DBObjectName, name)

    def get_object_name(
        self,
        name: Optional[str] = None,
        db_id: Optional[str] = None,
        status: Optional[DBStatus] = None,
        split: Optional[DBSplitType] = None,
    ) -> DBObjectName:
        """Get a specific object name, assert that it exists"""
        return cast(
            DBObjectName,
            self._get_name_key(
                KeyClass=DBObjectName,
                name=name,
                db_id=db_id,
                status=status,
                split=split,
            ),
        )

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
        is_plural: Optional[bool] = None,
        size: Optional[int] = None,
        contain_size: Optional[int] = None,
        value: Optional[float] = None,
        rarity: Optional[float] = None,
        status: DBStatus = DBStatus.REVIEW,
        creator_id: Optional[str] = None,
    ) -> str:
        """Create a new object, making a object_name first if required"""
        base_id = self.create_object_name(base_name, creator_id)
        with Session(self.engine) as session:
            db_id = DBObject.get_id()
            agent = DBObject(
                db_id=db_id,
                base_id=base_id,
                status=status,
                creator_id=creator_id,
                create_timestamp=time.time(),
                name=name,
                physical_description=physical_description,
                is_container=is_container,
                is_drink=is_drink,
                is_food=is_food,
                is_gettable=is_gettable,
                is_surface=is_surface,
                is_wearable=is_wearable,
                is_weapon=is_weapon,
                name_prefix=name_prefix,
                is_plural=is_plural,
                size=size,
                contain_size=contain_size,
                value=value,
                rarity=rarity,
            )
            session.add(agent)
            session.flush()
            session.commit()
        return db_id

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
        is_plural: Optional[bool] = None,
        status: Optional[DBStatus] = None,
        split: Optional[DBSplitType] = None,
        creator_id: Optional[str] = None,
    ) -> List["DBObject"]:
        """Return all objects matching the given parameters"""
        FLOAT_TRUE_THRESHOLD = 0.5
        # Construct query
        stmt = select(DBObject)
        if base_id is not None:
            stmt = stmt.where(DBObject.base_id == base_id)
        if name is not None:
            stmt = stmt.where(DBObject.name == name)
        if physical_description is not None:
            stmt = stmt.where(DBObject.physical_description == physical_description)
        if is_container is not None:
            if is_container:
                stmt = stmt.where(DBObject.is_container >= FLOAT_TRUE_THRESHOLD)
            else:
                stmt = stmt.where(DBObject.is_container < FLOAT_TRUE_THRESHOLD)
        if is_drink is not None:
            if is_drink:
                stmt = stmt.where(DBObject.is_drink >= FLOAT_TRUE_THRESHOLD)
            else:
                stmt = stmt.where(DBObject.is_drink < FLOAT_TRUE_THRESHOLD)
        if is_food is not None:
            if is_food:
                stmt = stmt.where(DBObject.is_food >= FLOAT_TRUE_THRESHOLD)
            else:
                stmt = stmt.where(DBObject.is_food < FLOAT_TRUE_THRESHOLD)
        if is_gettable is not None:
            if is_gettable:
                stmt = stmt.where(DBObject.is_gettable >= FLOAT_TRUE_THRESHOLD)
            else:
                stmt = stmt.where(DBObject.is_gettable < FLOAT_TRUE_THRESHOLD)
        if is_surface is not None:
            if is_surface:
                stmt = stmt.where(DBObject.is_surface >= FLOAT_TRUE_THRESHOLD)
            else:
                stmt = stmt.where(DBObject.is_surface < FLOAT_TRUE_THRESHOLD)
        if is_wearable is not None:
            if is_wearable:
                stmt = stmt.where(DBObject.is_wearable >= FLOAT_TRUE_THRESHOLD)
            else:
                stmt = stmt.where(DBObject.is_wearable < FLOAT_TRUE_THRESHOLD)
        if is_weapon is not None:
            if is_weapon:
                stmt = stmt.where(DBObject.is_weapon >= FLOAT_TRUE_THRESHOLD)
            else:
                stmt = stmt.where(DBObject.is_weapon < FLOAT_TRUE_THRESHOLD)
        if name_prefix is not None:
            stmt = stmt.where(DBObject.name_prefix == name_prefix)
        if is_plural is not None:
            stmt = stmt.where(DBObject.is_plural == is_plural)
        if status is not None:
            stmt = stmt.where(DBObject.status == status)
        if split is not None:
            # Need to join up to parent for split query
            stmt = stmt.select_from(
                join(DBObject, DBObjectName, DBObject.base_id)
            ).where(DBObjectName.split == split)
        if creator_id is not None:
            stmt = stmt.where(DBObject.creator_id == creator_id)
        # Do query
        with Session(self.engine) as session:
            objects = session.query(stmt).all()
            session.expunge_all()
            return objects

    def get_object(self, db_id: str) -> DBObject:
        """Return the given object, raise exception if non-existing"""
        return cast(DBObject, self._get_elem_by_db_id(DBObject, db_id))

    # Rooms

    def create_room_name(self, name: str) -> str:
        """Create a new room name in the database"""
        return self._create_name_key(DBRoomName, name)

    def get_room_name(
        self,
        name: Optional[str] = None,
        db_id: Optional[str] = None,
        status: Optional[DBStatus] = None,
        split: Optional[DBSplitType] = None,
    ) -> DBRoomName:
        """Get a specific room name, assert that it exists"""
        return cast(
            DBRoomName,
            self._get_name_key(
                KeyClass=DBRoomName,
                name=name,
                db_id=db_id,
                status=status,
                split=split,
            ),
        )

    def create_room_entry(
        self,
        name: str,
        description: str,
        backstory: str,
        size: Optional[int] = None,
        indoor_status: Optional[DBRoomInsideType] = None,
        rarity: Optional[float] = None,
        status: DBStatus = DBStatus.REVIEW,
        creator_id: Optional[str] = None,
    ) -> str:
        """Create a new room, making a room name first if required"""
        base_id = self.create_object_name(base_name, creator_id)
        with Session(self.engine) as session:
            db_id = DBObject.get_id()
            agent = DBObject(
                db_id=db_id,
                base_id=base_id,
                status=status,
                creator_id=creator_id,
                create_timestamp=time.time(),
                name=name,
                description=description,
                backstory=backstory,
                size=size,
                indoor_status=indoor_status,
                rarity=rarity,
            )
            session.add(agent)
            session.flush()
            session.commit()
        return db_id

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
        # Construct query
        stmt = select(DBRoom)
        if base_id is not None:
            stmt = stmt.where(DBRoom.base_id == base_id)
        if name is not None:
            stmt = stmt.where(DBRoom.name == name)
        if description is not None:
            stmt = stmt.where(DBRoom.description == description)
        if backstory is not None:
            stmt = stmt.where(DBRoom.backstory == backstory)
        if indoor_status is not None:
            stmt = stmt.where(DBRoom.indoor_status == indoor_status)
        if status is not None:
            stmt = stmt.where(DBRoom.status == status)
        if split is not None:
            # Need to join up to parent for split query
            stmt = stmt.select_from(join(DBRoom, DBRoomName, DBRoom.base_id)).where(
                DBRoomName.split == split
            )
        if creator_id is not None:
            stmt = stmt.where(DBRoom.creator_id == creator_id)
        # Do query
        with Session(self.engine) as session:
            rooms = session.query(stmt).all()
            session.expunge_all()
            return rooms

    def get_room(self, db_id: str) -> DBRoom:
        """Get a specific room, assert that it exists"""
        return cast(DBRoom, self._get_elem_by_db_id(DBRoom, db_id))

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
