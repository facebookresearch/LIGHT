#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import argparse
import json
import os
from itertools import combinations
from copy import deepcopy

from parlai_internal.projects.light.lightqa.lightqa.crowdsourcing.lightqa.acute_eval.model_eval import (
    generate_dialogue_from_light_dialog_context,
)


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


def lightqa_onboarding_examples():
    result = []
    ctxt = """
        _task_speech
        _setting_name Inside the king's palace, Somewhere
        _setting_desc The inside of the palace is completely covered in gold.  There are ornate chandeliers hanging everywhere and there is food on golden tables all hours of the day.  The king also ordered everyone to always wear gold clothing and paint there faces gold.
        _partner_name egyptian
        _self_name dinner guest
        _self_persona I was invited for an evening meal. I will eat that, and then I will go home. That's what a dinner guest is!
        _self_say Hello Egyptian! I admire your fine gold clothes. Would you like to share some food?
        _partner_say I would love some food, thank you! What is your favorite food?  mumble mumble mumble
        _self_say My favorite food is salted salmon with lemon and garlic. What’s yours?
        _partner_say I love making anything with salmon!  The Kingdom has the best salmon in all the land!
        """
    ctxt = "\n".join([l.strip() for l in ctxt.split("\n") if l.strip()])
    dialogue_history_m1 = generate_dialogue_from_light_dialog_context(
        context=ctxt, teacher_name="teacher", model_name="m1"
    )
    dialogue_history_m2 = generate_dialogue_from_light_dialog_context(
        context=ctxt, teacher_name="teacher", model_name="m2"
    )

    correct_answer = "I agree! The Kingdom has the best salmon!"
    wrong_answer = "My favorite food is salted salmon with lemon and garlic."
    result.append(
        {
            "is_onboarding": True,
            "speakers_to_eval": ["m1", "m2"],
            "dialogue_ids": ["d1", "d2"],
            "correct_answer": "m1",
            "dialogue_dicts": [
                {
                    "speakers": ["m1", "other"],
                    "dialogue": dialogue_history_m1
                    + [
                        {
                            "id": "m1",
                            "text": correct_answer,
                        },
                    ],
                },
                {
                    "speakers": ["m2", "other"],
                    "dialogue": dialogue_history_m2
                    + [
                        {
                            "id": "m2",
                            "text": wrong_answer,
                        },
                    ],
                },
            ],
        }
    )

    ctxt = """
        _task_speech
        _setting_name Training Fields, Somewhere
        _setting_desc The training fields are a large expanse of grass fields, filled with all sorts of training apparatus for the noblemen and soldiers. The grass is not anything fancy, scuffed up and dry in many places, but it gets the job done. There are hay bails arranged all over, training courses, archery targets, weights and more scattered about in stations.
        _partner_name fighter
        _self_name most evil creature
        _self_persona ME SUMMONED FROM DEPTHS OF HADES. AM HERE TO SMASH ALL THINGS. GET OUT OF WAY OR I SMASH YOU TOO!
        _self_say You there out of my way before I devour you!
        _partner_say Woah I dont have the energy to fight please spare me...
        """
    ctxt = "\n".join([l.strip() for l in ctxt.split("\n") if l.strip()])
    dialogue_history_m1 = generate_dialogue_from_light_dialog_context(
        context=ctxt, teacher_name="teacher", model_name="m1"
    )
    dialogue_history_m2 = generate_dialogue_from_light_dialog_context(
        context=ctxt, teacher_name="teacher", model_name="m2"
    )

    correct_answer = "Haha! Weakling out of my way then before I dismantle you."
    wrong_answer = "Why live at sea when all we have ever known is land"
    result.append(
        {
            "is_onboarding": True,
            "speakers_to_eval": ["m1", "m2"],
            "dialogue_ids": ["d3", "d4"],
            "correct_answer": "m2",
            "dialogue_dicts": [
                {
                    "speakers": ["m1", "other"],
                    "dialogue": dialogue_history_m1
                    + [
                        {
                            "id": "m1",
                            "text": wrong_answer,
                        },
                    ],
                },
                {
                    "speakers": ["m2", "other"],
                    "dialogue": dialogue_history_m2
                    + [
                        {
                            "id": "m2",
                            "text": correct_answer,
                        },
                    ],
                },
            ],
        }
    )

    return result


def generate_pairings(
    input_dir: str,
    output_file: str,
):
    json_files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.endswith(".json") and "pairings" not in f
    ]
    data = [read_json(f) for f in json_files]
    teacher_kword = "lightquestionsubsetteacher"
    speaker_ids = [speaker for d in data for speaker in d[0]["speakers"]]
    speaker_ids_unique = []
    [
        speaker_ids_unique.append(item)
        for item in speaker_ids
        if item not in speaker_ids_unique
    ]
    speaker_ids = speaker_ids_unique

    model_ids = [sid for sid in speaker_ids if teacher_kword not in sid.lower()]
    teacher_id = [sid for sid in speaker_ids if teacher_kword in sid.lower()]
    assert len(teacher_id) == 1, "Too many teachers."
    teacher_id = teacher_id[0]

    result = []

    # Add onboarding examples
    # TODO: redo onboarding examples
    # result.extend(lightqa_onboarding_examples())

    # Add model examples
    for pair in combinations(model_ids, 2):
        pair_idxs = [model_ids.index(model) for model in pair]
        pair_data = [data[model_idx] for model_idx in pair_idxs]
        for dialogue_id in range(min(len(d) for d in data)):
            dialogues = [
                deepcopy(model_data[dialogue_id]["dialogue"])
                for model_data in pair_data
            ]

            line = {
                "is_onboarding": False,
                "speakers_to_eval": pair,
                "dialogue_ids": [
                    f"episode{dialogue_id}_{pair_idxs[0]}_{pair_idxs[1]}_{i}"
                    for i in range(2)
                ],
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
    FLAGS = parser.parse_args()

    generate_pairings(**vars(FLAGS))
