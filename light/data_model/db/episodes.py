#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from light.data_model.db.base import BaseDB, DBStatus, DBSplitType
from omegaconf import MISSING, DictConfig
from typing import Optional, List, Tuple, Union, Dict, Any, Set, TYPE_CHECKING
from sqlalchemy import insert, select, Enum, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Session
from light.graph.events.base import GraphEvent
import time
import enum
import os

if TYPE_CHECKING:
    from light.graph.structured_graph import OOGraph

SQLBase = declarative_base()
FILE_PATH_KEY = "episodes"


class DBGroupName(enum.Enum):
    """Data Releases in the LIGHT episode DB"""

    ORIG = "orig"
    WILD = "wild"
    MULTIPARTY = "multiparty"
    PRE_LAUNCH = "crowdsourced"
    RELEASE_Q4_22 = "full_release_Q4_22"


class EpisodeLogType(enum.Enum):
    """Types of episodes in LIGHT"""

    ROOM = "room"
    AGENT = "agent"
    FULL = "full"


class DBEpisode(SQLBase):
    """Class containing the expected elements for an episode as stored in the db"""

    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True)
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
        from light.world.world import World

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
                tmp_world = World({}, None)
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


class DBEpisodeGraph(SQLBase):
    """Class containing expected elements for a stored graph"""

    __tablename__ = "graphs"

    id = Column(Integer, primary_key=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False, index=True)
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


class EpisodeDB(BaseDB):
    """
    Episode dataset database for LIGHT, containing accessors for all
    of the recorded LIGHT episodes, including previous dataset dumps.

    Used by InteractionLoggers to write new entries, and by ParlAI to
    create teachers for datasets.
    """

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
        with Session(self.engine) as session:
            episode = DBEpisode(
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

            episode_id = episode.id
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
