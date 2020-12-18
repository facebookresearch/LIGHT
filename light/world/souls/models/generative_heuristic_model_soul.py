#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.world.souls.models.partner_heuristic_model_soul import PartnerHeuristicModelSoul
from parlai.core.agents import create_agent

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
        speech_opt['override'] = {
            'inference': 'beam',
            'beam_context_block_ngram': 3,
            'beam_size': 2,
            'beam_min_length': 20,
        }
        return create_agent(speech_opt, requireModelExists=True)
