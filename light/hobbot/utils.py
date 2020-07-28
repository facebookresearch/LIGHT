#!/usr/bin/env python3

# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

import json
import random
import time


SETTING_NAME = "_setting_name "
SETTING_DESC = "_setting_desc "
SELF_NAME = "_self_name "
SELF_PERSONA = "_self_persona "
PARTNER_NAME = "_partner_name "
SELF_SAY = "_self_say "
PARTNER_SAY = "_partner_say "

EMOJI_LENGTH = 6

INTRO_EMOJIS = [
    "\U0001F432",
    "\U0001F409",
    "\U0001F52E",
    "\U0001F3B2",
    "\U0001F451",
    "\U0001F56F",
    "\U0001F531",
]

GAMEPLAY_EMOJIS = INTRO_EMOJIS + [
    "\U0001F5E1",
    "\U00002694",
    "\U0001F6E1",
    "\U0000265F",
    "\U0000265E",
]

LIGHTNING = "\U000026A1"

STAR_EMOJIS = [
    "\U00002B50",
    "\U0001F31F",
    "\U0001F320",
    "\U0001F386",
    "\U00002728",
    "\U0001F3C5",
]

PLACE_EMOJIS = [
    "\U0001F947",  # 1st
    "\U0001F948",  # 2nd
    "\U0001F949",  # 3rd
]

POLICIES = [
    "Facebook will process the messages you send in "
    "playing the game in accordance with our Data Policy (facebook.com/policy). "
    "Messages you send "
    "in playing the game may be used by Facebook for research purposes "
    "and as otherwise specified in our Data Policy, and "
    "may be used by and/or shared with third parties in connection with this "
    "research.",
    "This may involve public disclosure of the messages as part "
    "of a research paper or data set. We will take measures to remove any "
    "information that directly identifies you before doing so, but cannot "
    "guarantee that messages will be completely anonymous. Do not send "
    "personal information (for example, name, "
    "address, email, or phone number) in your messages. \n\n",
    "Facebook's Community Standards apply and you may not use any "
    "racist, sexist, or otherwise offensive language, or harass other "
    "players. \n\n"
    "If you violate our policies you may be reported and blocked. ",
]

SINGLE_PLAYER_TIMEOUT = 600
OVERWORLD_TIMEOUT = 300

OVERWORLD_INSTRUCTIONS = (
    "You will be teleported into the mystical realm of LIGHT and fill the shoes "
    "of a character who lives there — playing that role you must talk with "
    "another LIGHT denizen. As you talk, your messages will be evaluated by the "
    "Dungeon Master AI. Portray your character well and they will award points! "
    "\U00002b50\U0001f31f\U0001f3c5"
    "\n"
    "If you do really well, the dungeon master will award you a badge to show "
    "your mastery of a particular character. Try to collect them all!"
    "\nNOTE: At the moment, the dungeon master can only evaluate dialogue, so "
    "refrain from taking actions.\n"
    "If at any time you want a new chat partner, type NEW GAME"
)

lightning5 = LIGHTNING * 5
wizard = "\U0001f9d9"
dice = "\U0001f3b2"
FIRST_INTRO_MESSAGES = [
    f"{lightning5} Welcome to the world of LIGHT! {lightning5} \n"
    f"The dungeon master {wizard} is trying to source potential players for "
    "the upcoming LIGHT RPG. Come try your hand! Any progress here will "
    "carry over to future releases.",
    f"{dice*3}\n" + OVERWORLD_INSTRUCTIONS,
]

REPEAT_MESSAGE = (
    f"{lightning5} Welcome back to the world of LIGHT! {lightning5} \n"
    f"The dungeon master {wizard} is glad to see you " + "again {}!\n"
    f"{dice*3}\n"
)

OPTIONS_TEXT = (
    "\n1. *INSTRUCTIONS* : view the instructions again. "
    "\n2. *CHANGE USERNAME* : change your display name for the leaderboard. "
    "\n3. *LEADERBOARD* : view the leaderboard. "
    "\n4. *CHARACTERS* : view collected character badges. "
    "\n5. *POLICIES* : reread our policies. "
)

NEW_GAME_FLASHES = [
    "Fog covers the world, and there is a blinding flash!",
    "CRASH! The world shakes and you suddenly feel yourself transported..",
    "You feel like you are sucked through your own toes and suddenly pop out somewhere else....",
    "An *excruciating* flash of light hits you for a second, and then is gone. You are left facing a whole new world...",
    "A surprisingly dense puff of smoke engulfs you, then disappears. Suddenly, you're somewhere and someone else.",
]

END_GAME_FLASHES = [
    "Well done denizen! The Dungeon Master is assigning you a new mission... ",
    "POP! The Dungeon Master appears in a cloud of magic. ",
    "Swish! A portal door opens in the thin air. The Dungeon Master strides out and turns to you. Good work! ",
    "Wait...  Who is that plodding over? It's the Dungeon Master! ",
]

