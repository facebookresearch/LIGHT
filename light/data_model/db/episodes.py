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


class DBGroupName(Enum):
    """Edges in the LIGHT Environment DB"""

    ORIG = "orig"
    WILD = "wild"
    MULTIPARTY = "multiparty"
    PRE_LAUNCH = "crowdsourced"
    RELEASE = "full_release"


@dataclass
class DBEpisode:
    """Class containing the expected elements for an episode as stored in the db"""

    group: DBGroupName
    split: DBSplitType
    status: DBStatus
    actors: List[str]
    dump_file: str
    after_graph: str
    timestamp: float

    def get_before_graph(self, db: "EpisodeDB") -> "OOGraph":
        """Return the state of the graph before this episode"""

    def get_parsed_episode(self, db: "EpisodeDB") -> List[Any]:
        """Return all of the actions and turns from this episode"""

    def get_after_graph(self, db: "EpisodeDB") -> "OOGraph":
        """Return the state of the graph after this episode"""


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
        raise NotImplementedError()

    def _validate_init(self):
        """
        Ensure that the episode directory is properly loaded
        """
        raise NotImplementedError()

    def write_episode(self, args) -> str:
        """
        Create an entry given the current argument data, store it
        to file on the database
        """

    def get_episode(self, episode_id: str) -> "DBEpisode":
        """
        Return a specific episode by id, raising an issue if it doesnt exist
        """

    def get_episodes(
        self,
        group: Optional[str] = None,
        split: Optional[DBSplitType] = None,
        min_turns: Optional[int] = None,
        min_humans: Optional[int] = None,
        min_actions: Optional[int] = None,
        status: Optional[DBStatus] = None,
        user_id: Optional[str] = None,
        min_creation_time: Optional[float] = None,
        max_creation_time: Optional[float] = None,
        # ... other args
    ) -> List["DBEpisode"]:
        """
        Return all matching episodes
        """
