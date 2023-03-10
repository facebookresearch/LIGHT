#!/usr/bin/env python3

# Copyright (c) Meta, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from abc import ABC, abstractclassmethod
import copy
import jsonlines
from typing import Optional, Tuple

from parlai.core.message import Message
from parlai.core.metrics import ExactMatchMetric, F1Metric
from parlai.core.opt import Opt
from parlai.core.teachers import DialogTeacher
from parlai.core.torch_classifier_agent import ConfusionMatrixMetric
from parlai.core.params import ParlaiParser
from parlai.utils.data import DatatypeHelper
import parlai.utils.logging as logging

from parlai_internal.tasks.light_multiparty_dialogue.mutators import (
    flatten_personas,
    flatten_location,
)
from parlai.core.loader import register_teacher

from light.modeling.tasks.multilight.build import build


class BaseTeacher(DialogTeacher):
    """
    Base (Abstract) class for multi-party chat teacher.
    (Abstract class) Do NOT use directly.
    """

    def __init__(self, opt, shared=None):
        opt = copy.deepcopy(opt)
        build(opt)
        self.fold = DatatypeHelper.fold(opt['datatype'])
        opt['datafile'] = _path(opt, f'{self.fold}.jsonl')

        self.use_start_token = opt['use_start_token']
        self.start_token = opt['start_token']
        self.include_speaker_in_context = opt['include_speaker_in_context']
        self.include_speaker_in_label = opt['include_speaker_in_label']
        self.add_speaker_to_context_end = opt['add_speaker_to_context_end']
        self.utterance_delimiter = opt['utterance_delimiter']
        self.speaker_token_delimiter = opt['speaker_token_delimiter']
        self.include_timestep_in_context = opt['include_timestep_in_context']
        self.add_current_timestep_to_context = opt['add_current_timestep_to_context']
        self.add_personas_to_context = opt['add_personas_to_context']
        self.add_location_to_context = opt['add_location_to_context']
        self.use_bb3_context_format = opt['use_bb3_context_format']
        self.id = 'light_multiparty_dialogue'
        self.episode_quality_tiers = self._get_data_quality_tiers(
            opt['episode_quality_tiers']
        )
        self.speaker_quality_tiers = self._get_data_quality_tiers(
            opt['speaker_quality_tiers']
        )

        super().__init__(opt, shared)

    @classmethod
    def add_cmdline_args(
        cls, parser: ParlaiParser, partial_opt: Optional[Opt] = None
    ) -> ParlaiParser:
        super().add_cmdline_args(parser, partial_opt)
        agent = parser.add_argument_group('LIGHT Multiparty Chat Corpus Arguments')
        agent.add_argument(
            '--episode-quality-tiers',
            type=str,
            default='1,2',
            help='Comma seperated list of tiers of data quality for episodes to include. '
            'The available tiers are 1 (high), 2 (low) quality.'
            ' NOTE: only training data split has tiers. valid and test are only tier 1 data.',
        )
        agent.add_argument(
            '--speaker-quality-tiers',
            type=str,
            default='1,2',
            help='Comma seperated list of tiers of data quality for speakers to include. '
            'The available tiers are 1 (high), 2 (low) quality.'
            ' NOTE: only training data split has tiers. valid and test are only tier 1 data.',
        )
        agent.add_argument(
            '--utterance-delimiter',
            type=str,
            default='\n',
            help="A string used to separate each utterance in the context. Defaults to newline. For example, 'A: Hello\nB: Hi there'.",
        )
        agent.add_argument(
            '--include-speaker-in-label',
            type='bool',
            default=True,
            help="Whether to include speaker labels in the label. "
            "For example, message = { label: 'Rachel: Hi' } instead of message = { label: 'Hi' }",
        )
        agent.add_argument(
            '--include-speaker-in-context',
            type='bool',
            default=True,
            help="Whether to include speaker labels in the context. "
            "For example, message = { text: 'Rachel: Hi' } instead of message = { text: 'Hi' }",
        )
        agent.add_argument(
            '--add-speaker-to-context-end',
            type='bool',
            default=False,
            help='Append the current speaker (who says `label` text) to the end of each context. Defaults to True.',
        )
        agent.add_argument(
            '--use-start-token',
            type='bool',
            default=False,
            help='Use start token at the beginning of each conversation, and include the first sentence as a training example.',
        )
        agent.add_argument(
            '--start-token',
            type=str,
            default=START_TOKEN,
            help='The token to use to indicate the beginning of a conversation. Defaults to __START__',
        )
        agent.add_argument(
            '--speaker-token-delimiter',
            type=str,
            default=':',
            help="The token to use to separate the speaker label from the actual utterance in `obs['text']`.",
        )
        agent.add_argument(
            '--include-timestep-in-context',
            type=bool,
            default=False,
            help="If true, will add the timestep as part of the context for each previous utterance.",
        )
        agent.add_argument(
            '--add-current-timestep-to-context',
            type=bool,
            default=False,
            help="If true, will add the current timestep at the end of the context.",
        )
        agent.add_argument(
            '--add-personas-to-context',
            type=bool,
            default=False,
            help="If true, will add the flattened personas to the contet end.",
        )
        agent.add_argument(
            '--add-location-to-context',
            type=bool,
            default=False,
            help="If true, will add the flattened location to the contet end.",
        )
        agent.add_argument(
            '--use-bb3-context-format',
            type=bool,
            default=False,
            help="Flattens the personas and location description with the BB3 dataset format.",
        )
        return parser

    def _get_data_quality_tiers(self, tiers_str):
        tiers = set([int(t) for t in tiers_str.split(',')])
        for t in tiers:
            assert t in (
                1,
                2,
            ), f'Requested data tier ({t}) is invalid. Available tiers are 1 and 2 (only).'
        return tiers

    def get_speaker_prompt(self, utt, ts=None):
        spkr = (
            f'Person {utt["speaker_id"]}'
            if self.use_bb3_context_format
            else utt['speaker']
        )
        return (
            f'{spkr} {ts} {self.speaker_token_delimiter}'
            if ts and self.include_timestep_in_context
            else f'{spkr}{self.speaker_token_delimiter}'
        )

    def get_utterance_context(self, utt, ts=None):
        text = _get_text(utt)
        if self.include_speaker_in_context:
            text = f'{self.get_speaker_prompt(utt, ts)} {text}'
        return text

    def get_utterance_label(self, utt):
        label = _get_text(utt)
        if self.include_speaker_in_label:
            label = f'{self.get_speaker_prompt(utt)} {label}'
        return label

    def setup_data(self, datafile):

        with jsonlines.open(datafile) as reader:
            conversations = [dl for dl in reader]

        assert conversations, 'No data was loaded by teacher.'

        for conv in conversations:
            if conv['quality_tier'] not in self.episode_quality_tiers:
                continue
            last_utterance_index = len(conv['messages']) - 1

            first_utterance_timestamp = 0
            characters_index = dict()
            personas = []
            for i, c in enumerate(conv['characters']):
                personas.append({'name': c['name'], 'persona': c['persona']})
                characters_index[c['name']] = i + 1
            _validate_personas(personas)
            location = {
                'name': conv['location']['name'],
                'description': conv['location']['description'],
            }
            speaker_worker_tier = [
                wq['worker_tier'] for wq in conv['workers_quality_check']
            ]

            context = []

            for index, utterance in enumerate(conv['messages']):

                speaker = utterance['speaker']
                utterance['speaker_id'] = characters_index[speaker]
                if index == 0:
                    new_episode = True
                    # Setting the start time for the relative timestamps after this.
                    first_utterance_timestamp = utterance['timestamp']

                    if self.use_start_token:
                        context.append(self.start_token)
                    else:
                        # If it is the first utterance,
                        # we just add it to the context for the next round.
                        context.append(
                            self.get_utterance_context(
                                utt=utterance, ts=_format_timestep(0, 0)
                            )
                        )
                        # skip the first utterance after creating the initial context.
                        continue

                isConversationDone = index == last_utterance_index

                timestamp = utterance["timestamp"]
                timestep = _format_timestep(timestamp, first_utterance_timestamp)

                yield {
                    "timestep": timestep,
                    "location": location,
                    "personas": personas,
                    "speaker": speaker,
                    "characters": [p['name'] for p in personas],
                    "speaker_id": utterance['speaker_id'],
                    "full_context": context,
                    "speaker_worker_tier": speaker_worker_tier[
                        self.get_utterance_speaker_id(personas, speaker)
                    ],
                    "workers_tier": speaker_worker_tier,
                    "quality_tier": conv['quality_tier'],
                    "text": None,  # This is an abstract class, we will feel in the text later.
                    "label": self.get_utterance_label(utterance),
                }, new_episode

                new_episode = False
                # Generating context for the next round.
                if not isConversationDone:
                    context.append(
                        self.get_utterance_context(utt=utterance, ts=timestep)
                    )

    def get_utterance_speaker_id(self, personas, speaker):
        for idx, persona in enumerate(personas):
            if persona['name'] == speaker:
                return idx

    def get_extra_context_before(self, conv):
        """
        Generates the persona and location, which goes *before* the conversation
        context.
        """
        extra_context_before = []

        if self.add_location_to_context:
            extra_context_before.append(
                flatten_location(
                    conv['location'], bb3_format=self.use_bb3_context_format
                )
            )
        if self.add_personas_to_context:
            extra_context_before.append(
                flatten_personas(
                    conv['personas'], bb3_format=self.use_bb3_context_format
                )
            )
        return extra_context_before

    def get_extra_context_after(self, conv):
        """
        Generates the timestamp and speaker prompt, which goes *after* the conversation
        context.
        """
        extra_context_after = []
        if self.add_current_timestep_to_context:
            extra_context_after.append(conv['timestep'])
        if self.add_speaker_to_context_end:
            # Adding the speaker prompt to the end of the context
            extra_context_after.append(self.get_speaker_prompt(conv))
        return extra_context_after


