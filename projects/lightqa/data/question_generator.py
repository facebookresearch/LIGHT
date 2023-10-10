#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Generate questions from sentences.
"""

import random
import spacy

from time import sleep
from typing import List, Dict, Any, Optional, Callable, Set
from absl import logging

from nltk.corpus import stopwords
from nltk import sent_tokenize

from transformers import AutoModelWithLMHead, AutoTokenizer
from transformers import pipeline

from parlai.core.metrics import normalize_answer

# ! python -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")
STOP_WORDS = stopwords.words("english")


def safe_huggingface_loading(loading_fn: Callable, retries: int = 5, **kwargs):
    # When too many nodes try to load a huggingface model at once
    # it crashes. We need to retry loading multiple times.
    return loading_fn(**kwargs)

    retry_count = 0
    model = None
    while True:
        try:
            model = loading_fn(**kwargs)
            break
        except ValueError as e:
            retry_count += 1
            if retry_count >= retries:
                raise e

            sleep_duration = random.randint(20, 180)
            logging.info(
                f"Retry for {retry_count + 1}/{retries} after "
                f"sleep duration of {sleep_duration} seconds."
            )
            sleep(sleep_duration)
    return model


class SummarizationModel:
    def __init__(self, device: int = 0):
        self.summary_model = safe_huggingface_loading(
            loading_fn=pipeline,
            task="summarization",
            model="philschmid/bart-large-cnn-samsum",
            device=device,
        )

    def __call__(self, *args, **kwargs):
        if "max_length" not in kwargs:
            kwargs["max_length"] = min(len(args[0].split()), 100)

        return self.summary_model(*args, **kwargs)[0]["summary_text"]


class QuestionGenerator:
    def __init__(
        self,
        path: str = "mrm8488/t5-base-finetuned-question-generation-ap",
        device: int = 0,
    ):

        self.tokenizer = safe_huggingface_loading(
            loading_fn=AutoTokenizer.from_pretrained, pretrained_model_name_or_path=path
        )
        self.model = safe_huggingface_loading(
            loading_fn=AutoModelWithLMHead.from_pretrained,
            pretrained_model_name_or_path=path,
        )
        if device >= 0:
            self.model.to(f"cuda:{device}")

        self.qa_model = safe_huggingface_loading(
            loading_fn=pipeline,
            task="question-answering",
            # model='bert-large-uncased-whole-word-masking-finetuned-squad',
            model="bert-large-cased-whole-word-masking-finetuned-squad",
            device=device,
        )

    @staticmethod
    def extract_entities(
        sentence, pos=("PROPN", "NOUN"), use_named_entities=True, use_noun_chunks=True
    ):
        doc = nlp(sentence)
        results = []
        if pos:
            for token in doc:
                if token.pos_ in pos:
                    results.append(token)
        if use_named_entities:
            for ent in doc.ents:
                results.append(ent)
        if use_noun_chunks:
            for chunk in doc.noun_chunks:
                if chunk.text.lower() not in STOP_WORDS:
                    results.append(chunk)
        results = list(set([r.text for r in results]))
        return results

    def extract_answers_and_generate_questions(
        self,
        context: str,
        stop_after: int = 1,
        blocked_answers: Optional[List[str]] = None,
    ):
        questions = []
        # Extract the possible answers.
        answers = self.extract_entities(
            context,
            use_noun_chunks=True,
            use_named_entities=True,
            pos=("PROPN", "NOUN"),
        )
        random.shuffle(answers)

        if blocked_answers:
            normalized_blocked_answers = [
                normalize_answer(answer) for answer in blocked_answers
            ]
            answers = [
                answer
                for answer in answers
                if normalize_answer(answer) not in normalized_blocked_answers
            ]

        for answer in answers:
            # Generate a question for the current answer.
            question = self.get_question(answer, context)
            correct_answer, qa_out = self.reverse_check(
                answer, context, question, threshold=0.0
            )
            if correct_answer:
                # Find the knowledge response sentence.
                answer_sentence, len_count = "", 0
                for sent in sent_tokenize(context):
                    if qa_out["start"] >= len_count and qa_out["end"] < (
                        len_count + len(sent)
                    ):
                        answer_sentence = sent
                    len_count += len(sent)
                if not answer_sentence:
                    continue

                questions.append(
                    {
                        "question": question,
                        "answer": answer,
                        "answer_sentence": answer_sentence,
                        "score": qa_out["score"],
                    }
                )
                if len(questions) >= stop_after:
                    break
        return questions

    def get_question(self, answer, context, max_length=64):
        input_text = "answer: %s  context: %s </s>" % (answer, context)
        features = self.tokenizer([input_text], return_tensors="pt")
        features.to(self.model.device)

        output = self.model.generate(
            input_ids=features["input_ids"],
            attention_mask=features["attention_mask"],
            max_length=max_length,
        )
        output = self.tokenizer.decode(output[0])

        # Remove special tokens.
        output = output.split("<pad> question: ")[1]
        output = output.strip("</s>")

        return output

    def reverse_check(self, answer, context, question, threshold=0.0):
        out = self.qa_model(question=question, context=context)
        return out["answer"] == answer and out["score"] >= threshold, out
