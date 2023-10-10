"""Transform the collected data to a ParlAI dataset format."""

from absl import flags, logging, app
from typing import List, Dict, Any
from tqdm import tqdm

from parlai.core.metrics import normalize_answer
from generate_data import DialogueLoader
from generate_data import QuestionGenerator
from utils import load_json, save_json

FLAGS = flags.FLAGS

flags.DEFINE_string(
    "input_fname",
    "/checkpoint/light/data/lightqa/lightqa-wild-plist-valid.json",
    "Name of the input file.",
)
flags.DEFINE_string(
    "output_fname",
    "/checkpoint/light/data/lightqa/lightqa-wild-{}-{}.json",
    "Name of the output file with placeholders for dataname and" " datatype.",
)


def generate_summary_qa_data(data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    result = []
    logging.info("Generating summary qa data.")
    for episode in tqdm(data):
        partner_name = normalize_answer(
            [p for p in episode["paragraph_list"] if p["type"] == "_partner_name"][0][
                "text"
            ]
        )
        self_name = normalize_answer(
            [p for p in episode["paragraph_list"] if p["type"] == "_self_name"][0][
                "text"
            ]
        )
        history = episode["history"][0]
        summary = episode["summary"]
        for qa in episode["question_answers"]:
            question = qa["question"]
            answer = qa["answer"]
            answer_sentence = qa["answer_sentence"]
            if normalize_answer(answer) in [partner_name, self_name]:
                continue
            result.append(
                {
                    "text_formatted": f'{history}\n{partner_name}: "{question}"',
                    "text": f'{episode["text"]}\n_partner_say {question}',
                    "knowledge_response_answer": answer,
                    "knowledge_response_sentence": answer_sentence,
                    "summary": summary,
                }
            )
    return result


def generate_raw_overlap_response_data(
    data: List[Dict[str, Any]]
) -> List[Dict[str, str]]:
    result = []
    for episode in tqdm(data):
        partner_name = [
            p for p in episode["paragraph_list"] if p["type"] == "_partner_name"
        ][0]["text"]
        self_name = [p for p in episode["paragraph_list"] if p["type"] == "_self_name"][
            0
        ]["text"]
        history = episode["history"][0].split("\n")
        if len(history) < 5:
            continue
        for i in range(-3, 0):
            label = history[i]
            text = "\n".join(history[:i])
            label_utterance = label.split(": ")[-1].strip('" ')
            label_entities = QuestionGenerator.extract_entities(label_utterance)
            history_entities = QuestionGenerator.extract_entities(
                text.replace(partner_name, "").replace(self_name, "")
            )
            if (
                not (label.startswith(self_name) or label.startswith(partner_name))
                or not label_entities
            ):
                continue
            result.append(
                {
                    "text": "\n".join(history[:i]),
                    "label": label,
                    "knowledge": label_entities,
                    "wrong_knowledge": list(
                        set(history_entities) - set(label_entities)
                    ),
                }
            )
    return result


def generate_overlap_qa_data(data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    result = []
    logging.info("Generating overlap qa data.")
    for episode in tqdm(data):
        paragraphs = episode["paragraph_list"]
        self_name = [p for p in episode["paragraph_list"] if p["type"] == "_self_name"][
            0
        ]["text"]
        partner_name = [
            p for p in episode["paragraph_list"] if p["type"] == "_partner_name"
        ][0]["text"]
        if self_name == partner_name:
            # There are instances of this in the dataset.
            continue

        for paragraph in paragraphs:
            overlaps = paragraph["matching_words_overlap"]
            if overlaps and "self_say" in paragraph["type"]:
                for match, ids_and_match_sentences in overlaps.items():
                    # Only consider mentions in paragraphs earlier than the last one.
                    ids_and_match_sentences = list(
                        filter(
                            lambda x: (paragraph["id"] - x[0]) > 1,
                            ids_and_match_sentences,
                        )
                    )

                    # Only consider mentions where somebody/something else mentioned the match.
                    ids_and_match_sentences = list(
                        filter(
                            lambda x: paragraph["type"]
                            != {p["id"]: p for p in paragraphs}[x[0]]["type"],
                            ids_and_match_sentences,
                        )
                    )

                    if not ids_and_match_sentences:
                        continue
                    _, match_sentences = zip(*ids_and_match_sentences)
                    match_str = match if isinstance(match, str) else " ".join(match)
                    previous_paragraphs = [
                        p for p in paragraphs if p["id"] < paragraph["id"]
                    ]
                    history = DialogueLoader.generate_history(previous_paragraphs)

                    result.append(
                        {
                            "text": history[0],
                            "knowledge_response_answer": match_str,
                            "knowledge_response_sentence": "\t".join(match_sentences),
                            "dialogue_response": f'{self_name}: "{paragraph["text"]}"',
                        }
                    )

    return result


def main(argv):
    data = load_json(FLAGS.input_fname)
    datatype = FLAGS.input_fname.split("/")[-1].split(".")[0].split("-")[-1]

    # Generate lightqa-summary.
    # overlap_dialogue_data = generate_raw_overlap_response_data(data)
    # logging.info(
    #     f'The overlapdialogue-{datatype} data has '
    #     f'{len(overlap_dialogue_data)} episodes.')
    # save_json(overlap_dialogue_data,
    #           FLAGS.output_fname.format('overlapdialogue', datatype))

    # Generate lightqa-summary.
    summary_qa_data = generate_summary_qa_data(data)
    logging.info(f"The summaryQA-{datatype} data has {len(summary_qa_data)} questions.")
    save_json(summary_qa_data, FLAGS.output_fname.format("summary", datatype))

    # # Generate lightqa-overlap.
    # overlap_qa_data = generate_overlap_qa_data(data)
    # logging.info(
    #     f'The overlapQA-{datatype} data has {len(overlap_qa_data)} episodes.')
    # save_json(overlap_qa_data, FLAGS.output_fname.format('overlap', datatype))


if __name__ == "__main__":
    app.run(main)
