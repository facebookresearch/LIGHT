#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


ALL_ATYPES = ["speech", "action", "emote"]

SELF_SAY = "_self_say"
SELF_ACT = "_self_act"
SELF_EMOTE = "_self_emote"

PARTNER_SAY = "_partner_say"
PARTNER_ACT = "_partner_act"
PARTNER_EMOTE = "_partner_emote"

FUTURE_PSAY = "_future_partner_say "
FUTURE_PACT = "_future_partner_act "
FUTURE_PEMO = "_future_partner_emote "

FUTURE_PARTNER_TAG = {
    "speech": "_future_partner_say",
    "action": "_future_partner_act",
    "emote": "_future_partner_emote",
}

MISSING_SAY_TAG = "_missing_self_speech"
MISSING_ACT_TAG = "_missing_self_action"
MISSING_EMOTE_TAG = "_missing_self_emote"

NULL_ACT_TAG = "_null_act"

NULL_TAG = {"speech": "_null_say", "action": "_null_act", "emote": "_null_emote"}

USE_ACTIONS = [
    "get",
    "put",
    "drink",
    "eat",
    "steal",
    "hit",
    "hug",
    "wear",
    "wield",
    "drop",
    "give",
    "remove",
]

STOP_WORDS = list(
    set(
        [
            "i",
            "me",
            "my",
            "myself",
            "we",
            "our",
            "ours",
            "ourselves",
            "you",
            "your",
            "yours",
            "yourself",
            "yourselves",
            "he",
            "him",
            "his",
            "himself",
            "she",
            "her",
            "hers",
            "herself",
            "it",
            "its",
            "itself",
            "they",
            "them",
            "their",
            "theirs",
            "themselves",
            "what",
            "which",
            "who",
            "whom",
            "this",
            "that",
            "these",
            "those",
            "am",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "having",
            "do",
            "does",
            "did",
            "doing",
            "a",
            "an",
            "the",
            "and",
            "but",
            "if",
            "or",
            "because",
            "as",
            "until",
            "while",
            "of",
            "at",
            "by",
            "for",
            "with",
            "about",
            "against",
            "between",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "to",
            "from",
            "up",
            "down",
            "in",
            "out",
            "on",
            "off",
            "over",
            "under",
            "again",
            "further",
            "then",
            "once",
            "here",
            "there",
            "when",
            "where",
            "why",
            "how",
            "all",
            "any",
            "both",
            "each",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "nor",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "s",
            "t",
            "can",
            "will",
            "just",
            "don",
            "should",
            "now",
            "?",
            ",",
            ".",
            "!",
            '"',
            "'",
            ":",
            ";",
            "-",
            "(",
            ")",
            "am",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "having",
            "do",
            "does",
            "did",
            "doing",
            "a",
            "an",
            "the",
            "and",
            "but",
            "if",
            "or",
            "because",
            "as",
            "until",
            "while",
            "of",
            "at",
            "by",
            "for",
            "with",
            "about",
            "against",
            "between",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "to",
            "from",
            "up",
            "down",
            "in",
            "out",
            "on",
            "off",
            "over",
            "under",
            "again",
            "further",
            "then",
            "once",
            "here",
            "there",
            "when",
            "where",
            "why",
            "how",
            "all",
            "any",
            "both",
            "each",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "nor",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "s",
            "t",
            "can",
            "will",
            "just",
            "don",
            "should",
            "now",
            "?",
            ",",
            ".",
            "!",
            '"',
            "'",
            ":",
            ";",
            "-",
            "(",
            ")",
        ]
    )
)


EMOTES_STR = """frown
sigh
nod
smile
wave
stare
applaud
ponder
gasp
dance
cry
growl
yawn
laugh
nudge
scream
shrug
pout
blush
wink
grin
groan"""
ALL_EMOTES = [emote.strip() for emote in EMOTES_STR.split("\n")]
