#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from light.data_model.db.base import BaseDB, DBStatus, DBSplitType, HasDBIDMixin
from light.data_model.db.users import DBPlayer
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
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship, Session
from light.graph.events.base import GraphEvent
import time
import enum
import os
import hashlib

if TYPE_CHECKING:
    from light.graph.structured_graph import OOGraph

SQLBase = declarative_base()
FILE_PATH_KEY = "episodes"
ID_STRING_LENGTH = 40
USR_KEY = DBPlayer.ID_PREFIX
MAX_WILD_MODEL_LEN = 200
MAX_WILD_CHOICE_LEN = 100


class DBGroupName(enum.Enum):
    """Data Releases in the LIGHT episode DB"""

    ORIG = "orig"
    WILD = "wild"
    MULTIPARTY = "multiparty"
    PRE_LAUNCH = "crowdsourced"
    PRE_LAUNCH_TUTORIAL = "crowdsourced_tutorial"
    RELEASE_Q4_22 = "full_release_Q4_22"


class EpisodeLogType(enum.Enum):
    """Types of episodes in LIGHT"""

    ROOM = "room"
    AGENT = "agent"
    FULL = "full"


class DBEpisode(HasDBIDMixin, SQLBase):
    """Class containing the expected elements for an episode as stored in the db"""

    __tablename__ = "episodes"

    ID_PREFIX = "EPI"

    id = Column(String(ID_STRING_LENGTH), primary_key=True)
    group = Column(Enum(DBGroupName), nullable=False, index=True)
    split = Column(Enum(DBSplitType), nullable=False, index=True)
    status = Column(Enum(DBStatus), nullable=False, index=True)
    actors = Column(
        String
    )  # Comma separated list of actor IDs. Cleared on release data
    dump_file_path = Column(String(90), nullable=False)  # Path to data
    turn_count = Column(Integer, nullable=False)
    human_count = Column(Integer, nullable=False)
    action_count = Column(Integer, nullable=False)
    timestamp = Column(Float, nullable=False)
    log_type = Column(Enum(EpisodeLogType), nullable=False)
    first_graph_id = Column(ForeignKey("graphs.id"))
    final_graph_id = Column(ForeignKey("graphs.id"))

    _cached_map = None

    def get_actors(self) -> List[str]:
        """Return the actors in this episode"""
        if len(self.actors.strip()) == 0:
            return []
        return self.actors.split(",")

    def get_parsed_events(
        self, db: "EpisodeDB"
    ) -> List[Tuple[str, List["GraphEvent"]]]:
        """
        Return all of the actions and turns from this episode,
        split by the graph key ID relevant to those actions
        """
        # Import deferred as World imports loggers which import the EpisodeDB
        from light.world.world import World, WorldConfig

        events = db.read_data_from_file(self.dump_file_path, json_encoded=True)[
            "events"
        ]
        graph_grouped_events: List[Tuple[str, List["GraphEvent"]]] = []
        current_graph_events = None
        curr_graph_key = None
        curr_graph = None
        tmp_world = None
        # Extract events to the correct related graphs, initializing the graphs
        # as necessary
        for event_turn in events:
            # See if we've moved onto an event in a new graph
            if event_turn["graph_key"] != curr_graph_key:
                if current_graph_events is not None:
                    # There was old state, so lets push it to the list
                    graph_grouped_events.append((curr_graph_key, current_graph_events))
                # We're on a new graph, have to reset the current graph state
                curr_graph_key = event_turn["graph_key"]
                current_graph_events: List["GraphEvent"] = []
                curr_graph = self.get_graph(curr_graph_key, db)
                tmp_world = World(WorldConfig())
                tmp_world.oo_graph = curr_graph
            # The current turn is part of the current graph's events, add
            current_graph_events.append(
                GraphEvent.from_json(event_turn["event_json"], tmp_world)
            )
        if current_graph_events is not None:
            # Push the last graph's events, which weren't yet added
            graph_grouped_events.append((curr_graph_key, current_graph_events))
        return graph_grouped_events

    def get_before_graph(self, db: "EpisodeDB") -> "OOGraph":
        """Return the state of the graph before this episode"""
        return self.get_graph(self.first_graph_id, db)

    def get_graph(self, id_or_key: str, db: "EpisodeDB") -> "OOGraph":
        """Return a specific graph by id or key"""
        with Session(db.engine) as session:
            session.add(self)
            return self.get_graph_map()[id_or_key].get_graph(db)

    def get_after_graph(self, db: "EpisodeDB") -> "OOGraph":
        """Return the state of the graph after this episode"""
        return self.get_graph(self.final_graph_id, db)

    def get_graph_map(self):
        """Return a mapping from both graph keys and graph ids to their graph"""
        if self._cached_map is None:
            key_map = {graph.graph_key_id: graph for graph in self.graphs}
            id_map = {graph.id: graph for graph in self.graphs}
            key_map.update(id_map)
            self._cached_map = key_map
        return self._cached_map

    def __repr__(self):
        return f"DBEpisode(ids:[{self.id!r}] group/split:[{self.group.value!r}/{self.split.value!r}] File:[{self.dump_file_path!r}])"


