#!/usr/bin/env python3

# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

import datetime
import random
import time

from parlai.core.worlds import World
from parlai.chat_service.services.messenger.worlds import OnboardWorld
import light.hobbot.utils as utils

from copy import deepcopy

CURRENT_CHARACTER_COUNT = 630


def request_username(agent, world):
    """Handler for getting a new username for an agent"""
    a = None
    while not a:
        a = utils.get_response_timeout_loop(agent, world)
        if a is None:
            return None
        is_valid = world.service_strategy.username_is_valid(a["text"])
        if is_valid is not True:
            agent.observe(
                {"id": "", "text": is_valid,}
            )
            a = None
        else:
            # check if contains offensive subword
            bad = world.service_strategy.check_offensive_subwords(
                world.opt.get("dict_freqs"), a["text"],
            )
            if bad is not None and len(bad) > 0:
                a = None
                world.agent.observe({"id": "", "text": utils.USERNAME_OFFLANG})
    return a


# ---------- LIGHT Game Overworld -------- #
class LIGHTBotOverworld(World):
    """World to handle user entering into the LIGHT chat game
    """

    QUICK_REPLY_OPTIONS = ["PLAY", "OPTIONS", "EXIT"]
    TOS_REPLY_OPTIONS = ["AGREE", "DISAGREE", "EXIT"]
    INTRO_EMOJIS = utils.INTRO_EMOJIS
    OPTIONS = [
        "INSTRUCTIONS",
        "CHANGE USERNAME",
        "LEADERBOARD",
        "CHARACTERS",
        "POLICIES",
        "BACK",
    ]

    MENU_INSTRUCTIONS = (
        "Click *PLAY* below to start playing! "
        "Click *OPTIONS* below for more options. "
    )

    def __init__(self, opt, agent):
        self.debug = opt.get("is_debug", False)
        self.agent = agent
        self.opt = opt
        self.episodeDone = False
        self.agent.start_time = time.time()  # starting time for timing out session
        self.seen_intro = False

        self.service_strategy = opt["service_strategy"]

        self._log("LIGHTBotOverworld initialization complete...")
        self.table_prefix = "lightbot"

    @staticmethod
    def generate_world(opt, agents, task_state=None):
        return LIGHTBotOverworld(opt, agents[0])

    def _log(self, text):
        if self.debug:
            curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("{} DEBUG (LIGHTBotOverworld): {}".format(curr_time, text))

    def _populate_agent_data(self):
        """Register any important data from db tables for the user"""
        if self.agent.data.get("characters_caught") is None:
            character_string = self.service_strategy.get_character_collection(
                self.agent.id
            )
            if character_string is None:
                character_string = "0" * CURRENT_CHARACTER_COUNT
                self.service_strategy.update_character_collection(
                    self.agent.id, character_string
                )
            self.agent.data["characters_caught_string"] = character_string
            characters_caught = deepcopy(self.opt["all_persona_emojis"])
            for char in characters_caught.values():
                char["is_caught"] = character_string[int(char["emoji_id"])] != "0"
            self.agent.data["characters_caught"] = characters_caught

    def _view_characters(self):
        """
        Send a message to the agent telling them how many characters
        they've collected so far
        """
        characters = utils.get_awarded_character_emojis(self.agent)
        random.shuffle(characters)
        if len(characters) == 0:
            self.agent.observe(
                {"id": "", "text": utils.NO_CHARACTERS_TEXT,}
            )
        else:
            self.agent.observe(
                {"id": "", "text": utils.HAS_CHARACTERS_TEXT,}
            )
            chars_string = f"You've collected {len(characters)} badges: "
            self.agent.observe(
                {"id": "", "text": chars_string + "".join(characters),}
            )

    def _view_options(self):
        self.agent.observe(
            {
                "id": "OPTIONS",
                "text": utils.OPTIONS_TEXT,
                "quick_replies": self.OPTIONS,
            }
        )
        a = utils.get_response_timeout_loop(self.agent, self)
        if a is None:
            return False  # timeout
        if a["text"].upper() in self.OPTIONS:
            if a["text"].upper() == "INSTRUCTIONS":
                self._view_instructions()
            if a["text"].upper() == "CHARACTERS":
                self._view_characters()
            elif a["text"].upper() == "CHANGE USERNAME":
                if not self._change_username():
                    return False  # timed out
            elif a["text"].upper() == "LEADERBOARD":
                self._view_leaderboard()
            elif a["text"].upper() == "POLICIES":
                self._view_tos()
        return True

    def episode_done(self):
        return self.episodeDone

    def _agree_to_tos(self):
        """Lead user through accepting the policy. Return True if successful,
        False if timeout or if the user wants to exit"""
        for policy_msg in utils.POLICIES:
            self.agent.observe(
                {
                    "id": "",
                    "text": "*POLICIES*: {}".format(policy_msg),
                    "quick_replies": self.TOS_REPLY_OPTIONS,
                }
            )
        a = utils.get_response_timeout_loop(self.agent, self)
        if a is None:
            return False  # timeout

        while a["text"].upper() != "AGREE":
            self.agent.observe(
                {
                    "id": "",
                    "text": "In order to play this game, you must agree "
                    "to our policies. ",
                    "quick_replies": self.TOS_REPLY_OPTIONS,
                }
            )
            a = utils.get_response_timeout_loop(self.agent, self)
            if a is None:
                return False  # timeout

        self._log("User {} agreed to Terms of Service".format(self.agent.id))
        return True

    def _change_username(self):
        """
        Change the username.
        Return True if successful, false otherwise (timeout)
        """
        if self.agent.data.get("user_name", None) is None:
            self.agent.observe(
                {
                    "id": "",
                    "text": "PLAY a round to set your initial username",
                    "quick_replies": self.QUICK_REPLY_OPTIONS,
                }
            )
            return True
        self.agent.observe({"id": "", "text": "Please enter your new username. "})
        a = request_username(self.agent, self)
        if a is None:
            return False

        self.agent.data["user_name"] = a["text"]
        name_text = "Your username has been changed to {}. ".format(a["text"])
        self.service_strategy.update_leaderboard(self.agent.id, username=a["text"])
        self.agent.observe(
            {
                "id": "",
                "text": name_text + self.MENU_INSTRUCTIONS,
                "quick_replies": self.QUICK_REPLY_OPTIONS,
            }
        )
        self._log("Username changed for agent {}.".format(self.agent.id))
        return True

    def _view_leaderboard(self):
        leaderboard = self.service_strategy.get_top_n_leaderboard(num_rows=50)
        player_stats = self.service_strategy.get_player_leaderboard_stats(self.agent.id)
        if leaderboard is not None:
            if player_stats["rank"] is not None and player_stats["score"] is not None:
                self.agent.observe(
                    {
                        "id": "Game",
                        "text": f"Your *rank* is {int(player_stats['rank'])} out "
                        f"of {player_stats['total_players']}.\n"
                        f"Your *total score* is {player_stats['score']}. ",
                    }
                )
            text = []
            i = 1
            for tup in leaderboard:
                text.append(str(i) + ". " + tup[1] + ": " + str(tup[2]))
                i += 1
            display_text = "\n".join(text)
            self.agent.observe(
                {
                    "id": "LEADERBOARD",
                    "text": "\n" + display_text,
                    "quick_replies": self.QUICK_REPLY_OPTIONS,
                }
            )
        else:
            self.agent.observe(
                {
                    "id": "",
                    "text": "Sorry, the leaderboard is not accessible right now.",
                    "quick_replies": self.QUICK_REPLY_OPTIONS,
                }
            )

    def _view_instructions(self):
        self.agent.observe(
            {
                "id": "INSTRUCTIONS",
                "text": utils.OVERWORLD_INSTRUCTIONS,
                "quick_replies": self.QUICK_REPLY_OPTIONS,
            }
        )

    def _view_tos(self):
        for policy_msg in utils.POLICIES:
            self.agent.observe(
                {
                    "id": "POLICIES",
                    "text": policy_msg,
                    "quick_replies": self.QUICK_REPLY_OPTIONS,
                }
            )

    def _clear_message_queue(self):
        """Clear all messages from the agent's message queue"""
        a = self.agent.act()
        while a:
            a = self.agent.act()

    def _display_onboarding_emoji(self):
        self.agent.observe(
            {"id": "", "text": random.choice(self.INTRO_EMOJIS) * utils.EMOJI_LENGTH,}
        )

    def _display_intro(self):
        """Display introduction text for entering the overworld"""
        data = self.agent.data
        self._get_username()
        # clear all messages (starting fresh)
        self._clear_message_queue()

        if not data.get("returning_player"):
            # only display overworld info once
            data["returning_player"] = True
            self._display_onboarding_emoji()
            if data.get("user_name"):  # have played before
                u_name = data["user_name"]
                self.agent.observe(
                    {"id": "", "text": utils.REPEAT_MESSAGE.format(u_name),}
                )
            else:  # have never played before
                for message in utils.FIRST_INTRO_MESSAGES:
                    self.agent.observe(
                        {"id": "", "text": message,}
                    )
                if not self._agree_to_tos():
                    return None  # timed out
        self.agent.observe(
            {
                "id": "",
                "text": self.MENU_INSTRUCTIONS,
                "quick_replies": self.QUICK_REPLY_OPTIONS,
            }
        )
        self.seen_intro = True

    def _get_username(self):
        data = self.agent.data
        if data.get("user_name", None) is None:
            # get username from leaderboard if it exists
            lb_stats = self.service_strategy.get_player_leaderboard_stats(self.agent.id)
            username = lb_stats["username"]
            if username is not None:
                data["user_name"] = username

    def parley(self):
        if not self.seen_intro:
            self._display_intro()
            self._populate_agent_data()
        a = utils.get_response_timeout_loop(self.agent, self)
        if a is None:
            return None  # timeout or exit
        if a["text"].upper() in self.QUICK_REPLY_OPTIONS:
            if a["text"].upper() == "PLAY":
                self.agent.data["mode"] = "SinglePlayer"
                self.episodeDone = True
                return "SinglePlayer"
            else:
                if not self._view_options():  # agent clicked 'options'
                    return None  # timed out or exit
                self.agent.observe(
                    {
                        "id": "",
                        "text": self.MENU_INSTRUCTIONS,
                        "quick_replies": self.QUICK_REPLY_OPTIONS,
                    }
                )
        else:
            # invalid option, try again
            self.agent.observe(
                {
                    "id": "",
                    "text": "Invalid option. Please click *PLAY* or one of the "
                    "other options.",
                    "quick_replies": self.QUICK_REPLY_OPTIONS,
                }
            )


