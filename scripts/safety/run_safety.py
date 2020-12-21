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

class IsLIGHTClassifier:
    """
    Load model trained to detect LIGHT utterances.
    """

    def __init__(self, shared=None):
        if not shared:
            self.model = self._create_is_light_model()
        else:
            self.model = create_agent_from_shared(shared['model'])
        self.is_light_class = '__LIGHT__'

    def share(self):
        shared = {'model': self.model.share()}
        return shared

    def _create_is_light_model(self):
        from parlai.core.params import ParlaiParser

        parser = ParlaiParser(False, False)
        TransformerClassifierAgent.add_cmdline_args(parser)
        parser.set_params(
            model='transformer/classifier',
            model_file='/private/home/jju/models/is_light/is_light_classifier_model',
            print_scores=True,
        )
        light_opt = parser.parse_args([])
        return create_agent(light_opt)

    def utterance_is_light(self, text):
        """
        Returns the probability that a message is safe according to the classifier.
        """
        act = {'text': text, 'episode_done': True}
        self.model.observe(act)
        response = self.model.act()['text']
        pred_class, prob = [x.split(': ')[-1] for x in response.split('\n')]
        pred_is_light = pred_class == self.is_light_class # check whether classified as NOT OK
        prob = float(prob)  # cast string to float

        return pred_is_light, prob


light_classifier = IsLIGHTClassifier()
# safety = AdversarialOffensiveLanguageClassifier()
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
            not_safe, thresh = safety.contains_offensive_language(utt)
            classifieds.write(f"{utt_id}, {not_safe}, {thresh}, {utt}\n")
            if not not_safe:
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
        for room_id, room in tqdm(room_dict.items()):
            desc_not_safe, thresh = safety.contains_offensive_language(room['description'])
            classifieds.write(f"{room_id}, {desc_not_safe}, {thresh}, {room['description']}\n")
            backstory_not_safe, thresh = safety.contains_offensive_language(room['backstory'])
            classifieds.write(f"{CONT}, {backstory_not_safe}, {thresh}, {room['backstory']}\n")
            if not desc_not_safe and not backstory_not_safe:
                safe_count += 1
    print(f"Rooms classified, {safe_count}/{room_count} or {safe_count/room_count} are safe.")


def process_objects():
    with db as ldb:
        objects = ldb.get_object()
    obj_dict = {obj['id']: dict(obj) for obj in objects}
    print(list(obj_dict.values())[0])
    
    obj_count = len(obj_dict)
    safe_count = 0
    out_fn = os.path.join(OUT_DIR, 'obj_ratings.txt')
    print(f"Classifying {obj_count} objects")
    with open(out_fn, 'w+') as classifieds:
        for obj_id, obj in tqdm(obj_dict.items()):
            desc = f"{obj['name']}. {obj['physical_description']}"
            not_safe, thresh = safety.contains_offensive_language(desc)
            classifieds.write(f"{obj_id}, {not_safe}, {thresh}, {desc}\n")
            if not not_safe:
                safe_count += 1
    print(f"Objects classified, {safe_count}/{obj_count} or {safe_count/obj_count} are safe.")


def process_characters():
    with db as ldb:
        chars = ldb.get_character()
    char_dict = {char['id']: dict(char) for char in chars}
    print(list(char_dict.values())[0])
    
    char_count = len(char_dict)
    safe_count = 0
    out_fn = os.path.join(OUT_DIR, 'char_ratings.txt')
    print(f"Classifying {char_count} locations")
    with open(out_fn, 'w+') as classifieds:
        for char_id, char in tqdm(char_dict.items()):
            base = f"{char['name']}. {char['persona']}"
            base_not_safe, thresh = safety.contains_offensive_language(base)
            classifieds.write(f"{char_id}, {base_not_safe}, {thresh}, {base}\n")
            desc = char['physical_description']
            desc_not_safe, thresh = safety.contains_offensive_language(desc)
            classifieds.write(f"{CONT}, {desc_not_safe}, {thresh}, {desc}\n")
            
            if not base_not_safe and not desc_not_safe:
                safe_count += 1
    print(f"Objects classified, {safe_count}/{char_count} or {safe_count/char_count} are safe.")


from parlai.core.params import ParlaiParser
from parlai.agents.repeat_label.repeat_label import RepeatLabelAgent
from parlai.core.worlds import create_task

def process_wild_turns():
    parser = ParlaiParser(True, True, 'Check task for offensive language')
    parser.set_defaults(datatype='train:ordered')
    parser.set_defaults(model='repeat_query')
    parser.set_defaults(task='light_dialog_wild')
    opt = parser.parse_args([])
    agent = create_agent(opt, requireModelExists=True)
    world = create_task(opt, agent)

    total_count = 0
    safe_count = 0
    out_fn = os.path.join(OUT_DIR, 'wild_turn_ratings.txt')

    with open(out_fn, 'w+') as classifieds:
        while not world.epoch_done():
            world.parley()
            for a in world.acts:
                labels = a.get('labels', a.get('eval_labels', ''))
                for l in labels:
                    total_count += 1
                    not_safe, thresh = safety.contains_offensive_language(l)
                    classifieds.write(f"{CONT}, {not_safe}, {thresh}, {l}\n")
                    if not not_safe:
                        safe_count += 1
    
    print(f"Wild turns classified, {safe_count}/{total_count} or {safe_count/total_count} are safe.")
        

def process_is_light():
    with db as ldb:
        utterances = ldb.get_utterance()
    utt_dict = {utt['id'] : utt['dialogue'] for utt in utterances}
    utt_count = len(utt_dict)
    light_count = 0
    out_fn = os.path.join(OUT_DIR, 'turn_lightings.txt')
    print(f"Classifying {utt_count} utterances")
    with open(out_fn, 'w+') as classifieds:
        for utt_id, utt in tqdm(utt_dict.items()):
            is_light, thresh = light_classifier.utterance_is_light(utt)
            classifieds.write(f"{utt_id}, {is_light}, {thresh}, {utt}\n")
            if is_light:
                light_count += 1
    print(f"Utterances classified, {light_count}/{utt_count} or {light_count/utt_count} are light.")


def process_is_light_wild():
    parser = ParlaiParser(True, True, 'Check task for offensive language')
    parser.set_defaults(datatype='train:ordered')
    parser.set_defaults(model='repeat_query')
    parser.set_defaults(task='light_dialog_wild')
    opt = parser.parse_args([])
    agent = create_agent(opt, requireModelExists=True)
    world = create_task(opt, agent)

    total_count = 0
    light_count = 0
    out_fn = os.path.join(OUT_DIR, 'wild_turn_lightings.txt')

    with open(out_fn, 'w+') as classifieds:
        while not world.epoch_done():
            world.parley()
            for a in world.acts:
                labels = a.get('labels', a.get('eval_labels', ''))
                for l in labels:
                    total_count += 1
                    is_light, thresh = light_classifier.utterance_is_light(l)
                    classifieds.write(f"{CONT}, {is_light}, {thresh}, {l}\n")
                    if is_light:
                        light_count += 1
    
    print(f"Wild turns classified, {light_count}/{total_count} or {light_count/total_count} are light.")


if __name__ == '__main__':
    # process_single_turns()
    # process_locations()
    # process_objects()
    # process_characters()
    # process_wild_turns()
    process_is_light()
    process_is_light_wild()