class DBEpisodeGraph(HasDBIDMixin, SQLBase):
    """Class containing expected elements for a stored graph"""

    __tablename__ = "graphs"

    ID_PREFIX = "EPG"

    id = Column(String(ID_STRING_LENGTH), primary_key=True)
    episode_id = Column(
        String(ID_STRING_LENGTH), ForeignKey("episodes.id"), nullable=False, index=True
    )
    full_path = Column(String(80), nullable=False)
    graph_key_id = Column(String(60), nullable=False, index=True)
    episode = relationship("DBEpisode", backref="graphs", foreign_keys=[episode_id])

    def get_graph(self, db: "EpisodeDB") -> "OOGraph":
        """Return the initialized graph based on this file"""
        from light.graph.structured_graph import OOGraph

        graph_json = db.read_data_from_file(self.full_path)
        graph = OOGraph.from_json(graph_json)
        return graph

    def __repr__(self):
        return f"DBEpisodeGraph(ids:[{self.id!r},{self.graph_key_id!r}], episode:{self.episode_id!r})"


class QuestCompletion(HasDBIDMixin, SQLBase):
    """Class containing metadata for episodes that represent quest completions"""

    __tablename__ = "quest_completions"

    ID_PREFIX = "QCP"

    id = Column(String(ID_STRING_LENGTH), primary_key=True)
    episode_id = Column(String, ForeignKey("episodes.id"), nullable=False, index=True)
    quest_id = Column(String(ID_STRING_LENGTH), nullable=True, index=True)


class WildMetadata(SQLBase):
    """Class containing the expected elements for an episode as stored in the db"""

    __tablename__ = "wild_metadata"

    episode_id = Column(
        String(ID_STRING_LENGTH),
        ForeignKey("episodes.id"),
        nullable=False,
        index=True,
        primary_key=True,
    )
    quest_id = Column(String(ID_STRING_LENGTH))
    model_name = Column(String(MAX_WILD_MODEL_LEN), nullable=True)
    score = Column(Integer, nullable=True)
    is_complete = Column(Boolean, nullable=True)
    choice_text = Column(String(MAX_WILD_CHOICE_LEN), nullable=True)


