#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import numpy as np
import re
from itertools import chain
from typing import Iterable, List
import nltk
from nltk.util import ngrams
from parlai.crowdsourcing.utils.acceptability import (
    AcceptabilityChecker,
)
import constants
from spellchecker import SpellChecker


NGRAM = 3

# Threshold for detecting repetition using Jaccard Similarity
ONBOARDING_OVERLAP_THRESHOLD = 0.2
OVERLAP_THRESHOLD = 0.3
NUM_KEYWORD_MENTION = 2

# Violations
COPIED_PERSONA = 'copied persona description'
COPIED_LOCATION = 'copied location description'
COPIED_INSTRUCTION = 'copied task instructions'
REPEATS_MESSSGE = 'repeats previous messages'
TOO_SHORT = 'average message length too short'
ONBOARDING_NO_MENTION_KEYWORD = 'did not mention enough keywords during onboarding'
SPELLING = 'too many spelling errors'
REPEATS_ONBOARDING_MESSAGE = 'repeats messages from onbaording'

onboarding_messages = [
    constants.ONBOARDING_WELCOME_MESSAGE,
    constants.ONBOARDING_CHAT_PARTNERS,
    constants.ONBOARDING_PERSONA_DESCRIPTION,
    constants.ONBOARDING_LOCATION_DESCRIPTION,
] + constants.ONBOARDING_MESSAGES


re_stripper_alpha = re.compile('[^a-zA-Z]+')
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

spell = SpellChecker()


def split_words(text):
    return re_stripper_alpha.sub(' ', text).split()


def num_spelling_errors(text):
    words = split_words(text)
    misspelled = spell.unknown(words)
    return len(misspelled)


def get_ngrams(txt):
    if not txt:
        return None
    txt = txt.lower()
    sentences = (re_stripper_alpha.split(x) for x in sent_detector.tokenize(txt) if x)
    # Need to filter X because of empty 'words' from punctuation split
    ng = (ngrams(filter(None, x), NGRAM) for x in sentences if len(x) >= NGRAM)
    return list(chain(*ng))


def jaccard_distance(a, b):
    """
    Calculate the jaccard distance between sets A and B.
    """
    a = set(a)
    b = set(b)
    return 1.0 * len(a & b) / (len(a | b) + 0.001)


def too_much_overlap(a: list, b: list, threshold) -> bool:
    return jaccard_distance(a, b) > threshold


def is_valid_agent_chat_message(message, agent_id):
    return message.get('text') and message.get('id') == agent_id


def is_valid_chat_message(message):
    return message.get('text')


def repeats_message(all_messages, agent_id, threshold):
    for i in range(len(all_messages)):
        ngram = get_ngrams(all_messages[i]['text'])
        for j in range(i + 1, len(all_messages)):
            if is_valid_agent_chat_message(all_messages[j], agent_id):
                if too_much_overlap(
                    ngram, get_ngrams(all_messages[j]['text']), threshold
                ):
                    return True
    return False


def repeats_onboarding_message(all_messages, agent_id):
    for onboarding_message in onboarding_messages:
        ngram = get_ngrams(onboarding_message)
        for message in all_messages:
            if is_valid_agent_chat_message(message, agent_id):
                if too_much_overlap(
                    ngram, get_ngrams(message['text']), ONBOARDING_OVERLAP_THRESHOLD
                ):
                    return True
    return False


