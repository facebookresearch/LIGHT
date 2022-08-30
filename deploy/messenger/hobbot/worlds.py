# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3

# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

from parlai.core.agents import create_agent
from parlai.core.dict import DictionaryAgent

import parlai_fb.chat_service.utils.misc as internal_utils
from parlai.chat_service.utils.misc import DictFrequencies
from parlai.core.opt import Opt
from light.hobbot.onboarding_worlds import (
    LIGHTBotOverworld,
    LIGHTBotOnboardWorld,
)
from light.hobbot.single_player_world import LIGHTSinglePlayerWorld
from light.graph.builders.one_room_builder import OneRoomChatBuilder
from light.data_model.light_database import LIGHTDatabase

from copy import deepcopy
import os
import json


def module_initialize(opt: Opt, manager, deploy_with_tw: bool = False):
    """Initialize the module, pulling in resources and the model file."""
    print(opt)
    opt["deploy_with_tw"] = deploy_with_tw
    service_strategy = internal_utils.get_service_strategy(opt, manager)
    opt["service_strategy"] = service_strategy

    res_path = service_strategy.fetch_resources()
    opt["offensive_lang_path"] = os.path.join(res_path, "offensive_language.txt")
    opt["nonsequiturs_path"] = os.path.join(res_path, "light-non-sequiturs.txt")

    service_strategy.init_safety(opt)

    # Rest of LIGHT setup
    ldb = LIGHTDatabase(os.path.join(res_path, "database.db"))
    opt["graph_builder"] = OneRoomChatBuilder(
        ldb=ldb,
        opt={
            "db_path": os.path.join(res_path, "database.db"),
            "model_path": os.path.join(res_path, "starspace"),
            "suggestion_type": "hybrid",
            "hybridity_prob": 0.2,
        },
    )

    # Build a dictionary for use in OffensiveLanguageDetector
    dict_agent = DictionaryAgent({})
    dict_agent.load(os.path.join(res_path, "personachat.dict"))
    dict_freqs = DictFrequencies(dict_agent.freq)

    opt["dict_freqs"] = dict_freqs

    opt["logger_handler"] = None  # only have single player
    with open(os.path.join(res_path, "character_emojis.json"), "r") as jsonfile:
        opt["all_persona_emojis"] = json.load(jsonfile)
    quest_dir = os.path.join(res_path, "quests")
    opt["available_quests"] = []
    for quest_file in os.listdir(quest_dir):
        with open(os.path.join(quest_dir, quest_file), "r") as jsonfile:
            opt["available_quests"].append(json.load(jsonfile))


def eligibility_function(agent_id):
    try:
        from parlai_bot.sql_utils import BeatTheHobbotSQLQueries as bhb_sql

        is_blocked = bhb_sql.is_blocked(agent_id, table="lightbot_blockedlist")
        if is_blocked is None or is_blocked == 0:
            return True
        return False
    except ImportError:
        return True
