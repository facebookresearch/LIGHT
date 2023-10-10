#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
import random

from copy import deepcopy
from typing import Optional, Dict, Tuple, List
from nltk import sent_tokenize
from tqdm import tqdm

from parlai.core.teachers import DialogTeacher
from parlai.core.params import ParlaiParser
from parlai.utils.io import PathManager
from parlai.core.opt import Opt
from parlai.core.message import Message
from parlai.core.metrics import F1Metric, normalize_answer, AverageMetric
from parlai.core.agents import Agent
from parlai.tasks.wizard_of_wikipedia.agents import RareWordF1Calculator

from parlai.tasks.light_dialog_wild.agents import DefaultTeacher as LightTeacher
from parlai_internal.projects.light.lightqa.data.utils import extract_entities
from parlai_internal.projects.light.lightqa.lightqa.task.utils import (
    knowledge_from_dialogue_response,
    extract_knowledge,
)

from parlai.tasks.wizard_of_wikipedia.agents import (
    TOKEN_KNOWLEDGE,
    TOKEN_END_KNOWLEDGE,
)

from .build import build


class SummaryQATeacher(DialogTeacher):
    """
    Teacher for the SummaryQA dataset.
    """

    def __init__(self, opt, shared=None):
        self.datatype = opt["datatype"].split(":")[0]
        build(opt)
        opt["datafile"] = os.path.join(
            opt["datapath"], f"lightqa/lightqa-wild-summaryqa2-{self.datatype}.json"
        )
        self.id = "summaryqa"
        super().__init__(opt, shared)

    def setup_data(self, path):
        print("loading: " + path)
        with PathManager.open(path) as data_file:
            self.episodes = json.load(data_file)
        for ex in self.episodes:
            episode_done = ex.pop("episode_done")
            yield ex, episode_done

    def custom_evaluation(
        self, teacher_action: Message, labels, model_response: Message
    ):
        if "text" in model_response and model_response["text"]:
            normalized_response = normalize_answer(model_response["text"])

            if labels:
                normalized_labels = [normalize_answer(a) for a in labels]
                self.metrics.add(
                    "norm_f1",
                    F1Metric.compute(normalized_response, normalized_labels),
                )
                self.metrics.add(
                    "norm_em",
                    AverageMetric(int(normalized_response in normalized_labels)),
                )
                self.metrics.add(
                    "kaa",
                    AverageMetric(
                        int(any([l in normalized_response for l in normalized_labels]))
                    ),
                )

                if "knowledge_response" in model_response:
                    # Is the predicted knowledge response in the dialogue response?
                    # TODO: move to seq2seq2seq agent?
                    self.metrics.add(
                        "pkaa",
                        AverageMetric(
                            int(
                                normalize_answer(model_response["knowledge_response"])
                                in normalized_response
                            )
                        ),
                    )


