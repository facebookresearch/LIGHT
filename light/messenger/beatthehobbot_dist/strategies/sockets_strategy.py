#!/usr/bin/env python3

# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

from typing import Optional, List, Dict, Any, Union

import re

from parlai.core.opt import Opt
from parlai_internal.projects.light.beatthehobbot_dist.strategies.light_chat_strategy import LIGHTChatStrategy
from parlai.chat_service.utils.misc import PersonalInfoDetector


class SocketChatStrategy(LIGHTChatStrategy):
    """Class to handle launching the LIGHT chat game externally on a local machine"""

    def __init__(self, manager, opt: Optional[Opt] = None):
        """Initialize internal resources for running a chat"""
        super().__init__(manager, opt)
        # TODO initialize a local database or something?
        self.player_stats: Dict[str, Dict[str, Any]] = {}
        self.init_safety(opt)
        self.pii_detector = PersonalInfoDetector()

    def _init_player(self, player_id: str) -> None:
        """Track a new player"""
        if player_id not in self.player_stats:
            self.player_stats[player_id] = {
                'score': 0,
                'username': None,
                'collected_characters': None,
            }

    def fetch_resources(self) -> str:
        assert 'resources_path' in self.opt, "Must provide resource path for local runs"
        return self.opt['resources_path']

    def has_offensive_language(self, message: str, previous_turn: Optional[str] = None):
        """Determine if the provided act is offensive"""
        return self.safety_detectors['offensive_language'].contains_offensive_language(message)

    def has_personal_info(self, message: str):
        """Determine if the provided message contains personal info"""
        return self.pii_detector.txt_format_detect_all(message)
        
    def update_leaderboard(self, player_id: str, score: Optional[int] = None, username: Optional[str] = None) -> None:
        """Updates the leaderboard for this game with the parameters provided"""
        self._init_player(player_id)
        if score is not None:
            self.player_stats[player_id]['score'] += score
        if username is not None:
            self.player_stats[player_id]['username'] = username

    def get_top_n_leaderboard(self, num_rows: int = 5) -> List[Any]:
        """
        Dumps the top rows on the current leaderboard, currently expects to return
        a list of rows for the top n players.
        """
        sorted_players = [(None, x['username'], x['score']) for x in self.player_stats.values()]
        sorted_players.sort(key=lambda x: x[2])
        return sorted_players[:num_rows]

    def get_player_leaderboard_stats(self, player_id: str) -> Dict[str, Any]:
        """Return interesting leaderboard stats for the given player id.
        
        Return dict expects the following fields:
            total_players: total number of players
            rank: rank of the given player
            score: total score of the given player

        # TODO return the players above and below to construct a contextual leaderboard
        """
        self._init_player(player_id)
        return {
            'total_players': len(self.player_stats),
            'rank': -1,
            'score': self.player_stats[player_id]['score'],
            'username': self.player_stats[player_id]['username'],
        }

    def update_character_collection(self, player_id: str, collected_characters: str):
        """Update the characters that an agent has collected"""
        self._init_player(player_id)
        self.player_stats[player_id]['collected_characters'] = collected_characters

    def get_character_collection(self, player_id: str) -> Optional[str]:
        """Get the character collected string for the given player if it exists"""
        self._init_player(player_id)
        return self.player_stats[player_id]['collected_characters'] 

    def log(self, data: Dict[str, Any]):
        """Log data via the logger config for this game"""
        print("Would log data", data)

    def check_offensive_subwords(self, dict_freqs, message):
        """Determine if the given message has any offensive subwords"""
        return self.safety_detectors['offensive_language'].contains_offensive_language(message)

    def username_is_appropriate(self, username: str):
        """Determine if the username is considered appropriate"""
        return self.safety_detectors['offensive_language'].contains_offensive_language(username)

    def username_is_valid(self, username: str) -> Union[str, bool]:
        """Ensure the username can be properly stored, return True if valid and 
        an error message for the user if it is not
        """
        return True