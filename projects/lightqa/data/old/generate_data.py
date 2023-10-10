#!/usr/bin/env python3
import os
import re
import random
import spacy

from time import sleep
from datetime import datetime
from tqdm import tqdm
from string import punctuation
from typing import List, Dict, Any, Optional, Callable, Set
from collections import defaultdict
from absl import flags, logging, app

from nltk import ngrams, word_tokenize, sent_tokenize
from nltk.corpus import stopwords

from transformers import AutoModelWithLMHead, AutoTokenizer
from transformers import pipeline

from parlai.core.params import ParlaiParser
from parlai.agents.fixed_response.fixed_response import FixedResponseAgent
from parlai.core.worlds import create_task

from parlai_internal.projects.light.lightqa.data.utils import save_json

FLAGS = flags.FLAGS

flags.DEFINE_enum(
    "task",
    "light_dialog_wild",
    ["light_dialog_wild"],  # TODO: support light.
    "Name of the dataset.",
)
flags.DEFINE_enum("datatype", "train", ["train", "valid", "test"], "Data type split.")
flags.DEFINE_string(
    "output_directory", "/checkpoint/light/data/lightqa/", "Directory for output."
)

# ! python -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")
STOP_WORDS = stopwords.words("english")
PUNCTUATION = set(punctuation)


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


class DialogueLoader:
    def __init__(
        self,
        task: str = "light_dialog_wild",
        datatype: str = "train",
        n_data_chunks: int = 1,
        data_chunk_id: int = 0,
    ):
        parser = ParlaiParser(True, True, "")
        parser.add_argument("--ignore-agent-reply", type=bool, default=True)
        parser.add_argument("--display-add-fields", type=str, default="")
        parser.set_defaults(datatype=datatype)
        self.opt = parser.parse_args(["--task", task])
        self.opt["datatype"] = datatype
        self.opt["fixed_response"] = None

        self.agent = FixedResponseAgent(self.opt)
        self.world = create_task(self.opt, self.agent)
        teacher = self.world.agents[0]
        self.episodes = teacher.episodes
        data_chunk_size = len(self.episodes) // n_data_chunks
        self.episodes = self.episodes[
            data_chunk_id * data_chunk_size : (data_chunk_id + 1) * data_chunk_size
        ]

        self.dialogues = self.load_dialogue_data()

    def load_dialogue_data(self):
        stripped_episodes = []
        for episode in self.episodes:
            new_episode = []
            for turn in episode:
                text = turn.get("text", "[no text field]")
                new_episode.extend(text.split("\n"))
            stripped_episodes.append(new_episode)
        return stripped_episodes

    def get_dialogue(self, n=-1):
        dialogues = self.dialogues[:n] if n > 0 else self.dialogues

        result = []
        for dialogue in tqdm(dialogues):
            dialogue_paragraph_list = self.dialogue_to_paragraph_list(dialogue)
            history = self.generate_history(dialogue_paragraph_list)
            result.append(
                {
                    "text": "\n".join(dialogue),
                    "paragraph_list": dialogue_paragraph_list,
                    "history": history,
                }
            )
        return result

    @staticmethod
    def add_summary_questions_to_dialogue(
        dialogue: Dict[str, Any], summary_model, qg_model
    ):
        dialogue["summary"] = summary_model(dialogue["history"], max_length=100)[0][
            "summary_text"
        ]
        dialogue["question_answers"] = qg_model.extract_answers_and_generate_questions(
            dialogue["summary"]
        )

    @staticmethod
    def dialogue_to_paragraph_list(dialogue: List[str]):
        paragraphs = []
        for i, paragraph in enumerate(dialogue):
            if not paragraph.split():
                continue
            pdict = {
                "id": i,
                "type": paragraph.split()[0],  # e.g. _setting_name
                "text": " ".join(paragraph.split()[1:]),
                "entities": [],
            }
            paragraphs.append(pdict)
        return paragraphs

    @staticmethod
    def generate_history(paragraph_list: List[Dict]):
        result = []
        self_name, partner_name = "", ""
        new_dialogue = []
        for p in paragraph_list:
            if p["type"] == "_self_name":
                self_name = p["text"]
                continue
            elif p["type"] == "_partner_name":
                partner_name = p["text"]
                continue

            text = p["text"]
            if (p["type"] == "_self_say" or p["type"] == "_self_persona") and self_name:
                text = f'{self_name}: "{text}"'
            elif p["type"] == "_partner_say" and partner_name:
                text = f'{partner_name}: "{text}"'

            new_dialogue.append(text)
        result.append("\n".join(new_dialogue).strip("\n"))
        return result


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

    def extract_answers_and_generate_questions(self, context: str):
        questions = []
        # Extract the possible answers.
        answers = self.extract_entities(
            context,
            use_noun_chunks=True,
            use_named_entities=True,
            pos=("PROPN", "NOUN"),
        )
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


def clean_string(s: str, remove_sw: bool = True):
    # Remove punctutation.
    s = "".join(ch for ch in s if ch not in PUNCTUATION)

    # Remove special characters.
    s = re.sub(r"[^a-zA-Z0-9]+", " ", s)

    s = s.lower()
    if remove_sw:
        # Remove stop words.
        s = " ".join([word for word in word_tokenize(s) if word not in STOP_WORDS])
    s = s.strip()
    return s


