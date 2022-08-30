# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3

# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

from abc import ABC, abstractmethod
from typing import Optional, List, Any, Dict, Union

from parlai_fb.chat_service.core.chat_service_strategy import ChatServiceStrategy


class LIGHTChatStrategy(ChatServiceStrategy):
    """
    Abstract class that defines a interface for LIGHT chat functions that
    are unique to chat services. Each usable chat service should have a derived class
    that implements each abstract method.
    """

    @abstractmethod
    def has_offensive_language(
        self, message: str, previous_turn: Optional[str] = None
    ) -> Optional[str]:
        """Determine if the provided message contains offensive language

        Args:
            message: string. Message to check
            previous_turn: Optional string. Text of previous turn to provide context
        """

    @abstractmethod
    def has_personal_info(self, message: str) -> Optional[str]:
        """Determine if the provided message contains PII

        Args:
            message: string. Message to check
        """

    @abstractmethod
    def update_leaderboard(
        self,
        player_id: str,
        score: Optional[int] = None,
        username: Optional[str] = None,
    ) -> None:
        """Updates the leaderboard for this game with the parameters provided"""

    @abstractmethod
    def get_top_n_leaderboard(self, num_rows: int = 5) -> List[Any]:
        """
        Dumps the top rows on the current leaderboard, currently expects to return
        a list of rows for the top n players.
        """

    @abstractmethod
    def get_player_leaderboard_stats(self, player_id: str) -> Dict[str, Any]:
        """Return interesting leaderboard stats for the given player id.

        Return dict expects the following fields:
            total_players: total number of players
            rank: rank of the given player
            score: total score of the given player
            username: username of the given player

        # TODO return the players above and below to construct a contextual leaderboard
        """

    @abstractmethod
    def check_offensive_subwords(self, dict_freqs, message):
        """Determine if the given message has any offensive subwords"""

    @abstractmethod
    def update_character_collection(self, player_id: str, collected_characters: str):
        """Update the characters that an agent has collected"""

    @abstractmethod
    def get_character_collection(self, player_id: str) -> Optional[str]:
        """Get the character collected string for the given player if it exists"""

    @abstractmethod
    def username_is_appropriate(self, username: str):
        """Determine if the username is considered appropriate"""

    @abstractmethod
    def username_is_valid(self, username: str) -> Union[str, bool]:
        """Ensure the username can be properly stored"""
