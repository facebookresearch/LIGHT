#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.data_model.db.base import (
    BaseDB,
    LightDBConfig,
    DBStatus,
    DBSplitType,
    HasDBIDMixin,
)
from light.data_model.db.users import DBPlayer
from typing import Optional, List, Tuple, Dict, Set, Sequence, TYPE_CHECKING
from sqlalchemy import (
    select,
    Enum,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import (
    relationship,
    Session,
    Mapped,
    mapped_column,
    DeclarativeBase,
    reconstructor,
)
from light.graph.events.base import GraphEvent
import time
import enum
import os
import hashlib

if TYPE_CHECKING:
    from light.graph.structured_graph import OOGraph

FILE_PATH_KEY = "episodes"
ID_STRING_LENGTH = 40
USR_KEY = DBPlayer.ID_PREFIX
MAX_WILD_MODEL_LEN = 200
MAX_WILD_CHOICE_LEN = 100


class SQLBase(DeclarativeBase):
    pass


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


class DBEpisodeGraph(HasDBIDMixin, SQLBase):
    """Class containing expected elements for a stored graph"""

    __tablename__ = "graphs"

    ID_PREFIX = "EPG"

    id: Mapped[str] = mapped_column(String(ID_STRING_LENGTH), primary_key=True)
    episode_id: Mapped[str] = mapped_column(
        String(ID_STRING_LENGTH), ForeignKey("episodes.id"), nullable=False, index=True
    )
    full_path: Mapped[str] = mapped_column(String(80), nullable=False)
    graph_key_id: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    episode: Mapped["DBEpisode"] = relationship(
        argument="DBEpisode", back_populates="graphs", foreign_keys=[episode_id]
    )

    def get_graph(self, db: "EpisodeDB") -> "OOGraph":
        """Return the initialized graph based on this file"""
        from light.graph.structured_graph import OOGraph

        graph_json = db.read_data_from_file(self.full_path)
        assert isinstance(graph_json, str)
        graph = OOGraph.from_json(graph_json)
        return graph

    def __repr__(self):
        return f"DBEpisodeGraph(ids:[{self.id!r},{self.graph_key_id!r}], episode:{self.episode_id!r})"


class DBEpisode(HasDBIDMixin, SQLBase):
    """Class containing the expected elements for an episode as stored in the db"""

    __tablename__ = "episodes"

    ID_PREFIX = "EPI"

    id: Mapped[str] = mapped_column(String(ID_STRING_LENGTH), primary_key=True)
    group: Mapped[DBGroupName] = mapped_column(
        Enum(DBGroupName), nullable=False, index=True
    )
    split: Mapped[DBSplitType] = mapped_column(
        Enum(DBSplitType), nullable=False, index=True
    )
    status: Mapped[DBStatus] = mapped_column(Enum(DBStatus), nullable=False, index=True)
    actors: Mapped[str] = mapped_column(
        String
    )  # Comma separated list of actor IDs. Cleared on release data
    dump_file_path: Mapped[str] = mapped_column(
        String(90), nullable=False
    )  # Path to data
    turn_count: Mapped[int] = mapped_column(Integer, nullable=False)
    human_count: Mapped[int] = mapped_column(Integer, nullable=False)
    action_count: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False)
    log_type: Mapped[EpisodeLogType] = mapped_column(
        Enum(EpisodeLogType), nullable=False
    )
    first_graph_id: Mapped[str] = mapped_column(
        String(ID_STRING_LENGTH), ForeignKey("graphs.id")
    )
    final_graph_id: Mapped[str] = mapped_column(
        String(ID_STRING_LENGTH), ForeignKey("graphs.id")
    )
    graphs: Mapped[List["DBEpisodeGraph"]] = relationship(
        back_populates="episode", foreign_keys=[DBEpisodeGraph.episode_id]
    )

    @reconstructor
    def init_on_load(self):
        self._cached_map = None

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

        data_dict = db.read_data_from_file(self.dump_file_path, json_encoded=True)
        assert isinstance(data_dict, dict)
        events = data_dict["events"]
        graph_grouped_events: List[Tuple[str, List["GraphEvent"]]] = []
        current_graph_events = []
        curr_graph_key = None
        curr_graph = None
        tmp_world = None
        # Extract events to the correct related graphs, initializing the graphs
        # as necessary
        for event_turn in events:
            # See if we've moved onto an event in a new graph
            if event_turn["graph_key"] != curr_graph_key:
                if curr_graph_key is not None:
                    # There was old state, so lets push it to the list
                    graph_grouped_events.append((curr_graph_key, current_graph_events))
                # We're on a new graph, have to reset the current graph state
                curr_graph_key = event_turn["graph_key"]
                current_graph_events: List["GraphEvent"] = []
                curr_graph = self.get_graph(curr_graph_key, db)
                tmp_world = World(WorldConfig())
                tmp_world.oo_graph = curr_graph
            # The current turn is part of the current graph's events, add
            assert tmp_world is not None, "Must have created a world by here"
            current_graph_events.append(
                GraphEvent.from_json(event_turn["event_json"], tmp_world)
            )
        if len(current_graph_events) > 0:
            assert curr_graph_key is not None, "Must have graph_key by here"
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


class QuestCompletion(HasDBIDMixin, SQLBase):
    """Class containing metadata for episodes that represent quest completions"""

    __tablename__ = "quest_completions"

    ID_PREFIX = "QCP"

    id: Mapped[str] = mapped_column(String(ID_STRING_LENGTH), primary_key=True)
    episode_id: Mapped[str] = mapped_column(
        String, ForeignKey("episodes.id"), nullable=False, index=True
    )
    quest_id: Mapped[str] = mapped_column(
        String(ID_STRING_LENGTH), nullable=True, index=True
    )