class OverlapQuestionGenerator:
    def __init__(self, dialogues: List[Dict[str, Any]]):
        self.dialogues = dialogues

    def __call__(self, matching_fn_type: str = "large_matching_fn"):
        try:
            matching_fn = {"large_matching_fn": self.large_matching_fn}[
                matching_fn_type
            ]
        except ValueError:
            raise NotImplementedError(
                f"Matching fn {matching_fn_type} not implemented."
            )

        for dialogue in self.dialogues:
            self.add_overlap(dialogue["paragraph_list"], matching_fn)

    @staticmethod
    def large_matching_fn(text: str) -> List[str]:
        return list(
            set()
            | set(OverlapQuestionGenerator.n_gram_matching(text, n=6, remove_sw=False))
            | set(OverlapQuestionGenerator.n_gram_matching(text, n=5, remove_sw=False))
            | set(OverlapQuestionGenerator.n_gram_matching(text, n=4, remove_sw=False))
            | set(OverlapQuestionGenerator.n_gram_matching(text, n=4, remove_sw=True))
            | set(OverlapQuestionGenerator.n_gram_matching(text, n=3, remove_sw=True))
            | set(OverlapQuestionGenerator.n_gram_matching(text, n=2, remove_sw=True))
            | set(OverlapQuestionGenerator.entities_matching(text))
        )

    @staticmethod
    def add_overlap(paragraph_list: List[Dict[str, Any]], matching_fn: Callable):
        matching_lookup = defaultdict(list)

        for paragraph in paragraph_list:
            matching_words = matching_fn(paragraph["text"])

            paragraph["matching_words_overlap"] = defaultdict(list)
            for match in matching_words:
                if match in matching_lookup:
                    match_str = match if isinstance(match, str) else " ".join(match)

                    for matched_paragraph_id in matching_lookup[match]:
                        # Find the sentence it matched.
                        matched_paragraph_text = {p["id"]: p for p in paragraph_list}[
                            matched_paragraph_id
                        ]["text"]

                        # Use full paragraph as fallback.
                        matched_sentence = matched_paragraph_text
                        for sentence in sent_tokenize(matched_paragraph_text):
                            if match in matching_fn(sentence):
                                matched_sentence = sentence
                                break

                        # Disregard matches that happened across sentence boundaries.
                        if len(sent_tokenize(matched_sentence)) > 1:
                            continue

                        paragraph["matching_words_overlap"][match_str].append(
                            tuple([matched_paragraph_id, matched_sentence])
                        )

                matching_lookup[match].append(paragraph["id"])

    @staticmethod
    def n_gram_matching(sentence: str, n: int, **clean_kwargs):
        def get_ngrams(sentence: str, n: int) -> zip:
            return ngrams(word_tokenize(sentence), n)

        sentence = clean_string(sentence, **clean_kwargs)
        return [" ".join(w) for w in set(list(get_ngrams(sentence, n)))]

    @staticmethod
    def entities_matching(sentence: str, **kwargs):
        return [
            e.lower()
            for e in QuestionGenerator.extract_entities(
                sentence, pos=(), use_named_entities=False, use_noun_chunks=True
            )
        ]


def main(argv):
    n_tasks = int(os.environ.get("SLURM_NTASKS_PER_NODE", "1"))
    task_id = int(os.environ.get("SLURM_LOCALID", "0"))
    n_nodes = int(os.environ.get("SLURM_STEP_NUM_NODES", "1"))
    node_id = int(os.environ.get("SLURM_NODEID", "0"))
    job_id = int(os.environ.get("SLURM_JOB_ID", "0"))
    total_processes = n_tasks * n_nodes

    date_time = datetime.now().strftime("%Y-%m-%d-%H-%M")

    job_path = os.path.join(FLAGS.output_directory, f"{date_time}--{job_id}")
    if not (task_id == 0 and node_id == 0):
        sleep(10)
    if not os.path.isdir(job_path):
        os.mkdir(job_path)
    fname = f"{job_path}/data-{node_id}-{task_id}.{FLAGS.datatype}"

    if total_processes > 1:
        # Random sleep time to ensure not all processes trying to
        # access/download the models at the same time.
        sleep(random.randint(1, 300))

    device = task_id
    dl = DialogueLoader(
        task=FLAGS.task,
        datatype=FLAGS.datatype,
        n_data_chunks=total_processes,
        data_chunk_id=node_id * n_tasks + task_id,
    )

    dialogues = dl.get_dialogue(n=-1)

    # Add questions based on summaries.
    qg_model = QuestionGenerator(device=device)
    summary_model = safe_huggingface_loading(
        loading_fn=pipeline,
        task="summarization",
        model="philschmid/bart-large-cnn-samsum",
        device=device,
    )

    logging.info(f"Add summary and questions to dialogues.")
    for dialogue in tqdm(dialogues):
        DialogueLoader.add_summary_questions_to_dialogue(
            dialogue, summary_model=summary_model, qg_model=qg_model
        )

    # Add the overlap matching between paragraphs.
    logging.info(f"Add overlap matching.")
    oqg = OverlapQuestionGenerator(dialogues)
    oqg("large_matching_fn")

    # Save to file.
    save_json(dialogues, fname)


if __name__ == "__main__":
    app.run(main)
