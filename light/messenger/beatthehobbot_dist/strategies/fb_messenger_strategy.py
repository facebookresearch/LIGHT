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

from parlai_bot.fb_messenger_manager import FBMessengerManager
from parlai_bot.safety import (
    fetch_and_initialize_safety_model, 
    SAFETY_MODEL_OPT,
    MessageSafetyDetector, 
    fetch_and_initialize_safety_model
)
from parlai_bot.utils import (
    OffensiveLanguageDetector, 
    PersonalInfoDetector,
    fetch_resources,
    resource_path,
)

from parlai_bot.sql_utils import BeatTheBotSQLQueries as bb_sql
from parlai_bot.sql_utils import BeatTheHobbotSQLQueries as bhb_sql

from dsi.logger.py.LoggerConfigHandler import LoggerConfigHandler

class FBMessengerChatStrategy(LIGHTChatStrategy):
    """Class to handle launching the LIGHT chat game on internal FB Messenger"""

    def __init__(self, manager: FBMessengerManager, opt: Optional[Opt] = None):
        """Initialize internal resources for running a chat"""
        super().__init__(manager, opt)
        assert opt is not None, "Internal service must be initialized with options"

        if not opt.get('db_tier'):
            raise ValueError('need to specify a db tier for BeatTheHobbot tables')

        if opt.get('deploy_with_tw', False):
            opt['resources_path'] = '/packages/ai-group.parlaibot-light-resources'
        else:
            fetch_resources(package='ai-group.parlaibot-light-resources')
            opt['resources_path'] = resource_path(
                '',
                package='ai-group.parlaibot-light-resources'
            )

        self.logger_handler = LoggerConfigHandler(
            'ParlAIBotBeatTheHobbitSinglePlayerLoggerConfig'
        )

        self.offensive_language = OffensiveLanguageDetector(
            path=opt.get('offensive_lang_path')
        )
        self.personal_info = PersonalInfoDetector()

        # safety_opt = deepcopy(SAFETY_MODEL_OPT)
        # # override the model:
        # safety_opt['model'] = 'transformer/classifier'
        # safety_opt['override']['model'] = 'transformer/classifier'

        # fetch_and_initialize_safety_model(
        #     opt,
        #     deploy_with_tw=deploy_with_tw,
        #     custom_model_path=os.path.join(res_path, 'safety_model'),
        #     safety_opt=safety_opt,
        # )
        # opt['safety_classifier_opts']['override'] = {
        #     'threshold', 0.9
        # }
        # opt['safety_classifier_opts']['threshold'] = 0.9
        # self.safety_checker = MessageSafetyDetector(opt)

        self.db_tier = opt['db_tier']
        self.table_prefix = 'lightbot'



    def fetch_resources(self) -> str:
        return self.opt['resources_path']

    def has_offensive_language(self, message: str, previous_turn: Optional[str] = None):
        """Determine if the provided act is offensive"""
        return self.offensive_language.contains_offensive_language(message)

    def has_personal_info(self, message: str):
        """Determine if the provided message contains personal info"""
        return self.personal_info.txt_format_detect_all(message)
        
    def update_leaderboard(self, player_id: str, score: Optional[int] = None, username: Optional[str] = None) -> None:
        """Updates the leaderboard for this game with the parameters provided"""
        if score is not None:
            # update score
            bhb_sql.update_leaderboard_score(
                player_id,
                username,
                score,
                tier=self.db_tier,
                table='{}_leaderboard'.format(self.table_prefix),
            )
        if username is not None:
            # update username
            bhb_sql.update_leaderboard_username(
                player_id,
                username,
                tier=self.db_tier,
                table='{}_leaderboard'.format(self.table_prefix),
            )

    def get_top_n_leaderboard(self, num_rows: int = 5) -> List[Any]:
        """
        Dumps the top rows on the current leaderboard, currently expects to return
        a list of rows for the top n players.
        """
        return bhb_sql.display_leaderboard(
            num_rows=5,
            tier=self.db_tier,
            table='{}_leaderboard'.format(self.table_prefix),
        )

    def get_player_leaderboard_stats(self, player_id: str) -> Dict[str, Any]:
        """Return interesting leaderboard stats for the given player id.
        
        Return dict expects the following fields:
            total_players: total number of players
            rank: rank of the given player
            score: total score of the given player

        # TODO return the players above and below to construct a contextual leaderboard
        """
        total_players = bhb_sql.get_leaderboard_total(
            tier=self.db_tier,
            table='{}_leaderboard'.format(self.table_prefix),
        )

        rank = bhb_sql.get_leaderboard_rank(
            player_id,
            tier=self.db_tier,
            table='{}_leaderboard'.format(self.table_prefix),
        )
        score = bhb_sql.get_leaderboard_score(
            player_id,
            tier=self.db_tier,
            table='{}_leaderboard'.format(self.table_prefix),
        )
        username = bhb_sql.get_leaderboard_username(
            player_id,
            tier=self.db_tier,
            table='{}_leaderboard'.format(self.table_prefix),
        )
        return {
            'total_players': total_players,
            'rank': rank,
            'score': score,
            'username': username,
        }

    def update_character_collection(self, player_id: str, collected_characters: str):
        """Update the characters that an agent has collected"""
        bhb_sql.update_character_collection(
            player_id,
            self.agent.data['characters_caught_string'],
            tier=self.db_tier,
            table='{}_extradata'.format(self.table_prefix),
        )

    def get_character_collection(self, player_id: str) -> Optional[str]:
        """Get the character collected string for the given player if it exists"""
        return bhb_sql.get_character_collection(
            player_id,
            tier=self.db_tier,
            table='{}_extradata'.format(self.table_prefix),
        )

    def log(self, data: Dict[str, Any]):
        """Log data via the logger config for this game"""
        self.logger_handler.log(data)

    def check_offensive_subwords(self, dict_freqs, message):
        """Determine if the given message has any offensive subwords"""
        return self.offensive_language.contains_offensive_subwords(dict_freqs, message)

    def username_is_valid(self, username: str) -> Union[str, bool]:
        """Ensure the username can be properly stored, return True if valid and 
        an error message for the user if it is not
        """
    
        """
        Check if the name only contains alphanumeric characters and
        spaces, and warn the user of these restrictions if it doesn't
        """
        name_without_spaces = username.replace(' ', '')
        is_valid = re.match('^[A-Za-z0-9_]*$', name_without_spaces) is not None
        if not is_valid:
            return (
                'Your username may only contain letters and '
                'numbers. Please try again.'
            )
        return True