class WildMetadata(SQLBase):
    """Class containing the expected elements for an episode as stored in the db"""

    __tablename__ = "wild_metadata"

    episode_id: Mapped[str] = mapped_column(
        String(ID_STRING_LENGTH),
        ForeignKey("episodes.id"),
        nullable=False,
        index=True,
        primary_key=True,
    )
    quest_id: Mapped[str] = mapped_column(String(ID_STRING_LENGTH))
    model_name: Mapped[str] = mapped_column(String(MAX_WILD_MODEL_LEN), nullable=True)
    score: Mapped[int] = mapped_column(Integer, nullable=True)
    is_complete: Mapped[bool] = mapped_column(Boolean, nullable=True)
    choice_text: Mapped[str] = mapped_column(String(MAX_WILD_CHOICE_LEN), nullable=True)


class EpisodeDB(BaseDB):
    """
    Episode dataset database for LIGHT, containing accessors for all
    of the recorded LIGHT episodes, including previous dataset dumps.

    Used by InteractionLoggers to write new entries, and by ParlAI to
    create teachers for datasets.
    """

    DB_TYPE = "episode"

    def _complete_init(self, config: "LightDBConfig"):
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
            first_id = None
            curr_id = None
            for idx, graph_info in enumerate(graphs):
                graph_full_path = os.path.join(graph_dump_root, graph_info["filename"])
                curr_id = DBEpisodeGraph.get_id()
                db_graph = DBEpisodeGraph(
                    id=curr_id,
                    graph_key_id=graph_info["key"],
                    full_path=graph_full_path,
                )
                if idx == 0:
                    first_id = curr_id
                episode.graphs.append(db_graph)

            session.add(episode)
            assert first_id is not None and curr_id is not None
            episode.first_graph_id = first_id
            episode.final_graph_id = curr_id
            session.flush()
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
    ) -> Sequence["DBEpisode"]:
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
                    assert isinstance(graph_data, str)
                    anon_graph_data = replace_all_actors(graph_data)
                    self.write_data_to_file(anon_graph_data, graph.full_path)
                event_data = self.read_data_from_file(episode.dump_file_path)
                assert isinstance(event_data, str)
                anon_event_data = replace_all_actors(event_data)
                self.write_data_to_file(anon_event_data, episode.dump_file_path)
                session.commit()
        return True

    def export(
        self, config: "LightDBConfig", group: Optional[DBGroupName] = None
    ) -> "EpisodeDB":
        """
        Create a scrubbed version of this database for use in releases
        """
        assert config.file_root != self.file_root, "Cannot copy DB to same location!"
        new_db = EpisodeDB(config)

        # Copy all the basic content
        with self.engine.connect() as orig_conn:
            with new_db.engine.connect() as new_conn:
                # Write the episodes
                episode_table = SQLBase.metadata.tables["episodes"]
                stmt = select(DBEpisode)
                if group is not None:
                    stmt = stmt.where(DBEpisode.group == group)
                episodes = orig_conn.execute(stmt)
                episode_data = [dict(r) for r in episodes]
                episode_ids = [d["id"] for d in episode_data]
                new_conn.execute(episode_table.insert().values(episode_data))
                for tbl_name in ["graphs", "quest_completions", "wild_metadata"]:
                    tbl_obj = SQLBase.metadata.tables[tbl_name]
                    stmt = select(tbl_obj.c).where(
                        tbl_obj.c.episode_id.in_(episode_ids)
                    )
                    table_data = [dict(r) for r in orig_conn.execute(stmt)]
                    new_conn.execute(tbl_obj.insert().values(table_data))
                new_conn.commit()  # type: ignore

        # Copy graphs over
        with Session(self.engine) as session:
            stmt = select(DBEpisode)
            if group is not None:
                stmt = stmt.where(DBEpisode.group == group)
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

        if group is not None:
            new_db.anonymize_group(group=group)
        else:
            for group in DBGroupName:
                new_db.anonymize_group(group=group)

        return new_db

    def download_and_import_group(self, group: DBGroupName) -> None:
        """Download the group from a hosted source, then """
        stmt = select(DBEpisode).where(DBEpisode.group == group).limit(1)
        with Session(self.engine) as session:
            episodes = session.scalars(stmt).all()
            if len(episodes) > 0:
                print(f"You already have {group} installed")
                return
        assert NotImplementedError("Still need to implement the download step")
        # data_url = light.data_utils.get_episode_group(group) or something like it
        # download data to temporary directory
        # unzip db and data in temporary directory
        # create LightDBConfig pointing to this dir
        # self.import_db(other_db)
        # delete temporary db directory

    def import_db(self, other_db: "EpisodeDB") -> None:
        """Attempt to import the contents of the specified db to this one"""
        # Copy all the contents from the source
        for _, table_obj in SQLBase.metadata.tables.items():
            with self.engine.connect() as dest_conn:
                with other_db.engine.connect() as source_conn:
                    all_data = [
                        dict(row) for row in source_conn.execute(select(table_obj.c))
                    ]
                    if len(all_data) == 0:
                        continue
                    dest_conn.execute(table_obj.insert().values(all_data))
                    dest_conn.commit()  # type: ignore

        with Session(other_db.engine) as session:
            stmt = select(DBEpisode)
            episodes = session.scalars(stmt).all()
            for episode in episodes:
                graphs = episode.graphs
                for graph in graphs:
                    # Copy the graphs to the new DB
                    graph_data = other_db.read_data_from_file(graph.full_path)
                    self.write_data_to_file(graph_data, graph.full_path)
                # Copy the events to the new DB
                event_data = other_db.read_data_from_file(episode.dump_file_path)
                self.write_data_to_file(event_data, episode.dump_file_path)
