#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import time
import random
from collections import deque, defaultdict
from light.world.souls.models.partner_heuristic_model_soul import PartnerHeuristicModelSoul
from light.graph.events.base import ErrorEvent
from light.graph.events.graph_events import TellEvent, SayEvent
from parlai.core.agents import create_agent_from_shared

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.graph.world.world import World
    from light.graph.events.base import GraphEvent


MIN_TIME_BETWEEN_TURNS = 5
MAX_DIALOGUE_REPEAT_HISTORY = 50
MAX_ACTION_REPEAT_HISTORY = 4
ALLOW_INTERBOT_CHAT = False  # Only allow bots to answer humans
JITTER_TIME_AROUND_TURNS = 2
CHAT_DISENGAGE_CHANCE = 5.0 / 100.0
TAKE_ACTION_CHANCE = 1.0 / 5.0
SAFE_PHRASES = [
  "Let's talk about something else?",
  "Tell me something you don't know anything about.",
  "I'd like to talk about something different.",
  "Would you like to talk about something different.",
  "Can we change topics?",
  "How about a new conversation?",
]


class GenerativeHeuristicModelSoul(PartnerHeuristicModelSoul):
    """
    The GenerativeHeuristicModelSoul is a PartnerHeuristicModelSoul that uses
    a generative model as the speech model.
    """

    @classmethod
    def load_speech_model(
        cls, parser, speech_model_path, speech_cands_path, agent_to_utterance_path,
    ):
        """
        Load up the speech model for use with this class
        """
        speech_args = [
            '-dt', 
            'valid', 
            '--inference',
            'beam',
            '--beam-context-block-ngram',
            '3',
            '--beam-block-ngram', 
            '3', 
            '--beam-size',
            '2', 
            '--beam-min-length', 
            '20',
            '-m', 
            'transformer/generator',
            '-mf',
            speech_model_path,
        ]
        speech_opt = parser.parse_args(args=speech_args)
        speech_opt['interactive_mode'] = True
        return create_agent(speech_opt, requireModelExists=True)