class MultiPartyChatChecker(AcceptabilityChecker):
    """
    ParlAI general acceptabilty checker customized for multi-party chat.
    """

    def __init__(self):
        super().__init__()

    def check_messages(
        self,
        agent_id: str,
        messages: List[str],
        location_description: str,
        persona_description: str,
        violation_types: Iterable[str] = (),
        is_onboarding: bool = False,
    ) -> str:
        threshold = ONBOARDING_OVERLAP_THRESHOLD if is_onboarding else OVERLAP_THRESHOLD
        violations = self.get_violations(
            messages, agent_id, location_description, persona_description, threshold
        )
        if is_onboarding:
            onboarding_violations = self.get_onboarding_violations(
                messages, agent_id, location_description, persona_description
            )
            if onboarding_violations:
                violations.extend(onboarding_violations)

        general_chat_violations = super().check_messages(
            self.get_merged_messages(messages, agent_id),
            False,
            violation_types,
        )
        if general_chat_violations:
            violations.extend(general_chat_violations.split(','))

        return ','.join(violations)

    def get_onboarding_violations(
        self, agent_messages, agent_id, location_description, persona_description
    ):
        violations = []
        messages = self.get_messages(agent_messages, agent_id)
        message_concat = ' '.join(messages).lower()
        keyword_count = 0
        for keyword in constants.ONBOARDING_KEYWORDS:
            if keyword.lower() in message_concat:
                keyword_count += 1
        if keyword_count < NUM_KEYWORD_MENTION:
            violations.append(ONBOARDING_NO_MENTION_KEYWORD)
        return violations

    def get_violations(
        self,
        agent_messages,
        agent_id,
        location_description,
        persona_description,
        threshold,
    ):
        violations = []
        messages = self.get_messages(agent_messages, agent_id)
        message_concat = ' '.join(messages)
        merged_messages = self.get_merged_messages(agent_messages, agent_id)
        all_messages = self.get_all_messages(agent_messages)

        # Check for excessive overlap with persona description
        persona_ngrams = get_ngrams(persona_description)
        if any(
            [
                too_much_overlap(persona_ngrams, get_ngrams(msg), threshold)
                for msg in messages
            ]
        ):
            violations.append(COPIED_PERSONA)

        # Check for excessive overlap with location description
        location_ngrams = get_ngrams(location_description)
        if any(
            [
                too_much_overlap(location_ngrams, get_ngrams(msg), threshold)
                for msg in messages
            ]
        ):
            violations.append(COPIED_LOCATION)

        # Check for excessive overlap with task instructions
        instructions_ngrams = [
            get_ngrams(instruction) for instruction in constants.TASK_INSTRUCTIONS
        ]
        if any(
            [
                too_much_overlap(ngram, get_ngrams(msg), threshold)
                for msg in messages
                for ngram in instructions_ngrams
            ]
        ):
            violations.append(COPIED_INSTRUCTION)

        # Check average response length
        avg_response_len = np.average([len(msg) for msg in merged_messages])
        if avg_response_len < constants.MIN_AVG_CHAR_LENGTH_UTTERANCES:
            violations.append(TOO_SHORT)

        # Repeats message
        if repeats_message(all_messages, agent_id, threshold):
            violations.append(REPEATS_MESSSGE)

        # Repeats onboarding message
        if repeats_onboarding_message(all_messages, agent_id):
            violations.append(REPEATS_ONBOARDING_MESSAGE)

        # Spelling errors
        if num_spelling_errors(message_concat) >= 5:
            violations.append(SPELLING)

        return violations

    def get_messages(self, agent_messages, agent_id):
        return [
            msg["text"]
            for msg in agent_messages
            if is_valid_agent_chat_message(msg, agent_id)
        ]

    def get_all_messages(self, agent_messages):
        return [msg for msg in agent_messages if is_valid_chat_message(msg)]

    def get_merged_messages(self, agent_messages, agent_id):
        """
        Get messages sent by the given agen_id. Treat multiple messages sent in the same
        turn as one message. Messages sent by the same person before others speak count
        as the same turn.

        This is done for more linient checks for
        minimum number of words per message and
        minimum number of characters per message

        e.g.
            Agent 1: Hello there!
            Agent 1: Hola hola!
            Agent 2: Heyyy!

        =>
            Agent 1: Hello there! Hola hola!
            Agent 2: Heyyy!
        """
        messages = []
        message = []
        for msg in agent_messages:
            if is_valid_agent_chat_message(msg, agent_id):
                message.append(msg['text'])
            elif len(message) > 0:
                messages.append(' '.join(message))
                message = []

        if len(message) > 0:
            messages.append(' '.join(message))

        return messages
