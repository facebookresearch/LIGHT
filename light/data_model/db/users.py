#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from light.data_model.db.base import BaseDB
from omegaconf import MISSING, DictConfig
from typing import Optional, Union, Dict, Any
from dataclasses import dataclass
from enum import Enum


class PlayerStatus(Enum):
    STANDARD = "standard"
    BLOCKED = "blocked"
    TUTORIAL = "in_tutorial"
    ADMIN = "admin"


@dataclass
class DBPlayer:
    """Class containing the expected elements for a Player as stored in the db"""

    extern_id: str
    is_preauth: bool
    flag_count: int
    safety_trigger_count: int
    total_messages: int
    account_status: PlayerStatus


class UserDB(BaseDB):
    """
    User database for the core LIGHT game. Tracks people's progress in the
    game, as associated with a given id.
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

    def create_user(
        self,
        extern_id: str,
        is_preauth: bool,
    ) -> int:
        """Create the specified player"""

    def get_user_by_id(self, extern_id: str) -> DBPlayer:
        """Find the specified player, raise exception if non-existent"""

    def get_agent_score(
        self, player_id: str, base_agent_id: Optional[str] = None
    ) -> int:
        """Get the specific agent score. Supply none for total score"""

    def update_agent_score(self, player_id: str, base_agent_id: str, new_points: int):
        """Update both the base agent score and total score for a player"""