class LightQATeacher(DialogTeacher):
    """
    Teacher for lightqa data.

    Can be summaryQA (old version) or overlapQA data.
    """

    @classmethod
    def add_cmdline_args(
        cls, parser: ParlaiParser, partial_opt: Optional[Opt] = None
    ) -> ParlaiParser:
        super().add_cmdline_args(parser, partial_opt)
        agent = parser.add_argument_group("LIGHTQA options")
        agent.add_argument(
            "--lightqa_dataname",
            type=str,
            default="summary",
            choices=["summary", "overlap", "overlapdialogue"],
        )
        agent.add_argument(
            "--lightqa_labeltype",
            type=str,
            default="knowledge_response_answer",
            choices=[
                "knowledge_response_answer",
                "knowledge_response_sentence",
                "knowledge_response_answer_sep_sentence",
                "dialogue_response",
            ],
        )
        agent.add_argument(
            "--lightqa_knowledge_provided",
            type=str,
            default="None",
            choices=[
                "None",
                "knowledge_response_answer",
                "knowledge_response_sentence",
                "knowledge_response_answer_sep_sentence",
            ],
        )
        agent.add_argument(
            "--lightqa_overlapdialogue_wrong_prob",
            type=float,
            default=0.1,
            help="For the overlapdialogue data, pick a wrong conditioning "
            "knowledge at random based on this probability.",
        )
        return parser

    def __init__(self, opt, shared=None):
        self.datatype = opt["datatype"]
        build(opt)
        assert opt["datatype"].split(":")[0] in [
            "train",
            "valid",
            "test",
        ], f'No datatype "{opt["datatype"]}".'
        datatype = opt["datatype"].split(":")[0]
        self.dataname = opt["lightqa_dataname"]
        opt["datafile"] = os.path.join(
            opt["datapath"],
            f"lightqa/lightqa-wild-{self.dataname}-{datatype}.json",
        )
        self.label_type = opt["lightqa_labeltype"]
        self.knowledge_provided = (
            opt["lightqa_knowledge_provided"]
            if opt["lightqa_knowledge_provided"] != "None"
            else None
        )
        self.overlapdialogue_wrong_prob = opt["lightqa_overlapdialogue_wrong_prob"]

        if self.dataname == "overlapdialogue":
            assert self.label_type in [
                "knowledge_response_answer",
                "dialogue_response",
            ], f'Label type "{self.label_type}" not supported for overlapdialogue.'
            assert self.knowledge_provided in [
                "knowledge_response_answer",
                None,
            ], f'Knowledge "{self.knowledge_provided}" not supported for overlapdialogue.'

        self.id = f'lightqa-{self.dataname}-{self.knowledge_provided or "None"}-{self.label_type}'
        super().__init__(opt, shared)

    def custom_evaluation(
        self, teacher_action: Message, labels, model_response: Message
    ):
        if "text" in model_response and model_response["text"]:
            self.metrics.add("f1", F1Metric.compute(model_response["text"], labels))

            if "knowledge_answer" in teacher_action:
                self.metrics.add(
                    "kaa",
                    AverageMetric(
                        int(
                            normalize_answer(teacher_action["knowledge_answer"])
                            in normalize_answer(model_response["text"])
                        )
                    ),
                )
                # What is the maximum recall/overlap between labels and the model response?
                self.metrics.add(
                    "ka_rec",
                    AverageMetric(
                        F1Metric._prec_recall_f1_score(
                            normalize_answer(
                                teacher_action["knowledge_answer"]
                            ).split(),
                            normalize_answer(model_response["text"]).split(),
                        )[0]
                    ),
                )
            if "knowledge_response" in model_response:
                self.metrics.add(
                    "pkaa",
                    AverageMetric(
                        int(
                            normalize_answer(model_response["knowledge_response"])
                            in normalize_answer(model_response["text"])
                        )
                    ),
                )
                # What is the maximum recall/overlap between labels and the model response?
                self.metrics.add(
                    "pka_rec",
                    AverageMetric(
                        F1Metric._prec_recall_f1_score(
                            normalize_answer(
                                model_response["knowledge_response"]
                            ).split(),
                            normalize_answer(model_response["text"]).split(),
                        )[0]
                    ),
                )

            if self.label_type == "dialogue_response" and model_response["text"]:
                # Add KnowledgeF1 between the response and the knowledge
                # provided.
                if TOKEN_KNOWLEDGE in teacher_action["text"]:
                    knowledge = (
                        teacher_action["text"].split(TOKEN_KNOWLEDGE)[-1].strip(": ")
                    )
                    self.metrics.add(
                        "kf1",
                        F1Metric.compute(model_response["text"], [knowledge]),
                    )

                if teacher_action["knowledge_answer"]:
                    self.metrics.add(
                        "kaf1",
                        F1Metric.compute(
                            model_response["text"],
                            [teacher_action["knowledge_answer"]],
                        ),
                    )

                if teacher_action["knowledge_sentence"]:
                    self.metrics.add(
                        "ksf1",
                        F1Metric.compute(
                            model_response["text"],
                            [teacher_action["knowledge_sentence"]],
                        ),
                    )
            # If we do QA, compute the normalized answer EM and F1.
            elif (
                "knowledge_response" in self.label_type
                and "text" in model_response
                and model_response["text"]
            ):
                normalized_labels = [normalize_answer(a) for a in labels]
                normalized_response = normalize_answer(model_response["text"])
                self.metrics.add(
                    "norm_f1",
                    F1Metric.compute(normalized_response, normalized_labels),
                )
                self.metrics.add(
                    "norm_em",
                    AverageMetric(int(normalized_response in normalized_labels)),
                )

            if "knowledge_response" in model_response:
                # In the StackedAgent case that's the knowledge conditioned
                # on.
                self.metrics.add(
                    "kf1_predicted",
                    F1Metric.compute(
                        model_response["text"],
                        [model_response["knowledge_response"]],
                    ),
                )
                self.metrics.add(
                    "kaa_predicted",
                    AverageMetric(
                        int(
                            normalize_answer(model_response["knowledge_response"])
                            in normalize_answer(model_response["text"])
                        )
                    ),
                )

    def _knowledge_mapping(
        self,
        knowledge_answer: str = "",
        knowledge_sentence: str = "",
        separator: str = "<SEP>",
    ) -> Dict[str, str]:
        return {
            "knowledge_response_answer": knowledge_answer,
            "knowledge_response_sentence": knowledge_sentence,
            "knowledge_response_answer_sep_sentence": f"{knowledge_answer} {separator} {knowledge_sentence}",
        }

    def setup_data(self, path):
        print("loading: " + path)

        with PathManager.open(path) as data_file:
            self.light_episodes = json.load(data_file)

        for dialogue in self.light_episodes:
            text = dialogue["text"]

            # TODO: should it be split using \t?
            knowledge_sentence = dialogue.get("knowledge_response_sentence", "").split(
                "\t"
            )[0]
            knowledge_answer = dialogue.get("knowledge_response_answer", "")
            dialogue_response = dialogue.get("dialogue_response", "")

            if self.dataname == "overlapdialogue":
                # Pick p% of the time a noun chunk that appears in the target
                # utterance and (100-p)% of the time choose another random
                # utterance that appears in the context.
                knowledge_answer = random.choice(dialogue["knowledge"])
                knowledge_answer_wrong = random.choice(dialogue["wrong_knowledge"])
                knowledge_answer = (
                    knowledge_answer
                    if random.random() > self.overlapdialogue_wrong_prob
                    else knowledge_answer_wrong
                )
                dialogue_response = dialogue["label"]

            knowledge = ""
            if self.knowledge_provided:
                knowledge = self._knowledge_mapping(
                    knowledge_answer=knowledge_answer,
                    knowledge_sentence=knowledge_sentence,
                )[self.knowledge_provided]
                text = f"{text}\n{TOKEN_KNOWLEDGE}: {knowledge}"

            label = {
                **self._knowledge_mapping(
                    knowledge_answer=knowledge_answer,
                    knowledge_sentence=knowledge_sentence,
                ),
                **{"dialogue_response": dialogue_response},
            }[self.label_type]
            yield Message(
                text=text,
                labels=(label,),
                knowledge_sentence=knowledge_sentence,
                knowledge_answer=knowledge_answer,
                knowledge=knowledge,
            ), True


