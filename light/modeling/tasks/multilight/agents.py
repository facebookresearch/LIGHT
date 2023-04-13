#!/usr/bin/env python3

# Copyright (c) Meta, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from abc import ABC, abstractclassmethod
import copy
import jsonlines
import random
import os
from typing import Dict, Optional, Tuple

from parlai.core.message import Message
from parlai.core.metrics import ExactMatchMetric, F1Metric
from parlai.core.opt import Opt
from parlai.core.params import ParlaiParser
from parlai.core.loader import register_teacher
from parlai.core.teachers import DialogTeacher
from parlai.core.torch_classifier_agent import ConfusionMatrixMetric
from parlai.utils.data import DatatypeHelper

from light.modeling.tasks.multilight.build import build, DATA_PATH
from light.modeling.tasks.multilight import constants


def _format_timestep(timestamp, first_utterance_timestamp):
    """
    Outputs timestep in the format of '00:00:00' relative to `first_utterance_timestamp`
    """
    time_delta = float(timestamp) - float(first_utterance_timestamp)
    hour = int(time_delta // 3600)
    time_delta %= 3600
    minute = int(time_delta // 60)
    time_delta %= 60
    second = int(time_delta)
    return f"{hour:02d}:{minute:02d}:{second:02d}"


def get_clean_text(message):
    return message["text"].replace("\n", " ")


def flatten_personas(personas: Dict, delim="\n"):
    personass_str_parts = []
    personass_str_parts.append("__personas__")
    personass_str_parts.extend([f"{p['name']}: {p['persona']}" for p in personas])
    personass_str_parts.append("__end-personas__")
    return delim.join(personass_str_parts)


def flatten_location(location: Dict, delim="\n"):
    location_str_parts = [
        "__location__",
        f"{location['name']}: {location['description']}",
        "__end-location__",
    ]
    return delim.join(location_str_parts)


def get_speaker_names(utt):
    return [p["name"] for p in utt["personas"]]


def get_speaker_name_from_index(utt, index):
    return utt["personas"][index]["name"]


class BaseTeacher(DialogTeacher):
    """
    Base class for multi-party chat teacher.
    The messages from this teacher are not formatted for use. Do NOT use directly!
    """

    def __init__(self, opt, shared=None):
        opt = copy.deepcopy(opt)
        build(opt)
        self.fold = DatatypeHelper.fold(opt["datatype"])
        opt["datafile"] = os.path.join(
            DATA_PATH, constants.PROCESSED_FILES_DIRNAME, f"{self.fold}.jsonl"
        )

        self.use_start_token = opt["use_start_token"]
        self.start_token = opt["start_token"]
        self.include_speaker_in_context = opt["include_speaker_in_context"]
        self.include_speaker_in_label = opt["include_speaker_in_label"]
        self.add_speaker_to_context_end = opt["add_speaker_to_context_end"]
        self.utterance_delimiter = opt["utterance_delimiter"]
        self.speaker_token_delimiter = opt["speaker_token_delimiter"]
        self.include_timestep_in_context = opt["include_timestep_in_context"]
        self.add_current_timestep_to_context = opt["add_current_timestep_to_context"]
        self.add_personas_to_context = opt["add_personas_to_context"]
        self.add_location_to_context = opt["add_location_to_context"]
        self.id = "light_multiparty_dialogue"
        self.episode_quality_tiers = self._get_data_quality_tiers(
            opt["episode_quality_tiers"]
        )
        self.speaker_quality_tiers = self._get_data_quality_tiers(
            opt["speaker_quality_tiers"]
        )

        super().__init__(opt, shared)

    @classmethod
    def add_cmdline_args(
        cls, parser: ParlaiParser, partial_opt: Optional[Opt] = None
    ) -> ParlaiParser:
        super().add_cmdline_args(parser, partial_opt)
        agent = parser.add_argument_group("MultiLIGHT Corpus Arguments")
        agent.add_argument(
            "--episode-quality-tiers",
            type=str,
            default="1,2",
            help="Comma seperated list of tiers of data quality for episodes to include. "
            "The available tiers are 1 (high), 2 (low) quality."
            " NOTE: only training data split has tiers. valid and test are only tier 1 data.",
        )
        agent.add_argument(
            "--speaker-quality-tiers",
            type=str,
            default="1,2",
            help="Comma seperated list of tiers of data quality for speakers to include. "
            "The available tiers are 1 (high), 2 (low) quality."
            " NOTE: only training data split has tiers. valid and test are only tier 1 data.",
        )
        agent.add_argument(
            "--utterance-delimiter",
            type=str,
            default="\n",
            help="A string used to separate each utterance in the context. Defaults to newline. For example, 'A: Hello\nB: Hi there'.",
        )
        agent.add_argument(
            "--include-speaker-in-label",
            type="bool",
            default=True,
            help="Whether to include speaker labels in the label. "
            "For example, message = { label: 'Rachel: Hi' } instead of message = { label: 'Hi' }",
        )
        agent.add_argument(
            "--include-speaker-in-context",
            type="bool",
            default=True,
            help="Whether to include speaker labels in the context. "
            "For example, message = { text: 'Rachel: Hi' } instead of message = { text: 'Hi' }",
        )
        agent.add_argument(
            "--add-speaker-to-context-end",
            type="bool",
            default=False,
            help="Append the current speaker (who says `label`) to the end of each context. Defaults to True.",
        )
        agent.add_argument(
            "--use-start-token",
            type="bool",
            default=False,
            help="Use start token at the beginning of each conversation, and include the first sentence as a training example.",
        )
        agent.add_argument(
            "--start-token",
            type=str,
            default=constants.START_TOKEN,
            help=f"The token to use to indicate the beginning of a conversation. Defaults to {constants.START_TOKEN}",
        )
        agent.add_argument(
            "--speaker-token-delimiter",
            type=str,
            default=":",
            help="The token to use to separate the speaker label from the actual utterance in `obs['text']`.",
        )
        agent.add_argument(
            "--include-timestep-in-context",
            type=bool,
            default=False,
            help="If true, will add the timestep as part of the context for each previous utterance.",
        )
        agent.add_argument(
            "--add-current-timestep-to-context",
            type=bool,
            default=False,
            help="If true, will add the current timestep at the end of the context.",
        )
        agent.add_argument(
            "--add-personas-to-context",
            type=bool,
            default=False,
            help="If true, will prepend the flattened persona descriptions to the context.",
        )
        agent.add_argument(
            "--add-location-to-context",
            type=bool,
            default=False,
            help="If true, will prepend the flattened location description to the context.",
        )
        return parser

    def _get_data_quality_tiers(self, tiers_str):
        tiers = set([int(t) for t in tiers_str.split(",")])
        for t in tiers:
            assert t in (
                1,
                2,
            ), f"Requested data tier ({t}) is invalid. Available tiers are 1 and 2 (only)."
        return tiers

    def get_speaker_prompt(self, utt, ts=None):
        spkr = utt["speaker"]
        return (
            f"{spkr} {ts} {self.speaker_token_delimiter}"
            if ts and self.include_timestep_in_context
            else f"{spkr}{self.speaker_token_delimiter}"
        )

    def get_utterance_context(self, utt, ts=None):
        text = get_clean_text(utt)
        if self.include_speaker_in_context:
            text = f"{self.get_speaker_prompt(utt, ts)} {text}"
        return text

    def get_utterance_label(self, utt):
        label = get_clean_text(utt)
        if self.include_speaker_in_label:
            label = f"{self.get_speaker_prompt(utt)} {label}"
        return label

    def setup_data(self, datafile):
        with jsonlines.open(datafile) as reader:
            conversations = [dl for dl in reader]

        assert conversations, "No data was loaded by teacher."

        for conv in conversations:
            if conv["quality_tier"] not in self.episode_quality_tiers:
                continue
            last_utterance_index = len(conv["messages"]) - 1

            first_utterance_timestamp = 0
            characters_index = dict()
            personas = []
            for i, c in enumerate(conv["characters"]):
                personas.append({"name": c["name"], "persona": c["persona"]})
                characters_index[c["name"]] = i + 1

            location = {
                "name": conv["location"]["name"],
                "description": conv["location"]["description"],
            }
            speaker_worker_tier = [
                wq["worker_tier"] for wq in conv["workers_quality_check"]
            ]

            context = []

            for index, utterance in enumerate(conv["messages"]):
                speaker = utterance["speaker"]
                utterance["speaker_id"] = characters_index[speaker]
                if index == 0:
                    new_episode = True
                    # Setting the start time for the relative timestamps after this.
                    first_utterance_timestamp = utterance["timestamp"]

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
                    "characters": [p["name"] for p in personas],
                    "speaker_id": utterance["speaker_id"],
                    "full_context": context,
                    "speaker_worker_tier": speaker_worker_tier[
                        self.get_utterance_speaker_id(personas, speaker)
                    ],
                    "workers_tier": speaker_worker_tier,
                    "quality_tier": conv["quality_tier"],
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
            if persona["name"] == speaker:
                return idx

    def get_extra_context_before(self, conv):
        """
        Generates the persona and location, which goes *before* the conversation context.
        """
        extra_context_before = []

        if self.add_location_to_context:
            extra_context_before.append(flatten_location(conv["location"]))
        if self.add_personas_to_context:
            extra_context_before.append(flatten_personas(conv["personas"]))
        return extra_context_before

    def get_extra_context_after(self, conv):
        """
        Generates the timestep and speaker prompt, which goes *after* the conversation context.
        """
        extra_context_after = []
        if self.add_current_timestep_to_context:
            extra_context_after.append(conv["timestep"])
        if self.add_speaker_to_context_end:
            # Adding the speaker prompt to the end of the context
            extra_context_after.append(self.get_speaker_prompt(conv))
        return extra_context_after


@register_teacher("light:multilight:AllCharactersTeacher")
class AllSpeakersTeacher(BaseTeacher):
    def __init__(self, opt, shared=None):
        super().__init__(opt, shared)
        self.id = "multilight_dialogue_:all_speakers"

    def setup_data(self, datafile):
        for utt, _ in super().setup_data(datafile):
            ret = copy.deepcopy(utt)
            extra_context_before = self.get_extra_context_before(ret)
            extra_context_after = self.get_extra_context_after(ret)

            ret["text"] = self.utterance_delimiter.join(
                extra_context_before + ret["full_context"] + extra_context_after
            )
            if utt["speaker_worker_tier"] in self.speaker_quality_tiers:
                yield ret, True

    def custom_evaluation(
        self,
        teacher_action: Message,
        labels: Optional[Tuple[str]],
        model_response: Message,
    ) -> None:
        model_response = Message(model_response)
        if model_response.is_padding() or (not model_response.get("text", None)):
            return

        # Finding speaker label accuracy, only if it was included in the teacher labels
        if self.include_speaker_in_label:
            resp = model_response.get("text")
            parts = resp.split(self.speaker_token_delimiter)

            # If model predicts a speaker label, there should be at leat two parts separted by ':'
            if len(parts) >= 2:
                predited_speaker = parts[0].strip()
            else:
                predited_speaker = "__NO_SPEAKER__"

            # The teacher will always include the correct speaker label in the 'speaker' field
            expected_speaker = (
                teacher_action.get("speaker_id")
                if self.use_bb3_context_format
                else teacher_action.get("speaker")
            )

            # Predicted speaker accuracy
            self.metrics.add(
                "speaker_acc",
                ExactMatchMetric.compute(predited_speaker, [expected_speaker]),
            )

            # unigram F1 Metric for the speech part only, removing the speaker token
            speech_text = parts[-1]
            label_speech_text = labels[0].split(self.speaker_token_delimiter)[-1]
            self.metrics.add(
                "speech_f1",
                F1Metric.compute(speech_text, [label_speech_text]),
            )


@register_teacher("light:multilight:Speaker")
class SpeakerPredictionTeacher(AllSpeakersTeacher):
    def __init__(self, opt, shared=None):
        self.add_current_turn = opt["add_current_turn"]
        super().__init__(opt, shared)
        self.id = "SpeakerPrediction"

    @classmethod
    def add_cmdline_args(
        cls, parser: ParlaiParser, partial_opt: Optional[Opt] = None
    ) -> ParlaiParser:
        super().add_cmdline_args(parser, partial_opt)
        agent = parser.add_argument_group("MultiLIGHT Speaker prediction.")
        agent.add_argument(
            "--add-current-turn",
            type="bool",
            default=False,
            help="Whether to include the current turn in the text.",
        )

    def _remove_label_speaker(self, message):
        """
        Removes the speaker when the last utterance is being added to the context.
        """
        label = message["label"]
        if self.include_speaker_in_label:
            label_speaker, label_text = label.split(self.speaker_token_delimiter, 1)
            assert (
                label_speaker.strip() == message["speaker"]
            ), "Wrong speaker in the label."
            label = label_text.strip()
        return label

    def setup_data(self, datafile):
        for utt, _e in super().setup_data(datafile):
            msg = copy.deepcopy(utt)
            current_turn_utterance = self._remove_label_speaker(msg)
            msg["label"] = msg["speaker"]
            msg["label_candidates"] = get_speaker_names(msg)
            if self.add_current_turn:
                msg["text"] = self.utterance_delimiter.join(
                    [msg["text"], current_turn_utterance]
                )
            yield msg, _e


class SingleSpeakerTeacher(ABC, BaseTeacher):
    """
    Generaes the utterances for a single character only.
    The label will be the silent token if that character doesn't speak that round.
    (Abstract class) Do NOT use directly.
    """

    def __init__(self, opt, shared=None):
        self.silence_token = opt["silence_token"]
        self.silence_token_dropout = opt["silence_token_dropout"]
        assert (
            0 <= self.silence_token_dropout <= 1
        ), "--silence-token-dropout must be a number in [0, 1]"
        super().__init__(opt, shared)

    @classmethod
    def add_cmdline_args(
        cls, parser: ParlaiParser, partial_opt: Optional[Opt] = None
    ) -> ParlaiParser:
        super().add_cmdline_args(parser, partial_opt)
        agent = parser.add_argument_group(
            "LIGHT Multiparty Chat Corpus Arguments (Single Speaker Teacher)"
        )
        agent.add_argument(
            "--silence-token",
            type=str,
            default=constants.SILENCE_TOKEN,
            help=f"The token to use to indicate the chosen speaker is silent. Defaults to {constants.SILENCE_TOKEN}",
        )
        agent.add_argument(
            "--silence-token-dropout",
            type=float,
            default=0,
            help="Dropout probability for using silence token to generate training example"
            " for sentences where the chosen speaker is not speaking. "
            "When set to 0, all silence tokens will generate training examples. "
            "When set to 1, no silence tokens will generate training examples.",
        )
        return parser

    @abstractclassmethod
    def get_speaker_index(self):
        """
        Returns the index of the speaker in the dataset (0, 1, 2)
        """

    def generate_silence_label(self, speaker):
        label = self.silence_token
        if self.include_speaker_in_label:
            label = f"{speaker}{self.speaker_token_delimiter} {label}"
        return label

    def is_this_speaker_turn(self, utt):
        return (
            self.get_utterance_speaker_id(utt["personas"], utt["speaker"])
            == self.get_speaker_index()
        )

    def setup_data(self, datafile):
        episode_needs_reset = False

        for utt, new_episode in super().setup_data(datafile):
            # checking if we need to skip this round because of the speaker tier
            if (
                utt["workers_tier"][self.get_speaker_index()]
                not in self.speaker_quality_tiers
            ):
                continue

            if new_episode:
                last_speaker_trun = -1
                turn_num = 0
            else:
                turn_num += 1

            is_silence_turn = not self.is_this_speaker_turn(utt)
            if (
                is_silence_turn
                and self.silence_token_dropout
                and random.random() < self.silence_token_dropout
            ):
                if new_episode:
                    # We keep this to reset the episode next round around.
                    episode_needs_reset = True
                continue

            if episode_needs_reset:
                # Setting new episode because we missed the original one due to silence drop out.
                episode_needs_reset = False
                new_episode = True

            ret = copy.deepcopy(utt)
            context = ret["full_context"][(last_speaker_trun + 1) :]

            if not context:
                context = [self.silence_token] if turn_num > 0 else [self.start_token]

            if last_speaker_trun < 0:
                # Only adding the extra context on the first episode that will get yielded
                ret["text"] = self.utterance_delimiter.join(
                    self.get_extra_context_before(ret) + context
                )
            else:
                ret["text"] = self.utterance_delimiter.join(context)

            # Adding the prompot to the temp_history for not keeping it in the full history.
            # There is also an extra \n to make the format more alike the other teachers.
            ret["temp_history"] = "\n".join([""] + self.get_extra_context_after(ret))

            last_speaker_trun = turn_num
            # Setting the speaker to the current speaker.
            # Even if the speaker doesn't speak, the silence term is this speaker's action.
            ret["speaker"] = get_speaker_name_from_index(utt, self.get_speaker_index())
            if is_silence_turn:
                ret["label"] = self.generate_silence_label(
                    get_speaker_name_from_index(utt, self.get_speaker_index())
                )
            else:
                last_speaker_trun += 1

            yield ret, new_episode

    def custom_evaluation(
        self,
        teacher_action: Message,
        labels: Optional[Tuple[str]],
        model_response: Message,
    ) -> None:
        if model_response.is_padding() or (not model_response.get("text", None)):
            return

        model_predicted_speak = str(self.silence_token not in model_response["text"])
        label_was_speak = str(self.silence_token not in labels[0])
        self.metrics.add(
            "self_speaker_acc",
            ExactMatchMetric.compute(model_predicted_speak, [label_was_speak]),
        )
        # Precited speaker confusion metrics
        precision, recall, f1 = ConfusionMatrixMetric.compute_metrics(
            [model_predicted_speak], [label_was_speak], "True"
        )
        self.metrics.add("self_speaker_precision", precision[0])
        self.metrics.add("self_speaker_recall", recall[0])
        self.metrics.add("self_speaker_f1", f1[0])


@register_teacher("light:multilight:speaker1")
class FirstSpeakerTeacher(SingleSpeakerTeacher):
    def __init__(self, opt, shared=None):
        super().__init__(opt, shared)
        self.id = "multilight_dialogue:first_speaker"

    def get_speaker_index(self):
        return 0


@register_teacher("light:multilight:speaker2")
class SecondSpeakerTeacher(SingleSpeakerTeacher):
    def __init__(self, opt, shared=None):
        super().__init__(opt, shared)
        self.id = "multilight_dialogue:second_speaker"

    def get_speaker_index(self):
        return 1


@register_teacher("light:multilight:speaker3")
class ThirdSpeakerTeacher(SingleSpeakerTeacher):
    def __init__(self, opt, shared=None):
        super().__init__(opt, shared)
        self.id = "multilight_dialogue:third_speaker"

    def get_speaker_index(self):
        return 2
