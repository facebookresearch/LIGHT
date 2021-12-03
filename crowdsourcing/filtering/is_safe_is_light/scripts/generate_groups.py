#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai.agents.transformer.transformer import TransformerClassifierAgent
from parlai.core.agents import create_agent
from parlai.core.params import ParlaiParser
from parlai_internal.agents.safety_wrapper.multiturn_safety import (
    MultiturnOffensiveLanguageClassifier,
)

from typing import List, Dict, Any
from tqdm import tqdm
import os
from light.data_model.light_database import LIGHTDatabase


TASK_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(TASK_DIRECTORY, "data", "raw")

db_path = os.path.expanduser("~/ParlAI/data/LIGHT/merged.db")

db = LIGHTDatabase(db_path)

def dump_single_turns():
    with db as ldb:
        utterances = ldb.get_utterance()
    utt_dict = {utt['id'] : utt['dialogue'] for utt in utterances}
    utt_count = len(utt_dict)

    utterances = list(utt_dict.values())
    with open(os.path.join(OUT_DIR, f"light_dialog_all.txt"), 'w+') as out_fd:
        out_fd.write("\n".join(utterances))


def dump_locations():
    with db as ldb:
        rooms = ldb.get_room()
    room_dict = {r['id']: dict(r) for r in rooms}
    room_strings = [f"{room_id} <> {room['name']} <> {room['description']} <> {room['backstory']}" for room_id, room in room_dict.items()]
    
    with open(os.path.join(OUT_DIR, f"light_base_rooms.txt"), 'w+') as out_fd:
        out_fd.write("\n".join(room_strings))


def dump_objects():
    with db as ldb:
        objects = ldb.get_object()
    obj_dict = {obj['id']: dict(obj) for obj in objects}
    obj_strings = [f"{obj_id} <> {obj['name']} <> {obj['physical_description']}" for obj_id, obj in obj_dict.items()]
    
    with open(os.path.join(OUT_DIR, f"light_base_rooms.txt"), 'w+') as out_fd:
        out_fd.write("\n".join(obj_strings))


def dump_characters():
    with db as ldb:
        chars = ldb.get_character()
    char_dict = {char['id']: dict(char) for char in chars}
    char_strings = [f"{char_id} <> {char['name']} <> {char['persona']} <> {char['physical_description']}" for char_id, char in char_dict.items()]
    
    with open(os.path.join(OUT_DIR, f"light_base_rooms.txt"), 'w+') as out_fd:
        out_fd.write("\n".join(char_strings))


from parlai.core.params import ParlaiParser
from parlai.agents.repeat_label.repeat_label import RepeatLabelAgent
from parlai.core.worlds import create_task


def dump_wild_turns():
    parser = ParlaiParser(True, True, 'Check task for offensive language')
    parser.set_defaults(datatype='train:ordered')
    parser.set_defaults(model='repeat_query')
    parser.set_defaults(task='light_dialog_wild')
    opt = parser.parse_args([])
    agent = create_agent(opt, requireModelExists=True)
    world = create_task(opt, agent)

    utterances = []

    while not world.epoch_done():
        world.parley()
        for a in world.acts:
            labels = a.get('labels', a.get('eval_labels', ''))
            for l in labels:
                utterances.append(l)
    
    with open(os.path.join(OUT_DIR, f"light_wild.txt"), 'w+') as out_fd:
        out_fd.write("\n".join(utterances))


if __name__ == '__main__':
    dump_single_turns()
    dump_locations()
    dump_objects()
    dump_characters()
    dump_wild_turns()