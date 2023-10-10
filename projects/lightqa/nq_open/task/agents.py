#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import Optional, List, Iterable, Tuple
import random
from nltk.tokenize import sent_tokenize
import json

from parlai.core.params import ParlaiParser
from parlai.core.opt import Opt
from parlai.core.message import Message
from parlai.core.metrics import F1Metric, AverageMetric
from parlai.core.metrics import ExactMatchMetric, normalize_answer
from parlai.tasks.wizard_of_wikipedia.build import build as wow_build_data
from parlai.tasks.wizard_of_wikipedia.agents import TOKEN_LABEL, TOKEN_END_LABEL

from parlai_internal.tasks.natural_questions_retrieval.agents import (
    DefaultTeacher as NQDefaultTeacher,
)


def find_supporting_sentence(question: str, answer: str, docs: List[str]) -> str:
    """
    Finds the supporting sentence for the answer in the docs.
    """
    # Remove the title of the documents.
    for i, doc in enumerate(docs):
        if " | " in doc:
            docs[i] = ". ".join(doc.split(" | ")[1:])
    concat_docs = ". ".join(docs)
    sentences = sent_tokenize(concat_docs)

    # Sort sentences according to recall with the answer and question.
    sorted_sentences = sorted(
        sentences,
        key=lambda sentence: (
            F1Metric._prec_recall_f1_score(
                normalize_answer(answer).split(), normalize_answer(sentence).split()
            )[0],
            F1Metric._prec_recall_f1_score(
                normalize_answer(question).split(), normalize_answer(sentence).split()
            )[0],
        ),
        reverse=True,
    )

    return sorted_sentences[0]


class NQOpenTeacher(NQDefaultTeacher):
    def __init__(self, opt, shared=None):
        self.id = "NQOpenTeacher"
        super().__init__(opt, shared)

    @classmethod
    def add_cmdline_args(
        cls, parser: ParlaiParser, partial_opt: Optional[Opt] = None
    ) -> ParlaiParser:
        super().add_cmdline_args(parser, partial_opt)
        group = parser.add_argument_group("Natural Questions retrieval")
        group.add_argument(
            "--add-wow-history",
            default=False,
            type=bool,
            help="Add a conversational history from WoW to the question.",
        )
        return parser

    def setup_data(self, fold):
        data = super().setup_data(fold)
        if not self.opt["add_wow_history"]:
            for ex, done in data:
                yield ex, done
            return

        # Find matching wow dialogue.
        wow_build_data(self.opt)
        wow_filename = os.path.join(
            self.opt["datapath"], "wizard_of_wikipedia", "train.json"
        )
        with open(wow_filename, "r") as f:
            wow_data = json.load(f)
        wow_topics = set([e["chosen_topic"].lower() for e in wow_data])

        def try_find_matching_topic(q):
            for topic in wow_topics:
                if (
                    f" {topic.lower()} " in q.lower()
                    or f" {topic.lower()} " in q.lower()
                ):
                    return topic
            return None

        def context_for_topic(topic):
            context = []
            for ex in wow_data:
                if ex["chosen_topic"].lower() == topic:
                    context = [d["text"] for d in ex["dialog"]]
                    break
            # Make sure that the dialogue doesn't end on a question.
            while context and context[-1].strip().endswith("?"):
                context.pop()
            return context

        for ex, done in data:
            question = ex["text"]
            topic = try_find_matching_topic(question)
            if not topic:
                continue
            context = context_for_topic(topic)
            if not context:
                continue
            ex["history"] = "\n".join(context)
            yield ex, done

    def custom_evaluation(
        self,
        teacher_action: Message,
        labels: Optional[Tuple[str]],
        model_response: Message,
    ):
        super().custom_evaluation(teacher_action, labels, model_response)
        if "text" in model_response and model_response["text"]:
            gold_answers = json.loads(teacher_action["answers"])
            self.metrics.add(
                "norm_em",
                ExactMatchMetric.compute(
                    guess=normalize_answer(model_response["text"]),
                    answers=[normalize_answer(a) for a in gold_answers],
                ),
            )
            self.metrics.add(
                "norm_f1",
                F1Metric.compute(
                    guess=normalize_answer(model_response["text"]),
                    answers=[normalize_answer(a) for a in gold_answers],
                ),
            )
            if gold_answers:
                # Is one of the labels (answers to the question) in the model response?
                self.metrics.add(
                    "kaa",
                    AverageMetric(
                        int(
                            any(
                                [
                                    normalize_answer(gold_answer)
                                    in normalize_answer(model_response["text"])
                                    for gold_answer in gold_answers
                                ]
                            )
                        )
                    ),
                )
                # What is the maximum recall/overlap between labels and the model response?
                self.metrics.add(
                    "ka_rec",
                    AverageMetric(
                        max(
                            [
                                F1Metric._prec_recall_f1_score(
                                    normalize_answer(gold_answer).split(),
                                    normalize_answer(model_response["text"]).split(),
                                )[0]
                                for gold_answer in gold_answers
                            ]
                        )
                    ),
                )
            if "knowledge_response" in model_response:
                # Is the predicted knowledge in the model response?
                self.metrics.add(
                    "pkaa",
                    AverageMetric(
                        int(
                            normalize_answer(model_response["knowledge_response"])
                            in normalize_answer(model_response["text"])
                        )
                    ),
                )
                # What is the recall/overlap of the predicted knowledge and the model response?
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
                # What is the em score of the knowledge response?
                self.metrics.add(
                    "krm_norm_em",
                    ExactMatchMetric.compute(
                        guess=normalize_answer(model_response["knowledge_response"]),
                        answers=[normalize_answer(a) for a in gold_answers],
                    ),
                )
                # What is the f1 score of the knowledge response?
                self.metrics.add(
                    "krm_norm_f1",
                    F1Metric.compute(
                        guess=normalize_answer(model_response["knowledge_response"]),
                        answers=[normalize_answer(a) for a in gold_answers],
                    ),
                )


class NQOpenKnowledgeTeacher(NQOpenTeacher):
    """
    Teacher for open Natural Questions data.
    """

    @classmethod
    def add_cmdline_args(
        cls, parser: ParlaiParser, partial_opt: Optional[Opt] = None
    ) -> ParlaiParser:
        super().add_cmdline_args(parser, partial_opt)

        agent = parser.add_argument_group("NQ Teacher options")
        agent.add_argument(
            "--prepend-answer",
            type=bool,
            default=True,
        )

        return parser

    def __init__(self, opt, shared=None):

        self.id = "open_nq_with_answer_as_input"
        super().__init__(opt, shared)

    def setup_data(self, fold) -> Iterable[tuple]:
        episode_dict, epoch_done = super().setup_data(fold)

        if self.opt["prepend_answer"]:
            # Add one of the labels as input.
            query = episode_dict.get("text", "")
            single_label = random.choice(episode_dict.get("answers", [""]))
            text = f"{query}\n{TOKEN_LABEL} {single_label} {TOKEN_END_LABEL}"
            episode_dict.force_set("text", text)
            episode_dict.force_set("labels", [""])

        return episode_dict, epoch_done