class DefaultTeacher(LightQATeacher):
    pass


class RandomKnowledgeAgent(Agent):
    """
    Model that randomly chooses a knowledge response from the input.
    """

    def __init__(self, opt, shared=None):
        super().__init__(opt, shared)
        self.id = "RandomKnowledgeAgent"
        self.opt = opt

        from parlai_internal.projects.light.lightqa.data.generate_data import (
            QuestionGenerator,
        )

        self.extract_entities = QuestionGenerator.extract_entities

        assert (
            "knowledge_response" in opt["lightqa_labeltype"]
        ), "The labeltype must be some knowledge_response."

    def observe(self, observation):
        self.observation = deepcopy(observation)
        return observation

    def act(self):
        history = self.observation["text"].replace("\n", " ")

        if self.opt["lightqa_labeltype"] == "knowledge_response_answer":
            knowledge_candidates = self.extract_entities(history)
        elif self.opt["lightqa_labeltype"] == "knowledge_response_sentence":
            knowledge_candidates = sent_tokenize(history)
        else:
            raise NotImplementedError(
                f'Labeltype {self.opt["lightqa_labeltype"]} is not yet '
                "supported for RandomKnowledgeAgent."
            )
        knowledge_response = random.choice(knowledge_candidates)

        return Message(id=self.id, episode_done=False, text=knowledge_response)


