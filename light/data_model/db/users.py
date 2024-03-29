#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.data_model.db.base import BaseDB, LightDBConfig, HasDBIDMixin
from omegaconf import MISSING, DictConfig
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy import (
    select,
    delete,
    Enum,
    Integer,
    String,
    Boolean,
    ForeignKey,
)
import enum
from sqlalchemy.orm import relationship, Session, Mapped, mapped_column, DeclarativeBase

if TYPE_CHECKING:
    from light.data_model.db.environment import EnvDB


class SQLBase(DeclarativeBase):
    pass


class PlayerStatus(enum.Enum):
    STANDARD = "standard"
    BLOCKED = "blocked"
    INTRO = "in_intro"
    TUTORIAL = "in_tutorial"
    ADMIN = "admin"


class DBPlayer(HasDBIDMixin, SQLBase):
    """Class containing the expected elements for a Player as stored in the db"""

    __tablename__ = "user_accounts"
    ID_PREFIX = "USR"

    db_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    extern_id: Mapped[str] = mapped_column(
        String(60), nullable=False, index=True, unique=True
    )
    is_preauth: Mapped[bool] = mapped_column(Boolean, nullable=False)
    flag_count: Mapped[int] = mapped_column(Integer, nullable=False)
    safety_trigger_count: Mapped[int] = mapped_column(Integer, nullable=False)
    total_messages: Mapped[int] = mapped_column(Integer, nullable=False)
    account_status: Mapped[PlayerStatus] = mapped_column(
        Enum(PlayerStatus), nullable=False
    )
    scores: Mapped[List["DBScoreEntry"]] = relationship(argument="DBScoreEntry")

    def __repr__(self):
        return f"DBPlayer(ids:[{self.db_id!r},{self.extern_id!r}], preauth:{self.is_preauth!r}, status:{self.account_status.value!r})"


class DBScoreEntry(SQLBase):
    """Class containing score entries per player and character, as stored in the DB"""

    __tablename__ = "user_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("user_accounts.db_id"), nullable=False, index=True
    )
    agent_name_id: Mapped[Optional[str]] = mapped_column(
        String(40), nullable=True, index=True
    )  # Null for overall score for an agent
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_xp: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self):
        if self.agent_name_id is None:
            return f"DBScoreEntry(ids:[{self.id!r},{self.user_id!r}] score:{self.score!r}, count:{self.count!r})"
        return f"DBScoreEntry(ids:[{self.id!r},{self.user_id!r}], agent:{self.agent_name_id!r}, score:{self.score!r}, count:{self.count!r})"


class UserDB(BaseDB):
    """
    User database for the core LIGHT game. Tracks people's progress in the
    game, as associated with a given id.
    """

    DB_TYPE = "users"

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
    ) -> str:
        """Create the specified player, idempotently"""
        try:
            user = self.get_player_by_extern_id(extern_id)
            return user.db_id
        except KeyError:
            pass  # Create a new user!
        with Session(self.engine) as session:
            player_id = DBPlayer.get_id()
            player = DBPlayer(
                db_id=player_id,
                extern_id=extern_id,
                is_preauth=is_preauth,
                flag_count=0,
                safety_trigger_count=0,
                total_messages=0,
                account_status=PlayerStatus.INTRO,
            )
            base_score = DBScoreEntry(
                score=0,
                count=0,
                reward_xp=0,
            )
            player.scores.append(base_score)
            session.add(player)
            session.commit()
        return player_id

    def get_player(self, player_id: str) -> DBPlayer:
        """Find the specified player, raise exception if non-existent"""
        stmt = select(DBPlayer).where(DBPlayer.db_id == player_id)
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
        self,
        player_id: str,
        agent_name_id: str,
        points: int,
        num_turns: int,
        reward_change: int,
    ):
        """Add to both the base agent score and total score for a player"""
        player_stmt = select(DBPlayer).where(DBPlayer.db_id == player_id)
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
            base_score.reward_xp += reward_change

            agent_score = session.scalars(specific_stmt).first()
            print(agent_score, agent_name_id)
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

    def mark_flag(self, player_id: str) -> None:
        """Mark that a player has been flagged"""
        get_player = select(DBPlayer).where(DBPlayer.db_id == player_id)
        with Session(self.engine) as session:
            player = self._enforce_get_first(session, get_player, "Player not found")
            player.flag_count += 1
            session.commit()

    def mark_safety_trigger(self, player_id: str) -> None:
        """mark that a specific player has triggered the safety"""
        get_player = select(DBPlayer).where(DBPlayer.db_id == player_id)
        with Session(self.engine) as session:
            player = self._enforce_get_first(session, get_player, "Player not found")
            player.safety_trigger_count += 1
            session.commit()

    def update_player_status(self, player_id: str, new_status: PlayerStatus) -> None:
        """Update the status for a given player"""
        get_player = select(DBPlayer).where(DBPlayer.db_id == player_id)
        with Session(self.engine) as session:
            player = self._enforce_get_first(session, get_player, "Player not found")
            player.account_status = new_status
            session.commit()

    def delete_player(self, player_id: str, env_db: "EnvDB") -> None:
        """
        Delete a player from the database, removing all
        of their personal game data and clearing
        association for their graphs
        """
        get_player = select(DBPlayer).where(DBPlayer.db_id == player_id)
        with Session(self.engine) as session:
            # Ensure player exists first
            _player = self._enforce_get_first(session, get_player, "Player not found")
            session.execute(delete(DBPlayer).where(DBPlayer.db_id == player_id))
            session.execute(
                delete(DBScoreEntry).where(DBScoreEntry.user_id == player_id)
            )
            session.commit()

        env_db.clear_player_graphs(player_id)
