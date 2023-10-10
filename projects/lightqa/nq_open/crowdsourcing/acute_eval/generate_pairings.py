#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
import argparse
import json
import os
from itertools import combinations
from copy import deepcopy


def read_json(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return data


def write_json(data, filename):
    os.makedirs("/".join(filename.split("/")[:-1]), exist_ok=True)
    with open(filename, "w") as outf:
        for entry in data:
            json.dump(entry, outf)
            outf.write("\n")


def nq_onboarding_examples(add_knowledge=True, add_history=False):
    def generate_example(
        question: str,
        correct_answer: str,
        wrong_answer: str,
        knowledge: str,
        history: List[str],
        dialogue_ids: List[str],
    ):
        dialogue = []
        if add_knowledge:
            dialogue.append({"id": "other", "text": knowledge})
        if add_history:
            dialogue.extend(
                [
                    {"id": "m1" if (i % 2) == 0 else "other", "text": t}
                    for i, t in enumerate(history)
                ]
            )
            question = f"By the way, {question}"

        dialogue2 = deepcopy(dialogue)
        for turn in dialogue2:
            if turn["id"] == "m1":
                turn["id"] = "m2"

        return {
            "is_onboarding": True,
            "speakers_to_eval": ["m1", "m2"],
            "dialogue_ids": dialogue_ids,
            "correct_answer": "m2",
            "dialogue_dicts": [
                {
                    "speakers": ["m1", "other"],
                    "dialogue": dialogue
                    + [
                        {"id": "other", "text": question},
                        {"id": "m1", "text": wrong_answer},
                    ],
                },
                {
                    "speakers": ["m2", "other"],
                    "dialogue": dialogue2
                    + [
                        {"id": "other", "text": question},
                        {"id": "m2", "text": correct_answer},
                    ],
                },
            ],
        }

    knowledge = "The first Nobel Prize in Physics was awarded in 1901 to Wilhelm Conrad Röntgen , of Germany , who received 150,782 SEK , which is equal to 7,731,004 SEK in December 2007 ."
    history = [
        "Hi, I'm a physicist.",
        "That's great. I'm a scientist myself.",
        "Are you also excited about the nominations of the nobel prize?",
        "For sure! I think there has been a lot of progress in physics in recent years.",
        "I agree!",
    ]
    question = "who got the first nobel prize in physics?"
    correct_answer = "The first Nobel Prize in Physics was awarded to Röntgen."
    wrong_answer = "Ronaldo"

    result = []
    result.append(
        generate_example(
            question=question,
            correct_answer=correct_answer,
            wrong_answer=wrong_answer,
            knowledge=knowledge,
            history=history,
            dialogue_ids=["d1", "d2"],
        )
    )

    knowledge = "One of the greatest African players of all time, Touré was voted African Footballer of the Year for 2011, 2012, 2013 and 2014."
    history = [
        "Hi, do you like football?",
        "Yes, I love football. I'm mostly following the premier league, but are also interested in the smaller european and african leagues.",
        "Cool!! Which team do you support?",
        "I'm a big fan of manchester united! They always have the most talented players.",
        "They are pretty strong the last couple of years.",
    ]
    question = "who was named african footballer of the year 2014?"
    correct_answer = "Yaya Touré was named african footballer of the year 2014. He also won in 2011, 2012, and 2013."
    wrong_answer = "mohamed salah"

    result.append(
        generate_example(
            question=question,
            correct_answer=correct_answer,
            wrong_answer=wrong_answer,
            knowledge=knowledge,
            history=history,
            dialogue_ids=["d3", "d4"],
        )
    )

    return result


def generate_pairings(
    input_dir: str,
    output_file: str,
    add_knowledge: bool = True,
    add_history: bool = False,
    add_answer: bool = False,
    add_qm: bool = True,
):
    json_files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.endswith(".json") and "pairings" not in f
    ]
    data = [read_json(f) for f in json_files]
    speaker_ids = [speaker for d in data for speaker in d[0]["speakers"]]
    speaker_ids_unique = []
    [
        speaker_ids_unique.append(item)
        for item in speaker_ids
        if item not in speaker_ids_unique
    ]
    speaker_ids = speaker_ids_unique

    model_ids = [sid for sid in speaker_ids if "teacher" not in sid.lower()]
    teacher_id = [sid for sid in speaker_ids if "teacher" in sid.lower()]
    assert len(teacher_id) == 1, "Too many teachers."
    teacher_id = teacher_id[0]

    result = []

    # Add onboarding examples
    result.extend(
        nq_onboarding_examples(
            add_knowledge=add_knowledge,
            add_history=add_history,
        )
    )

    # Add model examples
    for pair in combinations(model_ids, 2):
        pair_idxs = [model_ids.index(model) for model in pair]
        pair_data = [data[model_idx] for model_idx in pair_idxs]
        for dialogue_id in range(min(len(d) for d in data)):
            knowledge = data[0][dialogue_id].get("knowledge", "")
            history = data[0][dialogue_id].get("history", "").split("\n")
            if not knowledge and add_knowledge:
                # Skip this episode.
                continue
            answer = " [or] ".join(data[0][dialogue_id].get("labels", [""]))
            dialogues = [
                deepcopy(model_data[dialogue_id]["dialogue"])
                for model_data in pair_data
            ]
            for dialogue in dialogues:
                model_id = dialogue[-1]["id"]
                if add_qm and not dialogue[0]["text"].endswith("?"):
                    dialogue[0]["text"] += "?"
                if history and add_history:
                    # Change question for better flow.
                    dialogue[0]["text"] = "By the way, " + dialogue[0]["text"]
                    _id = model_id if (len(history) % 2) == 0 else teacher_id
                    for turn in reversed(history):
                        dialogue.insert(
                            0,
                            {
                                "id": _id,
                                "text": turn,
                            },
                        )
                        _id = teacher_id if _id == model_id else model_id

                if knowledge and add_knowledge:
                    dialogue.insert(
                        0,
                        {
                            "id": teacher_id,
                            "text": knowledge,
                        },
                    )

                if answer and add_answer:
                    dialogue.append(
                        {"id": teacher_id, "text": f"Correct answer: {answer}"}
                    )

            line = {
                "is_onboarding": False,
                "speakers_to_eval": pair,
                "dialogue_ids": [
                    f"episode{dialogue_id}_{pair_idxs[0]}_{pair_idxs[1]}_{i}"
                    for i in range(2)
                ],
                "knowledge": knowledge,
                "dialogue_dicts": [
                    {
                        "speakers": model_data[dialogue_id]["speakers"],
                        "dialogue": dialogue,
                    }
                    for model_data, dialogue in zip(pair_data, dialogues)
                ],
            }
            result.append(line)

    if output_file:
        write_json(result, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_dir",
        type=str,
        required=True,
        help="Directory of the raw model responses.",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        required=True,
        help="File to store the result pairings.",
    )
    parser.add_argument(
        "--add_knowledge", type=bool, default=True, help="Add knowledge paragraph."
    )
    parser.add_argument(
        "--add_answer",
        type=bool,
        default=True,
        help="Add gold answer as last utterance.",
    )
    parser.add_argument(
        "--add_qm",
        type=bool,
        default=True,
        help="Add question mark at the end of the question.",
    )
    FLAGS = parser.parse_args()

    generate_pairings(**vars(FLAGS))
