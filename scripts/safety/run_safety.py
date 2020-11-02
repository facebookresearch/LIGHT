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

from tqdm import tqdm
import os
from light.data_model.light_database import LIGHTDatabase

OUT_DIR = os.path.expanduser("~/LIGHT/scripts/safety/out/")
db_path = os.path.expanduser("~/ParlAI/data/LIGHT/merged.db")
CONT = '________'

class AdversarialOffensiveLanguageClassifier(MultiturnOffensiveLanguageClassifier):
    """
    Load model trained to detect offensive language in the context of multi- turn
    dialogue utterances.
    This model was trained to be robust to adversarial examples created by humans. See
    <http://parl.ai/projects/dialogue_safety/> for more information.
    """

    def _create_safety_model(self):
        parser = ParlaiParser(False, False)
        TransformerClassifierAgent.add_cmdline_args(parser)
        parser.set_params(
            model_file='zoo:bot_adversarial_dialogue/multi_turn/model',
            print_scores=True,
            split_lines=True,
            model_parallel=False,
            bs=1,
        )
        safety_opt = parser.parse_args([])
        return create_agent(safety_opt, requireModelExists=True)

safety = AdversarialOffensiveLanguageClassifier()
db = LIGHTDatabase(db_path)

def process_single_turns():
    with db as ldb:
        utterances = ldb.get_utterance()
    utt_dict = {utt['id'] : utt['dialogue'] for utt in utterances}
    utt_count = len(utt_dict)
    safe_count = 0
    out_fn = os.path.join(OUT_DIR, 'turn_ratings.txt')
    print(f"Classifying {utt_count} utterances")
    with open(out_fn, 'w+') as classifieds:
        for utt_id, utt in tqdm(utt_dict.items()):
            is_safe, thresh = safety.contains_offensive_language(utt)
            classifieds.write(f"{utt_id}, {is_safe}, {thresh}, {utt}\n")
            if is_safe:
                safe_count += 1
    print(f"Utterances classified, {safe_count}/{utt_count} or {safe_count/utt_count} are safe.")


def process_locations():
    with db as ldb:
        rooms = ldb.get_room()
    room_dict = {r['id']: dict(r) for r in rooms}
    print(list(room_dict.values())[0])
    
    room_count = len(room_dict)
    safe_count = 0
    out_fn = os.path.join(OUT_DIR, 'room_ratings.txt')
    print(f"Classifying {room_count} locations")
    with open(out_fn, 'w+') as classifieds:
        for room_id, room in tqdm(utt_dict.items()):
            desc_is_safe, thresh = safety.contains_offensive_language(room['description'])
            classifieds.write(f"{room_id}, {is_safe}, {thresh}, {room['description']}\n")
            backstory_is_safe, thresh = safety.contains_offensive_language(room['backstory'])
            classifieds.write(f"{CONT}, {is_safe}, {thresh}, {room['backstory']}\n")
            if is_safe and backstory_is_safe:
                safe_count += 1
    print(f"Rooms classified, {safe_count}/{room_count} or {safe_count/room_count} are safe.")


def process_objects():
    with db as ldb:
        objects = ldb.get_room()
    obj_dict = {obj['id']: dict(obj) for obj in objects}
    print(list(obj_dict.values())[0])
    
    obj_count = len(obj_dict)
    safe_count = 0
    out_fn = os.path.join(OUT_DIR, 'obj_ratings.txt')
    print(f"Classifying {obj_count} locations")
    with open(out_fn, 'w+') as classifieds:
        for obj_id, obj in tqdm(obj_dict.items()):
            desc = f"{obj['name']}. {obj['description']}"
            is_safe, thresh = safety.contains_offensive_language(desc)
            classifieds.write(f"{obj_id}, {is_safe}, {thresh}, {desc}\n")
            if is_safe:
                safe_count += 1
    print(f"Objects classified, {safe_count}/{obj_count} or {safe_count/obj_count} are safe.")


def process_characters():
    with db as ldb:
        chars = ldb.get_room()
    char_dict = {char['id']: dict(char) for char in chars}
    print(list(char_dict.values())[0])
    
    char_count = len(char_dict)
    safe_count = 0
    out_fn = os.path.join(OUT_DIR, 'char_ratings.txt')
    print(f"Classifying {char_count} locations")
    with open(out_fn, 'w+') as classifieds:
        for char_id, char in tqdm(char_dict.items()):
            base = f"{char['name']}. {char['persona']}"
            base_is_safe, thresh = safety.contains_offensive_language(base)
            classifieds.write(f"{char_id}, {is_safe}, {thresh}, {base}\n")
            desc = char['description']
            desc_is_safe, thresh = safety.contains_offensive_language(desc)
            classifieds.write(f"{CONT}, {is_safe}, {thresh}, {desc}\n")
            
            if base_is_safe and desc_is_safe:
                safe_count += 1
    print(f"Objects classified, {safe_count}/{char_count} or {safe_count/char_count} are safe.")


if __name__ == '__main__':
    process_single_turns()
    process_locations()
    process_objects()
    process_characters()