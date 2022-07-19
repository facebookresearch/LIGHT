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

FILE_PATH_KEY = "env"
GRAPH_PATH_KEY = "graphs"
QUEST_PATH_KEY = "quests"

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

    ID_PREFIX: int  # ID prefix should be 3 characters max.

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
        text_edges = use_session.query(stmt).all()
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
        text_edges = use_session.query(stmt).all()
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

    @property
    def attributes(self) -> List[DBNodeAttribute]:
        if hasattr(self, "_attributes") and self._attributes is not None:
            return self._attributes

        use_session = Session.object_session(self)
        assert (
            use_session is not None
        ), "Must be in-session if not cached. Otherwise call `load_attributes` first"
        stmt = select(DBNodeAttribute).where(DBNodeAttribute.target_id == self.db_id)
        attributes = use_session.query(stmt).all()
        self._attributes = attributes
        return attributes

    def load_attributes(self, db: "EnvDB", skip_cache=False) -> None:
        """Expand arbitrary attributes for this node"""
        if db._cache is not None and not skip_cache:
            # Load the edges from the cache
            node = db._cache["all"][self.db_id]
            self._attributes = node.attributes.copy()
        else:
            # Load everything in a session
            with Session(db.engine) as session:
                assert self.attributes is not None
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


class DBNodeAttribute(HasDBIDMixin, SQLBase):
    """
    Class containing unique attribute values for specific element instances
    """

    __tablename__ = "node_attributes"
    ID_PREFIX = "ATT"

    db_id = Column(String(ID_STRING_LENGTH), primary_key=True)
    target_id = Column(String(ID_STRING_LENGTH), nullable=False, index=True)
    attribute_name = Column(String(EDGE_LABEL_LENGTH_CAP), nullable=False, index=True)
    attribute_value_string = Column(String(EDGE_LABEL_LENGTH_CAP), nullable=False)
    status: DBStatus = Column(Enum(DBStatus), nullable=False, index=True)
    creator_id = Column(
        String(ID_STRING_LENGTH)
    )  # temp retain the creator ID for new things


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
    parent_id = Column(String(ID_STRING_LENGTH), nullable=False)
    edge_type = Column(Enum(DBEdgeType), nullable=False)
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

    child_id = Column(String(ID_STRING_LENGTH))
    built_occurrences = Column(Integer, nullable=False, default=0)

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
        # This may be better wrapped as a utility of EnvDB,
        # but that's not in-scope here
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
        child = use_session.query(stmt).one()
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
    """Suggested change to some DBElem content"""

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

    def accept_and_apply(self, db: EnvDB) -> None:
        """Accept and apply the given edit"""
        # TODO Implement
        raise NotImplementedError

    def reject_edit(self, db: EnvDB) -> None:
        """Reject the given edit"""
        with Session(db.engine) as session:
            edit = session.query(DBEdit).get(self.db_id)
            edit.status = DBStatus.REJECTED
            session.flush()
            session.commit()
            session.expunge_all()
            self.status = DBStatus.REJECTED

    def __repr__(self):
        return f"DBEdit({self.db_id!r}| {self.node_id}-{self.field}-{self.status})"


class DBFlagTargetType(enum.Enum):
    """Types of flags"""

    FLAG_USER = "user_flag"  # Something wrong about a user's behavior
    FLAG_UTTERANCE = "utterance_flag"  # Something specifically wrong about
    FLAG_ENVIRONMENT = "env_flag"  # Flag something inappropriate in the environment


class DBFlag(HasDBIDMixin, SQLBase):
    """User-flagged content of some type"""

    __tablename__ = "flags"
    ID_PREFIX = "FLG"

    db_id = Column(String(ID_STRING_LENGTH), primary_key=True)
    flag_type = Column(Enum(DBFlagTargetType), nullable=False)
    target_id = Column(String(ID_STRING_LENGTH), nullable=False, index=True)
    reason = Column(String(REPORT_REASON_LENGTH))
    status = Column(Enum(DBStatus), nullable=False, index=True)
    create_timestamp = Column(Float, nullable=False)

    def __repr__(self):
        return f"DBFlag({self.db_id!r}| {self.target_id}-{self.flag_type})"


class DBQuestTargetType(enum.Enum):
    """Types of quest targets"""

    TEXT_ONLY = "text_only"  # only a map from character to motivation
    TARGET_ACTION = "target_action"  # map from motivation to target action