class LightTeacherPlus(LightTeacher):
    """
    Standard light teacher with additional metrics.
    """

    def __init__(self, opt, shared=None):
        super().__init__(opt, shared)
        if shared and "rare_word_f1" in shared:
            self.rare_word_f1 = shared["rare_word_f1"]
        else:
            self.rare_word_f1 = self._build_rare_word_f1()

    def _build_rare_word_f1(self) -> RareWordF1Calculator:
        all_text = " ".join(
            turn["text"] for episode in self.episodes for turn in episode
        )
        return RareWordF1Calculator(all_text, top_p=0.5)

    def share(self):
        shared = super().share()
        if hasattr(self, "rare_word_f1"):
            shared["rare_word_f1"] = self.rare_word_f1
        return shared

    def custom_evaluation(
        self,
        teacher_action: Message,
        labels: Optional[Tuple[str]],
        model_response: Message,
    ):
        if "text" in model_response and labels:
            self.metrics.add(
                "rare_word_f1",
                self.rare_word_f1.compute(model_response["text"], labels),
            )
            # Dialogue response.
            normalized_response = normalize_answer(model_response["text"])
            if "knowledge_response" in model_response:
                normalized_knowledge_response = normalize_answer(
                    model_response["knowledge_response"]
                )
                self.metrics.add(
                    "pkaa",
                    AverageMetric(
                        int(normalized_knowledge_response in normalized_response)
                    ),
                )
                # Target dialogue response.
                normalized_labels = [normalize_answer(label) for label in labels]
                self.metrics.add(
                    "krm_em",
                    AverageMetric(
                        int(
                            max(
                                [
                                    normalized_knowledge_response in label
                                    for label in normalized_labels
                                ]
                            )
                        )
                    ),
                )