# ---------- Bot Onboarding World -------- #
class LIGHTBotOnboardWorld(OnboardWorld):
    """Onboarding world for LIGHT chat game, displays intro and
    explains instructions.
    """

    def __init__(self, opt, agent):
        self.debug = opt.get("is_debug", False)
        self.agent = agent
        self.episodeDone = False
        self.opt = opt

        self.service_strategy = opt["service_strategy"]

        self._log("LIGHTBotOnboardWorld initialization complete...")

        self.table_prefix = "lightbot"

    @staticmethod
    def generate_world(opt, agents, task_state=None):
        return LIGHTBotOnboardWorld(opt=opt, agent=agents[0])

    def episode_done(self):
        return self.episodeDone

    def _log(self, text):
        if self.debug:
            curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("{} DEBUG (LIGHTBotOnboardWorld): {}".format(curr_time, text))

    def parley(self):
        if not self.agent.data.get("user_name"):
            self.agent.observe(
                {"id": "", "text": "Enter your display name for the leaderboard."}
            )
            a = request_username(self.agent, self)
            if a is None:
                return False
            self.agent.data["user_name"] = a["text"]
            self.service_strategy.update_leaderboard(
                self.agent.id, username=a["text"], score=0,
            )
            self._log("Username has been updated")

        # Retrieve score, which is an approximate metric of familiarity
        lb_stats = self.service_strategy.get_player_leaderboard_stats(self.agent.id,)
        self.agent.data["total_score"] = lb_stats["score"]

        # Set to 0 if the load was too soon
        self.agent.data["total_score"] = self.agent.data.get("total_score", 0)
        self._log("Onboarding has completed...")
        self.episodeDone = True