class DBQuest(SQLBase, HasDBIDMixin):
    """Stores quest information for breaking down motivations"""

    __tablename__ = "quests"
    ID_PREFIX = "QST"

    db_id = Column(String(ID_STRING_LENGTH), primary_key=True)
    agent_id = Column(ForeignKey("agents.db_id"), nullable=False)
    parent_id = Column(ForeignKey("quests.db_id"))  # Map to possible parent
    text_motivation = Column(String(QUEST_MOTIVATION_LENGTH), nullable=False)
    target_type = Column(Enum(DBQuestTargetType), nullable=False)
    target = Column(String(QUEST_MOTIVATION_LENGTH))
    status = Column(Enum(DBStatus), nullable=False, index=True)
    origin_filepath = Column(String(FILE_PATH_LENGTH_CAP))
    creator_id = Column(
        String(ID_STRING_LENGTH)
    )  # temp retain the creator ID for new things
    create_timestamp = Column(Float, nullable=False)

    @property
    def subgoals(self) -> List[DBQuest]:
        """
        Return the list of DBQuests that are a direct
        subgoal of this one
        """
        if hasattr(self, "_subgoals") and self._subgoals is not None:
            return self._subgoals

        use_session = Session.object_session(self)
        assert (
            use_session is not None
        ), "Must be in-session if not cached. Otherwise call `load_relations` first"

        subgoals = use_session.query(DBQuest).where(DBQuest.parent_id == self.db_id)
        self._subgoals = subgoals
        return subgoals

    @property
    def parent_chain(self) -> List[DBQuest]:
        """
        Return the chain of quests/motivations above this level,
        starting from the highest down to this one
        """
        if hasattr(self, "_parent_chain") and self._parent_chain is not None:
            return self._parent_chain

        use_session = Session.object_session(self)
        assert (
            use_session is not None
        ), "Must be in-session if not cached. Otherwise call `load_relations` first"

        parent_chain = [self]
        curr_item = self
        while curr_item.parent_id is not None:
            parent_item = use_session.query(DBQuest).get(curr_item.parent_id)
            parent_chain.append(parent_item)
            curr_item = parent_item
        parent_chain = reversed(parent_chain)

        self._parent_chain = parent_chain
        return parent_chain

    def load_relations(self, db: "EnvDB") -> None:
        """Expand the parent chain and subgoals for this item"""
        # Load everything in a session
        with Session(db.engine) as session:
            assert self.parent_chain is not None
            # Recurse through subgoals to load entire chain
            subgoals_to_check = self.subgoals.copy()
            while len(subgoals_to_check) > 0:
                next_goal = subgoals_to_check.pop()
                subgoals_to_check += next_goal.subgoals.copy()
            session.expunge_all()

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
    status = Column(Enum(DBStatus), nullable=False, index=True)
    create_timestamp = Column(Float, nullable=False)

    def get_graph(self, db: EnvDB) -> OOGraph:
        """Get an OOGraph for this DBGraph, loading from file"""
        graph_json = db.read_data_from_file(self.file_path, json_encoded=False)
        graph = OOGraph.from_json(graph_json)
        return graph

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
        # TODO we can use the cache in more of the core DB functions
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
            node._attributes = []

        # manually link the attributes in a single pass
        all_attributes = self.get_attributes()
        for attribute in attributes:
            self._cache["all"][attribute.target_id]._attributes.append(attribute)

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

    def _resolve_id_to_db_elem(
        self,
        db_id: str,
    ) -> DBElem:
        """Query for the correct DBElem given the provided db_id"""
        if DBAgent.is_id(db_id):
            TargetClass = DBAgent
            stmt = select(DBAgent)
        elif DBObject.is_id(db_id):
            TargetClass = DBObject
            stmt = select(DBObject)
        elif DBRoom.is_id(db_id):
            TargetClass = DBRoom
            stmt = select(DBRoom)
        else:
            raise AssertionError("Edge type was none of Agent, room, or object")
        return self._get_elem_for_class(TargetClass, db_id)

    def _get_elem_for_class(
        self,
        ElemClass: Type[DBElem],
        db_id: str,
    ) -> DBElem:
        """Get a specific element of the given class by ID, asserting that it exists"""
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
        return cast(DBAgent, self._get_elem_for_class(DBAgent, db_id))

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
        return cast(DBObject, self._get_elem_for_class(DBObject, db_id))

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
        return cast(DBRoom, self._get_elem_for_class(DBRoom, db_id))

    # Attributes

    def create_arbitrary_attribute(
        self,
        target_id: str,
        attribute_name: str,
        attribute_value_string: str,
        status: DBStatus = DBStatus.REVIEW,
        creator_id: Optional[str] = None,
    ) -> str:
        """Create an arbitrary attribute entry for the target node"""
        with Session(self.engine) as session:
            db_id = DBNodeAttribute.get_id()
            attribute = DBNodeAttribute(
                db_id=db_id,
                target_id=target_id,
                attribute_name=attribute_name,
                attribute_value_string=attribute_value_string,
                status=status,
                creator_id=creator_id,
            )
            session.add(attribute)
            session.flush()
            session.commit()
        return db_id

    def get_attributes(
        self,
        target_id: Optional[str] = None,
        attribute_name: Optional[str] = None,
        attribute_value_string: Optional[str] = None,
        status: Optional[DBStatus] = None,
        creator_id: Optional[str] = None,
    ) -> List[DBNodeAttribute]:
        """Return the list of all attributes stored that match the given filters"""
        # Construct query
        stmt = select(DBNodeAttribute)
        if target_id is not None:
            stmt = stmt.where(DBNodeAttribute.target_id == target_id)
        if attribute_name is not None:
            stmt = stmt.where(DBNodeAttribute.attribute_name == attribute_name)
        if attribute_value_string is not None:
            stmt = stmt.where(
                DBNodeAttribute.attribute_value_string == attribute_value_string
            )
        if status is not None:
            stmt = stmt.where(DBNodeAttribute.status == status)
        if creator_id is not None:
            stmt = stmt.where(DBNodeAttribute.creator_id == creator_id)
        # Do query
        with Session(self.engine) as session:
            attributes = session.query(stmt).all()
            session.expunge_all()
            return attributes

    # Edges

    def create_edge(
        self,
        parent_id: str,
        child_id: str,
        edge_type: str,
        edge_label: Optional[str] = None,
        status: DBStatus = DBStatus.REVIEW,
        creator_id: Optional[str] = None,
    ) -> str:
        """Create an edge between two nodes"""
        with Session(self.engine) as session:
            db_id = DBEdge.get_id()
            edge = DBEdge(
                db_id=db_id,
                parent_id=parent_id,
                edge_type=edge_type,
                edge_label=edge_label,
                status=status,
                creator_id=creator_id,
                create_timestamp=time.time(),
                child_id=child_id,
            )
            session.add(edge)
            session.flush()
            session.commit()
        return db_id

    def get_edges(
        self,
        parent_id: Optional[str] = None,
        child_id: Optional[str] = None,
        edge_type: Optional[str] = None,
        status: Optional[DBStatus] = None,
        creator_id: Optional[str] = None,
        min_strength: Optional[float] = 0,
    ) -> List[DBEdge]:
        """Return all edges matching the given parameters"""
        # Construct query
        stmt = select(DBEdge)
        if parent_id is not None:
            stmt = stmt.where(DBEdge.parent_id == parent_id)
        if child_id is not None:
            stmt = stmt.where(DBEdge.child_id == child_id)
        if edge_type is not None:
            stmt = stmt.where(DBEdge.edge_type == edge_type)
        if status is not None:
            stmt = stmt.where(DBEdge.status == status)
        if creator_id is not None:
            stmt = stmt.where(DBEdge.creator_id == creator_id)
        # Do query
        with Session(self.engine) as session:
            edges = session.query(stmt).all()
            if min_strength is not None:
                # Need to post-filter out things below the min strength, where
                # strength is defined as the proportion of edge occurrences to
                # parent occurrences
                filtered_edges = []
                for edge in edges:
                    edge_occurrences = edge.built_occurrences
                    if edge_occurrences == 0:
                        continue  # No occurrences of edge
                    db_elem = self._resolve_id_to_db_elem(edge.parent_id)
                    elem_occurrences = db_elem.built_occurrences
                    if elem_occurrences == 0:
                        continue  # No occurrences of elem
                    if edge_occurrences / elem_occurrences >= min_strength:
                        filtered_edges.append(edge)
                edges = filtered_edges
            session.expunge_all()
            return edges

    def create_text_edge(
        self,
        parent_id: str,
        child_text: str,
        edge_type: str,
        edge_label: Optional[str] = None,
        status: DBStatus = DBStatus.REVIEW,
        creator_id: Optional[str] = None,
    ) -> str:
        """Create an edge between a node and the name of a possible leaf"""
        with Session(self.engine) as session:
            db_id = DBTextEdge.get_id()
            edge = DBTextEdge(
                db_id=db_id,
                parent_id=parent_id,
                edge_type=edge_type,
                edge_label=edge_label,
                status=status,
                creator_id=creator_id,
                create_timestamp=time.time(),
                child_text=child_text,
            )
            session.add(edge)
            session.flush()
            session.commit()
        return db_id

    def get_text_edges(
        self,
        parent_id: Optional[str] = None,
        child_text: Optional[str] = None,
        edge_type: Optional[str] = None,
        status: Optional[DBStatus] = None,
        creator_id: Optional[str] = None,
    ) -> List[DBTextEdge]:
        """Return all text edges matching the given parameters"""
        # Construct query
        stmt = select(DBTextEdge)
        if parent_id is not None:
            stmt = stmt.where(DBTextEdge.parent_id == parent_id)
        if child_text is not None:
            stmt = stmt.where(DBTextEdge.child_text == child_text)
        if edge_type is not None:
            stmt = stmt.where(DBTextEdge.edge_type == edge_type)
        if status is not None:
            stmt = stmt.where(DBTextEdge.status == status)
        if creator_id is not None:
            stmt = stmt.where(DBTextEdge.creator_id == creator_id)
        # Do query
        with Session(self.engine) as session:
            edges = session.query(stmt).all()
            session.expunge_all()
            return edges

    # Flags and edits

    def create_edit(
        self,
        editor_id: str,
        node_id: str,
        field: str,
        old_value: str,
        new_value: str,
        status: Optional[DBStatus] = DBStatus.REVIEW,
    ) -> str:
        """Write a potential edit to db. Return the edit db_id"""
        with Session(self.engine) as session:
            db_id = DBEdit.get_id()
            edge = DBEdit(
                db_id=db_id,
                editor_id=editor_id,
                node_id=node_id,
                field=field,
                old_value=old_value,
                new_value=new_value,
                status=status,
                create_timestamp=time.time(),
            )
            session.add(edge)
            session.flush()
            session.commit()
        return db_id

    def get_edits(
        self,
        editor_id: Optional[str] = None,
        node_id: Optional[str] = None,
        field: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        status: Optional[DBStatus] = None,
    ) -> List[DBEdit]:
        """Return all edits matching the given parameters"""
        # Construct query
        stmt = select(DBEdit)
        if editor_id is not None:
            stmt = stmt.where(DBEdit.editor_id == editor_id)
        if node_id is not None:
            stmt = stmt.where(DBEdit.node_id == node_id)
        if field is not None:
            stmt = stmt.where(DBEdit.field == field)
        if old_value is not None:
            stmt = stmt.where(DBEdit.old_value == old_value)
        if new_value is not None:
            stmt = stmt.where(DBEdit.new_value == new_value)
        if status is not None:
            stmt = stmt.where(DBEdit.status == status)
        # Do query
        with Session(self.engine) as session:
            edits = session.query(stmt).all()
            session.expunge_all()
            return edits

    def flag_entry(
        self,
        user_id: str,
        flag_type: DBFlagTargetType,
        target_id: str,
        reason: str,
        status: Optional[DBStatus] = DBStatus.REVIEW,
    ) -> str:
        """
        Write a potential flag to db, return the flag id
        """
        with Session(self.engine) as session:
            db_id = DBFlag.get_id()
            flag = DBFlag(
                db_id=db_id,
                flag_type=flag_type,
                target_id=target_id,
                reason=reason,
                status=status,
                create_timestamp=time.time(),
            )
            session.add(flag)
            session.flush()
            session.commit()
            # TODO enough flags could perhaps move node to review status
        return db_id

    def get_flags(
        self,
        user_id: Optional[str] = None,
        flag_type: Optional[DBFlagTargetType] = None,
        target_id: Optional[str] = None,
        reason: Optional[str] = None,
        status: Optional[DBStatus] = None,
    ) -> List[DBFlag]:
        """Return all flags matching the given parameters"""
        # Construct query
        stmt = select(DBFlag)
        if user_id is not None:
            stmt = stmt.where(DBFlag.user_id == user_id)
        if flag_type is not None:
            stmt = stmt.where(DBFlag.flag_type == flag_type)
        if target_id is not None:
            stmt = stmt.where(DBFlag.target_id == target_id)
        if reason is not None:
            stmt = stmt.where(DBFlag.reason == reason)
        if status is not None:
            stmt = stmt.where(DBFlag.status == status)
        # Do query
        with Session(self.engine) as session:
            flags = session.query(stmt).all()
            session.expunge_all()
            return flags

    # Quests

    def create_quest(
        self,
        agent_id: str,
        text_motivation: str,
        target_type: str,
        target: str,
        parent_id: Optional[str] = None,
        status: DBStatus = DBStatus.REVIEW,
        creator_id: Optional[str] = None,
    ) -> str:
        """
        Creates a Quest, which is a mapping from character and motivation
        text to a desired action or list of subquests
        """
        with Session(self.engine) as session:
            db_id = DBQuest.get_id()
            quest = DBQuest(
                db_id=db_id,
                agent_id=agent_id,
                parent_id=parent_id,
                text_motivation=text_motivation,
                target_type=target_type,
                target=target,
                origin_filepath=origin_filepath,
                status=status,
                creator_id=creator_id,
                create_timestamp=time.time(),
            )
            session.add(quest)
            session.flush()
            session.commit()
        return db_id

    def find_quests(
        self,
        agent_id: Optional[str] = None,
        text_motivation: Optional[str] = None,
        target_type: Optional[str] = None,
        target: Optional[str] = None,
        status: Optional[DBStatus] = None,
        creator_id: Optional[str] = None,
    ) -> List[DBQuest]:
        """Return all text edges matching the given parameters"""
        # Construct query
        stmt = select(DBQuest)
        if agent_id is not None:
            stmt = stmt.where(DBQuest.agent_id == agent_id)
        if text_motivation is not None:
            stmt = stmt.where(DBQuest.text_motivation == text_motivation)
        if target_type is not None:
            stmt = stmt.where(DBQuest.target_type == target_type)
        if target is not None:
            stmt = stmt.where(DBQuest.target == target)
        if new_value is not None:
            stmt = stmt.where(DBQuest.new_value == new_value)
        if status is not None:
            stmt = stmt.where(DBQuest.status == status)
        if creator_id is not None:
            stmt = stmt.where(DBQuest.creator_id == creator_id)
        # Do query
        with Session(self.engine) as session:
            quests = session.query(stmt).all()
            session.expunge_all()
            return quests

    # Graphs

    def save_graph(self, graph: "OOGraph", creator_id: str) -> str:
        """Save this graph to a file for the given user"""
        # Find or assign a db_id for this graph
        if hasattr(graph, "db_id") and graph.db_id is not None:
            db_id = graph.db_id
        else:
            db_id = DBGraph.get_id()
            graph.db_id = db_id

        dump_file_path = os.path.join(FILE_PATH_KEY, GRAPH_PATH_KEY, f"{db_id}.json")

        for graph_info in graphs:
            graph_full_path = os.path.join(graph_dump_root, graph_info["filename"])
            self.write_data_to_file(graph_info["graph_json"], graph_full_path)

        # Create or update the graph
        with Session(self.engine) as session:
            db_graph = session.query(DBGraph).get(db_id)
            if db_graph is not None:
                # Update old graph, ensure same creator
                assert db_graph.creator_id == creator_id, (
                    f"Creator ID mismatch on {db_id}, current "
                    f"{db_graph.creator_id} and new {creator_id}"
                )
                self.write_data_to_file(
                    graph.to_json(), dump_file_path, json_encode=False
                )
            else:
                # New graph
                db_graph = DBGraph(
                    db_id=db_id,
                    graph_name=graph.title,
                    creator_id=creator_id,
                    file_path=dump_file_path,
                    status=DBStatus.REVIEW,
                    create_timestamp=time.time(),
                )
                session.add(db_graph)
                self.write_data_to_file(
                    graph.to_json(), dump_file_path, json_encode=False
                )
            session.flush()
            session.commit()
        return db_id

    def load_graph(self, graph_id: str) -> DBGraph:
        """Return the queried graph, raising if nonexistent"""
        with Session(self.engine) as session:
            db_graph = session.query(DBGraph).get(db_id)
            if db_graph is None:
                raise KeyError(f"Graph key {db_id} didn't exist!")
            session.expunge_all()
            return db_graph

    def find_graphs(
        self,
        graph_name: Optional[str] = None,
        creator_id: Optional[str] = None,
        # ... TODO can add other search attributes?
    ) -> List[DBGraph]:
        """Return all graphs matching the provided parameters"""
        # Construct query
        stmt = select(DBGraph)
        if graph_name is not None:
            stmt = stmt.where(DBGraph.graph_name == graph_name)
        if creator_id is not None:
            stmt = stmt.where(DBGraph.creator_id == creator_id)
        # Do query
        with Session(self.engine) as session:
            db_graphs = session.query(stmt).all()
            session.expunge_all()
            return db_graphs