@register_teacher("light:multilight:AllCharactersTeacher")
class AllSpeakersTeacher(BaseTeacher):
    def __init__(self, opt, shared=None):
        opt['speaker'] = 'All'
        super().__init__(opt, shared)
        self.id = 'light_multiparty_dialogue_:all_speakers'

    def setup_data(self, datafile):
        for utt, _ in super().setup_data(datafile):
            ret = copy.deepcopy(utt)
            extra_context_before = self.get_extra_context_before(ret)
            extra_context_after = self.get_extra_context_after(ret)

            ret['text'] = self.utterance_delimiter.join(
                extra_context_before + ret['full_context'] + extra_context_after
            )
            if utt['speaker_worker_tier'] in self.speaker_quality_tiers:
                yield ret, True

    def custom_evaluation(
        self,
        teacher_action: Message,
        labels: Optional[Tuple[str]],
        model_response: Message,
    ) -> None:
        model_response = Message(model_response)
        if model_response.is_padding() or (not model_response.get('text', None)):
            return

        # Finding speaker label accuracy, only if it was included in the teacher labels
        if self.include_speaker_in_label:
            resp = model_response.get('text')
            parts = resp.split(self.speaker_token_delimiter)

            # If model predicts a speaker label, there should be at leat two parts separted by ':'
            if len(parts) >= 2:
                predited_speaker = parts[0].strip()
            else:
                predited_speaker = '__NO_SPEAKER__'

            # The teacher will always include the correct speaker label in the 'speaker' field
            expected_speaker = (
                teacher_action.get('speaker_id')
                if self.use_bb3_context_format
                else teacher_action.get('speaker')
            )

            # Predicted speaker accuracy
            self.metrics.add(
                'speaker_acc',
                ExactMatchMetric.compute(predited_speaker, [expected_speaker]),
            )

            # unigram F1 Metric for the speech part only, removing the speaker token
            speech_text = parts[-1]
            label_speech_text = labels[0].split(self.speaker_token_delimiter)[-1]
            self.metrics.add(
                'speech_f1',
                F1Metric.compute(speech_text, [label_speech_text]),
            )