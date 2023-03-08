#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


WORKER_REJECT_REASON = "reason_to_reject"
# The minimum acceptable number of characters per utterance.
# Agents that have less than this average during onboarding chats
# will be disqalified after the onboarding.
MIN_AVG_CHAR_LENGTH_UTTERANCES = 10
MIN_AVG_WORD_LENGTH_UTTERANCES = 5

# 30 seconds (onboarding takes 20 seconds system time already)
MIN_CONVERSATION_DURATION = 30

SAVED_DATA_WORKER_KEY = "worker"

# Violations to check in the standard AcceptabilityChecker
ACCEPTABILITY_VIOLATIONS = (
    'min_words',
    'all_caps',
    'exact_match',
    'safety',
)

ONBOARDING_LOCATION_DESCRIPTION = (
    "The throne room is a lavishly adorned stone fortification, with large purple and gold tapestries hanging on the walls. "
    "Between each tapestry there is a painting of the previous ruling families' patriarchs. At the center of the back wall sits a large throne adorned"
    "with gold and silver, with a red silk cushion on its seat."
)

ONBOARDING_PERSONA_DESCRIPTION = (
    "I guard the castle. I guard the king. I would kill to protect the royal family."
)

ONBOARDING_WELCOME_MESSAGE = (
    "Welcome! You've been assigned the character "
    "'Guard' and are in the "
    "location 'Throne room'."
)

ONBOARDING_CHAT_PARTNERS = (
    "Your chat partners are Sword-Maker and King. More details "
    "on your persona and location are available to the left."
)

ONBOARDING_MESSAGES = [
    (
        "Your Highness! This is such a magnificent room! I thank you for bestowing on me the honor to witness such greatness."
    ),
    (
        "Ha! You’re the most welcome! Any ruler would kill to have such a talented craftsman under their rule. I summoned you here since I admire your craft and I’m sure your swords would be of great use to my most loyal guard, Guard."
    ),
    (
        "Now it's your turn to speak! Please keep in mind your assigned persona (details on the left) and respond appropriately."
    ),
    (
        "You said that right, Guard! Now, why don’t you tell the Sword-maker about the time you defeated that Minotaur in the dungeon, all by yourself?"
    ),
    ("Now it's your turn to speak!"),
    (
        "How wonderful! A hero like you is the most befitting of a powerful weapon. I promise you I will give it all I have, and forge a legendary sword for you!"
    ),
    ("Now it's your turn to speak!"),
    ("Great job! Next up, please wait while " "we match you with two other workers..."),
]

ONBOARDING_KEYWORDS = [
    # Location keywords
    "throne",
    "room",
    "stone",
    "fortification",
    "purple",
    "gold",
    "tapest",
    "wall",
    "paint",
    "rule",
    "ruling",
    "famil",
    "patriarch",
    "silver",
    "silk",
    "cushion",
    "seat",
    # Persona keywords
    "guard",
    "castle",
    "king",
    "queen",
    "royal",
    "protect",
    "weapon",
    "shield",
    "sword",
    "duty",
    "SIre",
    # Scene keywords
    "weild",
    "struck",
    "strike",
    "creation",
    "beast",
    "cow",
    "minotaur",
    "dungeon",
    "court",
    "craft",
    "weapon",
    "highness",
    "obey",
    "blade",
    "knight",
    "maker",
    "fight",
    "hand",
    "fought",
    "kill",
    "slay",
    "slain",
    "bloodshed",
    "blood",
    "monster",
    "attack",
    "lord",
]

TASK_INSTRUCTIONS = [
    (
        "In this task you will have a conversation with two other people in a fantasy game setting. "
        "You will all be given characters and a description of the setting of the conversation. "
        "You should play your character, conversing as if you were your character in the provided setting."
    ),
    (
        "Anything, so long as you remain in character. "
        "If it would make sense for your character, you could try to learn about your partners, or talk about yourself, "
        "or the setting you have all been assigned to."
    ),
    (
        "Be aware the conversations you have will be made public, so act as you "
        "would e.g. on a public social network like Twitter."
    ),
    (
        "The conversation ends when all characters have spoken at least 8 turns. "
        "To avoid spamming, you're limited to sending at most 5 messages before others reply."
    ),
    (
        "Do not talk about the task itself, or about MTurk "
        "Avoid racism, sexism, hate speech, and other forms of inappropriate conversation. "
        "Avoid real world topics and locations, and instead remain in the medieval fantasy setting. "
        "Don't direct into conversations where you pretend to take actions "
        "(like 'here you go! *gives item*'), stick to strictly chat. "
        "Don't idle for too long (5 minutes) or you will be disconnected from the chat "
        "and unable to submit."
    ),
]
