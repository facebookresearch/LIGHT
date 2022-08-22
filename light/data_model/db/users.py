#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from light.data_model.db.base import BaseDB
from omegaconf import MISSING, DictConfig
from typing import Optional, Union, Dict, Any
from sqlalchemy import (
    insert,
    select,
    Enum,
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship, Session
import enum

SQLBase = declarative_base()


class PlayerStatus(enum.Enum):
    STANDARD = "standard"
    BLOCKED = "blocked"
    TUTORIAL = "in_tutorial"
    ADMIN = "admin"


class DBPlayer(SQLBase):
    """Class containing the expected elements for a Player as stored in the db"""

    __tablename__ = "user_accounts"

    id = Column(Integer, primary_key=True)
    extern_id = Column(String(60), nullable=False, index=True, unique=True)
    is_preauth = Column(Boolean, nullable=False)
    flag_count = Column(Integer, nullable=False)
    safety_trigger_count = Column(Integer, nullable=False)
    total_messages = Column(Integer, nullable=False)
    account_status = Column(Enum(PlayerStatus), nullable=False)
    scores = relationship("DBScoreEntry")

    def __repr__(self):
        return f"DBPlayer(ids:[{self.id!r},{self.extern_id!r}], preauth:{self.is_preauth!r}, status:{self.account_status.value!r})"


class DBScoreEntry(SQLBase):
    """Class containing score entries per player and character, as stored in the DB"""

    __tablename__ = "user_scores"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("user_accounts.id"), nullable=False, index=True
    )
    agent_name_id = Column(Integer, index=True)  # Null for overall score for an agent
    score = Column(Integer, nullable=False)
    count = Column(Integer, nullable=False)

    def __repr__(self):
        if self.agent_name_id is None:
            return f"DBScoreEntry(ids:[{self.id!r},{self.user_id!r}] score:{self.score!r}, count:{self.count!r})"
        return f"DBScoreEntry(ids:[{self.id!r},{self.user_id!r}], agent:{self.agent_name_id!r}, score:{self.score!r}, count:{self.count!r})"


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
        SQLBase.metadata.create_all(self.engine)

    def _validate_init(self):
        """
        Ensure that the interaction directory is properly loaded
        """
        # TODO Check the table for any possible consistency issues

    def create_user(
        self,
        extern_id: str,
        is_preauth: bool,
    ) -> int:
        """Create the specified player"""
        with Session(self.engine) as session:
            player = DBPlayer(
                extern_id=extern_id,
                is_preauth=is_preauth,
                flag_count=0,
                safety_trigger_count=0,
                total_messages=0,
                account_status=PlayerStatus.TUTORIAL,
            )
            base_score = DBScoreEntry(
                score=0,
                count=0,
            )
            player.scores.append(base_score)
            session.add(player)
            session.flush()
            player_id = player.id
            session.commit()
        return player_id

    def get_player(self, player_id: int) -> DBPlayer:
        """Find the specified player, raise exception if non-existent"""
        stmt = select(DBPlayer).where(DBPlayer.id == player_id)
        with Session(self.engine) as session:
            player = self._enforce_get_first(session, stmt, "Player not found")
            session.expunge_all()
            return player

    def get_player_by_extern_id(self, extern_id: str) -> DBPlayer:
        """Find the specified player, raise exception if non-existent"""
        stmt = select(DBPlayer).where(DBPlayer.extern_id == extern_id)
        with Session(self.engine) as session:
            player = self._enforce_get_first(session, stmt, "Player not found")
            session.expunge_all()
            return player

    def get_agent_score(
        self, player_id: str, agent_name_id: Optional[str] = None
    ) -> DBScoreEntry:
        """Get the specific agent score. Supply None for total score"""
        stmt = (
            select(DBScoreEntry)
            .where(DBScoreEntry.user_id == player_id)
            .where(DBScoreEntry.agent_name_id == agent_name_id)
        )
        with Session(self.engine) as session:
            score_entry = self._enforce_get_first(
                session, stmt, "Player or agent not found"
            )
            session.expunge_all()
            return score_entry

    def update_agent_score(
        self, player_id: str, agent_name_id: str, points: int, num_turns: int
    ):
        """Add to both the base agent score and total score for a player"""
        player_stmt = select(DBPlayer).where(DBPlayer.id == player_id)
        base_stmt = (
            select(DBScoreEntry)
            .where(DBScoreEntry.user_id == player_id)
            .where(DBScoreEntry.agent_name_id == None)
        )
        specific_stmt = (
            select(DBScoreEntry)
            .where(DBScoreEntry.user_id == player_id)
            .where(DBScoreEntry.agent_name_id == agent_name_id)
        )

        with Session(self.engine) as session:
            player = self._enforce_get_first(session, player_stmt, "Player not found")
            player.total_messages += num_turns

            base_score = session.scalars(base_stmt).first()
            if base_score is None:
                # we should never fail to get the basic agent score
                raise AssertionError("No default score for player, corruption issue")
            base_score.score += points
            base_score.count += 1

            agent_score = session.scalars(specific_stmt).first()
            if agent_score is None:
                # User has not played this character before, we'll need to initialize it
                agent_score = DBScoreEntry(
                    agent_name_id=agent_name_id,
                    score=points,
                    count=1,
                )
                player.scores.append(agent_score)
                session.add(agent_score)
            else:
                agent_score.score += points
                agent_score.count += 1

            session.commit()

    def mark_flag(self, player_id: int) -> None:
        """Mark that a player has been flagged"""
        get_player = select(DBPlayer).where(DBPlayer.id == player_id)
        with Session(self.engine) as session:
            player = self._enforce_get_first(session, get_player, "Player not found")
            player.flag_count += 1
            session.commit()

    def mark_safety_trigger(self, player_id: int) -> None:
        """mark that a specific player has triggered the safety"""
        get_player = select(DBPlayer).where(DBPlayer.id == player_id)
        with Session(self.engine) as session:
            player = self._enforce_get_first(session, get_player, "Player not found")
            player.safety_trigger_count += 1
            session.commit()

    def update_player_status(self, player_id: int, new_status: PlayerStatus) -> None:
        """Update the status for a given player"""
        get_player = select(DBPlayer).where(DBPlayer.id == player_id)
        with Session(self.engine) as session:
            player = self._enforce_get_first(session, get_player, "Player not found")
            player.account_status = new_status
            session.commit()