SELF_CAUGHT_FLASHES = [
    "You did well enough that the Dungeon Master grants you this badge of proficiency in your character: ",
    "The Dungeon Master appreciates your role-playing, and gives you the following badge: ",
    "The Dungeon Master gives you a badge to celebrate your role-playing skills: ",
]

PARTNER_CAUGHT_FLASHES = [
    "You did so well the Dungeon Master awards you a badge for both your and your partner's characters: ",
    '"Amazing work" the Dungeon Master says, before handing you both of these badges: ',
    "Your character proficiency was so strong the Dungeon Master insisted on giving you two badges: ",
]

ALREADY_CAUGHT_FLASHES = [
    "You already had one of these, but the more the merrier I suppose.",
    "The Dungeon Master has so many of these that you can have a duplicate.",
    "Alas you already had one of these before, but you can always use another!",
]

GAME_TIMEOUT_FLASHES = [
    "A force pulls you out from this location, for you have left for too long. The Dungeon Master invites you to come back later.",
    "You're pulled back into your own reality by something, and the Dungeon Master is sad to see you go. Perhaps you'll return sometime.",
    "The potion tying you to this life wears off, and you're back as yourself. The Dungeon Master would be happy to assign you another mission later.",
]

SINGLE_PLAYER_WELCOME = (
    "Play your character and have a *conversation* with your partner, and "
    "remember that the dungeon master is watching.\n"
    "*Please enter the first message.*"
)

ONBOARD_INSTRUCTION_TEXT = (
    "You will be asked to play the following *character*. "
    "Please read it carefully: \n\n"
)

NO_CHARACTERS_TEXT = (
    "The Dungeon Master only awards character badges during particularly good bouts of roleplaying. "
    "Try to aim to get a large number of points by following your character's persona more closely, "
    "using info from the setting, or otherwise staying in character."
)

HAS_CHARACTERS_TEXT = "Here are all of the badges the Dungeon Master has awarded you for exemplary performance so far."

REPORT_BOT = (
    "Your report was successfully submitted. "
    "You reported a *bot*. "
    "Your report will be reviewed, and appropriate action will be taken. "
    "*The game is now ending.* "
)

OFFLANG = "Your message could not be processed. Please try again."

REPORTED_OFFLANG = "We are unable to respond at this time. *The game is now ending.*"

USERNAME_OFFLANG = (
    "We've found that the username you entered may contain offensive language. "
    "*Please enter another one.* You may be reported if we find that your "
    "username is in violation of our policies."
)


def agent_has_character(agent, character_name):
    """Return true if the given agent has collected the given character"""
    characters = agent.data["characters_caught"]
    character = characters[character_name.lower()]
    return character["is_caught"]


def award_agent_character(agent, character_name):
    """Give the given agent the given character, return the emoji"""
    char_str = agent.data["characters_caught_string"]
    characters = agent.data["characters_caught"]
    character = characters[character_name.lower()]
    character["is_caught"] = True
    update_idx = int(character["emoji_id"])
    new_string = char_str[:update_idx] + "1" + char_str[update_idx + 1 :]
    agent.data["characters_caught_string"] = new_string
    return character["emoji"]


def get_awarded_character_count(agent):
    """return the count of characters an agent has collected so far"""
    return agent.data["characters_caught_string"].count("1")


def get_awarded_character_emojis(agent):
    emojis = []
    for char in agent.data["characters_caught"].values():
        if char["is_caught"]:
            emojis.append(char["emoji"])
    return emojis


def get_response_timeout_loop(agent, world):
    """Get a response from the agent. If the agent times out or the
    agent wants to exit, return None. Otherwise, return the response"""
    start_time = time.time()
    a = agent.act()
    while a is None and time.time() - start_time < OVERWORLD_TIMEOUT:
        a = agent.act()
        if a is not None:
            start_time = time.time()
    if a is None:
        world.episodeDone = True
        agent.observe(
            {
                "id": "",
                "text": "Looks like you've stopped playing ... "
                "but you can return again whenever",
            }
        )
        return None

    if a["text"].upper() == "EXIT":
        world.episodeDone = True
        return None
    return a


class LIGHTPersonaGenerator(object):
    def __init__(self, path):
        # load personas
        with open(path, "rb") as personafp:
            self.personas = json.loads(personafp.read())
            self.num_personas = len(self.personas)

    # return two distinct randomly chosen personas
    def get_personas(self):
        return random.sample(self.personas, 2)

    # return one randomly chosen persona
    def get_persona(self):
        return random.choice(self.personas)

    def get_shortened_persona(self, length=2, pers=None):
        if pers is None:
            pers = self.get_persona()
        persona = pers[1].split(". ")
        to_samp = min(length, len(persona))
        p_list = random.sample(persona, to_samp)
        return p_list