class LightDialogueNounChunk(LightTeacher):
    """
    Light-dialog-wild Teacher with intermediate knowledge response.

    The intermediate knowledge response is a random entity or noun chunk from the
    dialogue response.
    """

    @classmethod
    def add_cmdline_args(
        cls, parser: ParlaiParser, partial_opt: Optional[Opt] = None
    ) -> ParlaiParser:
        super().add_cmdline_args(parser, partial_opt)
        agent = parser.add_argument_group("LIGHT NC options")
        agent.add_argument(
            "--lightnc-labeltype",
            type=str,
            default="knowledge_response",
            choices=[
                "knowledge_response",
                "dialogue_response",
            ],
        )
        agent.add_argument(
            "--lightnc-knowledge-provided",
            type=str,
            default="None",
            choices=[
                "None",
                "knowledge_response",
            ],
        )
        agent.add_argument(
            "--lightnc-wrong-knowledge-provided",
            type=bool,
            default=False,
            help="Randomly provide wrong knowledge.",
        )
        return parser

    def __init__(self, opt, shared=None):
        super().__init__(opt, shared)
        assert (
            opt["lightnc_labeltype"] != opt["lightnc_knowledge_provided"]
        ), "Label already in input."
        if shared and "all_words" in shared:
            self.all_words = shared["all_words"]
        else:
            self.all_words = self._get_all_words()
        self.id = f'LightDialogueNounChunk-{opt["lightnc_labeltype"]}'

    def share(self):
        shared = super().share()
        if hasattr(self, "all_words"):
            shared["all_words"] = self.all_words
        return shared

    def _get_all_words(self):
        all_text = " ".join(
            turn["text"] for episode in self.episodes for turn in episode
        )
        all_words = [w for w in all_text.split() if not w.startswith("_")]
        return all_words

    def get_wrong_knowledge(
        self, dialogue_response: str, context: Optional[str] = None
    ) -> List[str]:
        if not context:
            # Use a random context.
            context_length = 100
            random_start = random.randint(0, len(self.all_words) - (context_length + 1))
            context = " ".join(
                self.all_words[random_start : random_start + context_length]
            )

        return list(
            set(extract_knowledge(context)) - set(extract_knowledge(dialogue_response))
        )

    def next_example(self):
        ex, epoch_done = super().next_example()

        label_key = "eval_labels" if "eval_labels" in ex else "labels"
        if label_key not in ex or "text" not in ex:
            return ex, epoch_done

        text = ex.pop("text")
        dialogue_response = ex[label_key]
        if not isinstance(dialogue_response, str):
            dialogue_response = dialogue_response[0]

        if self.opt["lightnc_labeltype"] == "knowledge_response":
            knowledge = knowledge_from_dialogue_response(dialogue_response)
            ex.force_set(label_key, [knowledge])
            ex["text"] = text

        elif self.opt["lightnc_knowledge_provided"] == "knowledge_response":
            knowledge = knowledge_from_dialogue_response(dialogue_response)
            if self.opt["lightnc_wrong_knowledge_provided"]:
                # Add the probability as int between 0-10 to the input.
                p = random.random()
                if random.random() > p:
                    # Replace the knowledge with incorrect one.
                    wrong_knowledge = self.get_wrong_knowledge(
                        dialogue_response, context=text
                    )
                    if wrong_knowledge:
                        knowledge = random.choice(wrong_knowledge)

                confidence = round(p * 10)
                text += f"\n{TOKEN_KNOWLEDGE} {confidence}: {knowledge} {TOKEN_END_KNOWLEDGE}"
            else:
                text += f"\n{TOKEN_KNOWLEDGE} {knowledge} {TOKEN_END_KNOWLEDGE}"
            ex["text"] = text

        return ex, epoch_done


class LightQuestionSubsetTeacher(LightTeacher):
    def _question_episode_subset(self):
        """
        Find episodes that have a question in there that are "answered" with a noun
        chunk from the description text.
        """

        def flatten_to_longest(episode):
            flat_episode = [
                Message(
                    {
                        "text": "\n".join([turn["text"] for turn in episode]),
                        "episode_done": True,
                        "labels": episode[-1]["labels"],
                    }
                )
            ]
            return flat_episode

        res = []
        for episode in tqdm(self.episodes, desc="Find question episodes"):
            for i, turn in enumerate(episode):
                if turn["text"].endswith("?") and i > 0:
                    # The episode contains a question.
                    conv_history = [
                        utt for t in episode[:i] for utt in t["text"].split("\n")
                    ]
                    # Remove type.
                    cln_conv_history = [
                        " ".join(utt.split(" ")[1:]) for utt in conv_history
                    ]
                    # history = ' '.join(cln_conv_history)
                    # Only use the setting description as history.
                    history = cln_conv_history[2]
                    response = turn["labels"][0]

                    if response.endswith("?"):
                        continue

                    history_ent = extract_entities(history)
                    response_ent = extract_entities(response)
                    if any([ent in history_ent for ent in response_ent]):
                        # match
                        turn.force_set("episode_done", True)
                        res.append(flatten_to_longest(episode[: i + 1]))
        print(f"Total: {len(res)}/{len(self.episodes)} episodes.")
        return res

    def _setup_data(self, path):
        super()._setup_data(path)
        self.episodes = self._question_episode_subset()
        self.num_exs = len(self.episodes)