class EpisodeDB(BaseDB):
    """
    Episode dataset database for LIGHT, containing accessors for all
    of the recorded LIGHT episodes, including previous dataset dumps.

    Used by InteractionLoggers to write new entries, and by ParlAI to
    create teachers for datasets.
    """

    DB_TYPE = "episode"

    def _complete_init(self, config: "DictConfig"):
        """
        Initialize any specific episode-related paths. Populate
        the list of available splits and datasets.
        """
        SQLBase.metadata.create_all(self.engine)

    def _validate_init(self):
        """
        Ensure that the episode directory is properly loaded
        """
        # TODO Check the table for any possible consistency issues
        # and ensure that the episode directories for listed splits exist

    def write_wild_metadata(
        self,
        episode_id: str,
        score: int,
        model_name: Optional[str] = None,
        quest_id: Optional[str] = None,
        is_complete: Optional[bool] = None,
        choice_text: Optional[str] = None,
    ) -> None:
        with Session(self.engine) as session:
            episode_metadata = WildMetadata(
                episode_id=episode_id,
                score=score,
                model_name=model_name,
                quest_id=quest_id,
                is_complete=is_complete,
                choice_text=choice_text,
            )
            session.add(episode_metadata)
            if quest_id is not None and is_complete:
                completion = QuestCompletion(
                    id=QuestCompletion.get_id(),
                    episode_id=episode_id,
                    quest_id=quest_id,
                )
                session.add(completion)
            session.commit()

    def get_wild_metadata(self, episode_id: str) -> "WildMetadata":
        """
        Return a specific episode by id, raising an issue if it doesnt exist
        """
        stmt = select(WildMetadata).where(WildMetadata.episode_id == episode_id)
        with Session(self.engine) as session:
            wild_metadata = self._enforce_get_first(
                session, stmt, "Episode did not exist"
            )
            session.expunge_all()
            return wild_metadata

    def write_episode(
        self,
        graphs: List[Dict[str, str]],
        events: Tuple[str, List[Dict[str, str]]],
        log_type: EpisodeLogType,
        action_count: int,
        players: Set[str],
        group: DBGroupName,
    ) -> str:
        """
        Create an entry given the current argument data, store it
        to file on the database
        """
        actor_string = ",".join(list(players))
        event_filename = events[0]
        event_list = events[1]

        # Trim the filename from the left if too long
        event_filename = event_filename[-70:]

        dump_file_path = os.path.join(
            FILE_PATH_KEY, group.value, log_type.value, event_filename
        )
        graph_dump_root = os.path.join(
            FILE_PATH_KEY,
            group.value,
            log_type.value,
            "graphs",
        )

        # File writes
        self.write_data_to_file(
            {"events": event_list}, dump_file_path, json_encode=True
        )
        for graph_info in graphs:
            graph_full_path = os.path.join(graph_dump_root, graph_info["filename"])
            self.write_data_to_file(graph_info["graph_json"], graph_full_path)

        # DB Writes
        episode_id = DBEpisode.get_id()
        with Session(self.engine) as session:
            episode = DBEpisode(
                id=episode_id,
                group=group,
                split=DBSplitType.UNSET,
                status=DBStatus.REVIEW,
                actors=actor_string,
                dump_file_path=dump_file_path,
                turn_count=len(event_list),
                human_count=len(players),
                action_count=action_count,
                timestamp=time.time(),
                log_type=log_type,
            )
            first_graph = None
            for idx, graph_info in enumerate(graphs):
                graph_full_path = os.path.join(graph_dump_root, graph_info["filename"])
                db_graph = DBEpisodeGraph(
                    id=DBEpisodeGraph.get_id(),
                    graph_key_id=graph_info["key"],
                    full_path=graph_full_path,
                )
                if idx == 0:
                    first_graph = db_graph
                episode.graphs.append(db_graph)
            session.add(episode)
            session.flush()
            episode.first_graph_id = first_graph.id
            episode.final_graph_id = db_graph.id
            session.commit()

        return episode_id

    def get_episode(self, episode_id: str) -> "DBEpisode":
        """
        Return a specific episode by id, raising an issue if it doesnt exist
        """
        stmt = select(DBEpisode).where(DBEpisode.id == episode_id)
        with Session(self.engine) as session:
            episode = self._enforce_get_first(session, stmt, "Episode did not exist")
            for graph in episode.graphs:
                # Load all the graph keys
                assert graph.id is not None
            session.expunge_all()
            return episode

    def get_episodes(
        self,
        group: Optional[DBGroupName] = None,
        split: Optional[DBSplitType] = None,
        min_turns: Optional[int] = None,
        min_humans: Optional[int] = None,
        min_actions: Optional[int] = None,
        status: Optional[DBStatus] = None,
        user_id: Optional[str] = None,
        min_creation_time: Optional[float] = None,
        max_creation_time: Optional[float] = None,
        log_type: Optional[EpisodeLogType] = None,
        # ... other args
    ) -> List["DBEpisode"]:
        """
        Return all matching episodes
        """
        stmt = select(DBEpisode)
        if group is not None:
            stmt = stmt.where(DBEpisode.group == group)
        if split is not None:
            stmt = stmt.where(DBEpisode.split == split)
        if min_turns is not None:
            stmt = stmt.where(DBEpisode.turn_count >= min_turns)
        if min_humans is not None:
            stmt = stmt.where(DBEpisode.human_count >= min_humans)
        if min_actions is not None:
            stmt = stmt.where(DBEpisode.action_count >= min_actions)
        if status is not None:
            stmt = stmt.where(DBEpisode.status == status)
        if user_id is not None:
            stmt = stmt.where(DBEpisode.actors.contains(user_id))
        if log_type is not None:
            stmt = stmt.where(DBEpisode.log_type == log_type)
        if min_creation_time is not None:
            stmt = stmt.where(DBEpisode.timestamp >= min_creation_time)
        if max_creation_time is not None:
            stmt = stmt.where(DBEpisode.timestamp <= max_creation_time)
        with Session(self.engine) as session:
            episodes = session.scalars(stmt).all()
            session.expunge_all()
            return episodes

    def anonymize_group(self, group: DBGroupName) -> bool:
        """
        Run anonymization on the split to remove any link to the
        long-term user. All data within a quarter's dataset
        can be linked (for long-term memory analysis) but cannot be
        tracked cross-quarters.

        Return true on success
        """
        hashing_time = time.time()
        sha = hashlib.sha256()

        def rehash(curr_name):
            if not curr_name.startswith(USR_KEY):
                return curr_name  # already hashed

            # Adding a hashtime to make unique
            hash_name = f"{curr_name}-{hashing_time}"
            sha.update(hash_name.encode())
            return str(sha.hexdigest()[:30])

        with Session(self.engine) as session:
            stmt = select(DBEpisode).where(DBEpisode.group == group)
            episodes = session.scalars(stmt).all()
            for episode in episodes:
                actors_string = episode.actors
                actors = actors_string.split(",")
                processed_actors = [rehash(a) for a in actors]
                episode.actors = ",".join(processed_actors)
                # Rewrite the graphs and events too
                def replace_all_actors(in_data: str) -> str:
                    out_data = in_data
                    for i in range(len(actors)):
                        out_data = out_data.replace(actors[i], processed_actors[i])
                    return out_data

                graphs = episode.graphs
                for graph in graphs:
                    graph_data = self.read_data_from_file(graph.full_path)
                    anon_graph_data = replace_all_actors(graph_data)
                    self.write_data_to_file(anon_graph_data, graph.full_path)
                event_data = self.read_data_from_file(episode.dump_file_path)
                anon_event_data = replace_all_actors(event_data)
                self.write_data_to_file(anon_event_data, episode.dump_file_path)
                session.commit()
        return True

    def export(self, config: "DictConfig") -> "EpisodeDB":
        """
        Create a scrubbed version of this database for use in releases
        """
        assert config.file_root != self.file_root, "Cannot copy DB to same location!"
        new_db = EpisodeDB(config)

        # Copy all the basic content
        for table_name, table_obj in SQLBase.metadata.tables.items():
            with self.engine.connect() as orig_conn:
                with new_db.engine.connect() as new_conn:
                    all_data = [
                        dict(row) for row in orig_conn.execute(select(table_obj.c))
                    ]
                    if len(all_data) == 0:
                        continue
                    new_conn.execute(table_obj.insert().values(all_data))
                    new_conn.commit()

        with Session(self.engine) as session:
            stmt = select(DBEpisode)
            episodes = session.scalars(stmt).all()
            for episode in episodes:
                graphs = episode.graphs
                for graph in graphs:
                    # Copy the graphs to the new DB
                    graph_data = self.read_data_from_file(graph.full_path)
                    new_db.write_data_to_file(graph_data, graph.full_path)
                # Copy the events to the new DB
                event_data = self.read_data_from_file(episode.dump_file_path)
                new_db.write_data_to_file(event_data, episode.dump_file_path)

        for group in DBGroupName:
            new_db.anonymize_group(group=group)

        return new_db
