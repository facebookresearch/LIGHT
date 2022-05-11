#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from light.data_model.db.base import BaseDB
from omegaconf import MISSING, DictConfig
from typing import Optional, Union, Dict, Any


class InteractionDB(BaseDB):
    """
    Interaction dataset database for LIGHT, containing accessors for all
    of the recorded LIGHT episodes, including previous dataset dumps.

    Used by InteractionLoggers to write new entries, and by ParlAI to
    create teachers for datasets.
    """

    def _complete_init(self, config: "DictConfig"):
        """
        Initialize any specific interaction-related paths. Populate
        the list of available splits and datasets.
        """
        raise NotImplementedError()

    def _validate_init(self):
        """
        Ensure that the interaction directory is properly loaded
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
        split: Optional[str] = None,
        min_turns: Optional[int] = None,
        min_humans: Optional[int] = None,
        min_actions: Optional[int] = None,
        status: Optional[str] = None,
        user_id: Optional[str] = None,
        # ... other args
    ) -> List["DBEpisode"]:
        """
        Return all matching episodes
        """
