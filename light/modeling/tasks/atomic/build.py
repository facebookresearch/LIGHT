# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3

import os
from glob import glob
from parlai.utils.misc import msg_to_str
import random
import itertools
import pandas as pd
import json
import time
import shutil
import light.modeling.tasks.utils as utils
from light.data_model.light_database import LIGHTDatabase
import parlai.core.build_data as build_data
from parlai.core.build_data import DownloadableFile

import pandas
import json
import random
import math
import torch
import numpy as np

from tqdm import tqdm
from fitbert import FitBert
import torch.nn as nn
import string

RESOURCES = [
    DownloadableFile(
        "http://parl.ai/downloads/light_project/env/database3.db",
        "env/database3.db",
        "ed6b0c6b97b9ccd7a3083f690fa322c7dd7a33c628a5f72dc6c4ab57ff8666aa",
        zipped=False,
    ),
    DownloadableFile(
        "http://parl.ai/downloads/light_project/shared/all.dict",
        "shared/all.dict",
        "3e2856742c47d8cd8c123fa2c06654560f7793925b9ae244790960a4b362aa76",
        zipped=False,
    ),
    DownloadableFile(
        "http://parl.ai/downloads/light_project/light_atomic/atomic_tuned.tar.gz",
        "atomic/bert_raw/atomic_tuned.tar.gz",
        "8cc1d7d3c59d871d4c51ff95c74b365f9faa375bc8ada7f58372a3129fbe17e8",
        zipped=True,
    ),
    DownloadableFile(
        "https://storage.googleapis.com/ai2-mosaic/public/atomic/v1.0/atomic_data.tgz",
        "atomic/base/atomic_data.tgz",
        "f22779944e6613044d530875dd9592a333be2e3cb83d25493b36bba7c59b2ba9",
        zipped=True,
    ),
]


def download(opt, task):
    version = "v1.0"

    base_dpath = opt["light_datapath"]
    full_dpath = os.path.join(base_dpath, task)
    if not build_data.built(full_dpath, version):
        print("[building data: " + full_dpath + "]")
        if build_data.built(full_dpath):
            # An older version exists, so remove these outdated files.
            build_data.remove_dir(full_dpath)
        build_data.make_dir(full_dpath)

        # Download the data.
        for downloadable_file in RESOURCES:
            utils.download_for_light(base_dpath, downloadable_file)

        # Move the bert data to another directory
        bert_fin_path = os.path.join(base_dpath, "atomic/bert/")
        bert_orig_path = os.path.join(base_dpath, "atomic/bert_raw/atomic_tuned/bert/")
        if os.path.exists(bert_fin_path):
            build_data.remove_dir(bert_fin_path)
        shutil.move(bert_orig_path, bert_fin_path)
        build_data.remove_dir(os.path.join(base_dpath, "atomic/bert_raw"))

        # Mark the data as built.
        build_data.mark_done(bert_fin_path, version)
        build_data.mark_done(full_dpath, version)

    return full_dpath, version


def map_name(name):
    if name == "train":
        return "trn"
    elif name == "test":
        return "tst"
    else:
        return "dev"


class DataLoader(object):
    def __init__(self, opt):
        self.data = {}
        self.data["train"] = {}
        self.data["dev"] = {}
        self.data["test"] = {}

        self.sequences = {}
        self.sequences["train"] = {}
        self.sequences["dev"] = {}
        self.sequences["test"] = {}

        self.masks = {}
        self.masks["train"] = {}
        self.masks["dev"] = {}
        self.masks["test"] = {}

        self.offsets = {}
        self.offsets["train"] = {}
        self.offsets["dev"] = {}
        self.offsets["test"] = {}

    def offset_summary(self, split):
        return self.offsets[split]["total"]


def do_take_partial_dataset(data_opts):
    if data_opts.get("kr", None) is None:
        return False
    if data_opts.kr == 1:
        return False
    return True


def select_partial_dataset(data_opts, data):
    num_selections = math.ceil(data_opts.kr * len(data))
    return random.sample(data, num_selections)


class GenerationDataLoader(DataLoader):
    """
    Adapted from https://github.com/atcbosselut/comet-commonsense
    """

    def __init__(self, dpath, opt, categories):
        super(GenerationDataLoader, self).__init__(opt)

        self.categories = categories
        self.opt = opt

        for split in self.data:
            self.data[split] = {"total": []}
            self.offsets[split] = {"total": 0}

        self.special_chars = None

        self.load_data(dpath)

    def load_data(self, path):
        for split in self.data:
            file_name = "v4_atomic_{}.csv".format(map_name(split))

            df = pandas.read_csv("{}/{}".format(path, file_name), index_col=0)
            df.iloc[:, :9] = df.iloc[:, :9].apply(lambda col: col.apply(json.loads))

            for cat in self.categories:
                attr = df[cat]
                self.data[split]["total"] += utils.zipped_flatten(
                    zip(attr.index, ["<{}>".format(cat)] * len(attr), attr.values)
                )

        return False

    def shuffle_sequences(self, split="train", keys=None):
        if keys is None:
            keys = self.data[split].keys()

        for key in keys:
            idxs = list(range(len(self.data[split][key])))

            random.shuffle(idxs)

            self.sequences[split][key] = self.sequences[split][key].index_select(
                0, torch.LongTensor(idxs)
            )

            temp = [self.data[split][key][i] for i in idxs]
            self.data[split][key] = temp
            temp = [self.masks[split][key][i] for i in idxs]
            self.masks[split][key] = temp


def find_underscore_length(seq):
    start = "_"

    while start in seq:
        start += "_"
    return start[:-1]


def handle_underscores(suffix, prefix=False):
    if prefix:
        tok = "___"
    else:
        tok = find_underscore_length(suffix)

    suffix_parts = [i.strip() for i in suffix.split("{}".format(tok))]
    to_flatten = []
    for i, part in enumerate(suffix_parts):
        if part:
            to_flatten.append([part])

            if i != len(suffix_parts) - 1 and suffix_parts[i + 1]:
                to_flatten.append(["<blank>"])
        else:
            to_flatten.append(["<blank>"])

    final_suffix = utils.flatten(to_flatten)

    return final_suffix


def get_generation_sequences(opt, data, split, test):
    sequences = []
    count = 0

    for prefix, category, suffix in data[split]["total"]:
        final_prefix, final_suffix = do_example(prefix, suffix, True, True)

        final = compile_final_sequence(opt, final_prefix, final_suffix, category)

        sequences.append(final)

        count += 1

        if count > 10 and test:
            break

    return sequences


def do_example(prefix, suffix, do_prefix, do_suffix):
    final_prefix = None
    final_suffix = None

    if do_prefix:
        if "___" in prefix:
            final_prefix = handle_underscores(prefix, True)
        else:
            final_prefix = [prefix]
    if do_suffix:
        if "_" in suffix:
            final_suffix = handle_underscores(suffix)
        else:
            final_suffix = [suffix]

    return final_prefix, final_suffix


def compile_final_sequence(opt, final_prefix, final_suffix, category):
    final = []

    final.append(final_prefix)
    final.append([[category]] + final_suffix)
    return final


num_delimiter_tokens = {
    "category": 1,
    "hierarchy": 3,
    "hierarchy+label": 4,
    "category+hierarchy": 4,
    "category+hierarchy+label": 5,
}


def _get_light_entities(opt):
    """
    id_table
    COLUMNS[0, 'id', 'integer', 1, None, 1]
    COLUMNS[1, 'type', 'text', 1, None, 0]
    COLUMNS[2, 'status', 'text', 1, None, 0]
    COLUMNS[3, 'is_from_pickle', 'BOOLEAN', 1, '0', 0]
    COLUMNS[4, 'split', 'text', 0, None, 0]
    --------
    node_content_table
    COLUMNS[0, 'id', 'integer', 1, None, 1]
    COLUMNS[1, 'parent_id', 'integer', 1, None, 0]
    COLUMNS[2, 'child_id', 'integer', 1, None, 0]
    COLUMNS[3, 'edge_type', 'text', 1, None, 0]
    COLUMNS[4, 'edge_strength', 'BOOLEAN', 1, None, 0]
    --------
    text_edges_table
    COLUMNS[0, 'id', 'integer', 1, None, 1]
    COLUMNS[1, 'parent_id', 'integer', 1, None, 0]
    COLUMNS[2, 'child_text', 'text', 1, None, 0]
    COLUMNS[3, 'child_desc', 'text', 1, None, 0]
    COLUMNS[4, 'child_label', 'text', 1, None, 0]
    COLUMNS[5, 'edge_type', 'text', 1, None, 0]
    COLUMNS[6, 'edge_strength', 'BOOLEAN', 1, None, 0]
    --------
    characters_table
    COLUMNS[0, 'id', 'integer', 1, None, 1]
    COLUMNS[1, 'name', 'text', 1, None, 0]
    COLUMNS[2, 'base_id', 'integer', 1, None, 0]
    COLUMNS[3, 'persona', 'text', 1, None, 0]
    COLUMNS[4, 'physical_description', 'text', 1, None, 0]
    COLUMNS[5, 'name_prefix', 'text', 1, None, 0]
    COLUMNS[6, 'is_plural', 'float', 1, None, 0]
    COLUMNS[7, 'char_type', 'text', 1, None, 0]
    --------
    rooms_table
    COLUMNS[0, 'id', 'integer', 1, None, 1]
    COLUMNS[1, 'name', 'text', 1, None, 0]
    COLUMNS[2, 'base_id', 'integer', 1, None, 0]
    COLUMNS[3, 'description', 'text', 1, None, 0]
    COLUMNS[4, 'backstory', 'text', 1, None, 0]
    --------
    objects_table
    COLUMNS[0, 'id', 'integer', 1, None, 1]
    COLUMNS[1, 'name', 'text', 1, None, 0]
    COLUMNS[2, 'base_id', 'integer', 1, None, 0]
    COLUMNS[3, 'is_container', 'real', 1, None, 0]
    COLUMNS[4, 'is_drink', 'real', 1, None, 0]
    COLUMNS[5, 'is_food', 'real', 1, None, 0]
    COLUMNS[6, 'is_gettable', 'real', 1, None, 0]
    COLUMNS[7, 'is_surface', 'real', 1, None, 0]
    COLUMNS[8, 'is_wearable', 'real', 1, None, 0]
    COLUMNS[9, 'is_weapon', 'real', 1, None, 0]
    COLUMNS[10, 'physical_description', 'text', 1, None, 0]
    COLUMNS[11, 'name_prefix', 'text', 1, None, 0]
    COLUMNS[12, 'is_plural', 'float', 1, None, 0]
    --------
    base_characters_table
    COLUMNS[0, 'id', 'integer', 1, None, 1]
    COLUMNS[1, 'name', 'text', 1, None, 0]
    --------
    base_rooms_table
    COLUMNS[0, 'id', 'integer', 1, None, 1]
    COLUMNS[1, 'name', 'text', 1, None, 0]
    --------
    base_objects_table
    COLUMNS[0, 'id', 'integer', 1, None, 1]
    COLUMNS[1, 'name', 'text', 1, None, 0]
    """

    light_db = LIGHTDatabase(os.path.join(), read_only=True)
    light_db.use_cache = True
    light_db.__enter__()
    entities = {"characters": set(), "rooms": set(), "objects": set()}

    for k in list(light_db.cache["characters"].keys()):
        (
            id,
            name,
            base_id,
            persona,
            desc,
            prefix,
            plural,
            ctype,
        ) = light_db.get_character(id=k)[0]
        # names should be singular and of type person
        if ctype.lower() == "person" and plural == 0.0:
            entities["characters"].add(name)

    for k in list(light_db.cache["rooms"].keys()):
        room = light_db.get_room(id=k)[0]
        entities["rooms"].add(room[1])

    for k in list(light_db.cache["objects"].keys()):
        obj = light_db.get_object(id=k)[0]
        # if obj is not plural
        if obj[-1] == 0.0:
            entities["objects"].add(obj[1])

    entities = {k: list(v) for k, v in entities.items()}

    return entities


def _get_light_vocab(vocab_path):
    vocab = set()
    remove = ["__null__", "__end__", "__start__", "__unk__"]
    with open(vocab_path, "r") as f:
        for line in f:
            v, _ = line.split("\t")
            if v not in remove and v not in string.punctuation and str(v).isalpha():
                vocab.add(v)
    return list(vocab)


def _bert_fill(fitbert, sentence, to_mask, options):
    try:
        if sentence.find(to_mask) != -1:
            sentence = sentence.replace(to_mask, "***mask***")
            sentence = fitbert.fitb(sentence, options=options)
    except IndexError:
        print(sentence, len(options))
        print(sentence)
        print(options)
        print("-----")
        sentence = sentence.replace(to_mask, "")
    return sentence


def _rand_fill(sentence, to_mask, options):
    filler = random.choice(options)
    sentence = sentence.replace(to_mask, filler)
    return sentence


def build_atomic(dpath, odpath, opt):
    fill = opt["fill"]
    output_fname = os.path.join(odpath, "atomic_sample_")

    light_entities = _get_light_entities(opt)
    light_vocab = _get_light_vocab(
        os.path.join(opt["light_datapath"], "shared/all.dict")
    )

    # ATOMIC relation categories that we want
    categories = []
    # categories += ["oEffect"]
    # categories += ["oReact"]
    # categories += ["oWant"]
    # categories += ["xAttr"]
    categories += ["xEffect"]
    categories += ["xIntent"]
    categories += ["xNeed"]
    # categories += ["xReact"]
    categories += ["xWant"]
    data_all = GenerationDataLoader(dpath, opt, categories)

    if fill == "bert":
        # TODO finetune a BERT for LIGHT
        # BLM = pytorch_pretrained_bert.BertForMaskedLM.from_pretrained(model_name)
        # fitbert = FitBert(model=BLM)
        fitbert = FitBert()
        fitbert.bert = nn.DataParallel(fitbert.bert)

    def _write_data(split):
        output_file = open(output_fname + split + ".txt", "w")
        sequences = get_generation_sequences(opt, data_all.data, split, False)

        if "maxex" in opt.keys():
            maxex = min(len(sequences), int(opt["maxex"]))
            sequences = random.sample(sequences, maxex)

        label_candidates_all = {
            "<xNeed>": [],
            "<xIntent>": [],
            "<xWant>": [],
            "<xEffect>": [],
        }

        not_n_all = {
            "<xNeed>": set(),
            "<xIntent>": set(),
            "<xWant>": set(),
            "<xEffect>": set(),
        }

        skipped = set()

        for num, seq in tqdm(enumerate(sequences)):
            rel = seq[1][0][0]
            curr_cand = " ".join(seq[1][1:]).lower() + " "
            if "none" == utils.clean(curr_cand):
                skipped.add(num)
            else:
                curr_cand = curr_cand.replace("person x", "personx")
                curr_cand = curr_cand.replace(" x ", " personx ")

                curr_cand = curr_cand.replace("person y", " persony ")
                curr_cand = curr_cand.replace(" y ", " persony ")

                # if fill == 'bert':
                #    curr_cand = _bert_fill(fitbert, curr_cand, 'personx', light_entities['characters'])
                #    curr_cand = _bert_fill(fitbert, curr_cand, 'persony', light_entities['characters'])
                # elif fill == 'rand':
                curr_cand = _rand_fill(
                    curr_cand, "personx", light_entities["characters"]
                )
                curr_cand = _rand_fill(
                    curr_cand, "persony", light_entities["characters"]
                )

            ccand = utils.clean(curr_cand)
            label_candidates_all[rel].append(ccand)
            for c in categories:
                c = "<" + c + ">"
                if c != rel:
                    label_candidates_all[c].append("none")

        for c in categories:
            c = "<" + c + ">"
            not_n_all[c] = set(
                [
                    i
                    for i in range(len(label_candidates_all[c]))
                    if label_candidates_all[c][i] == "none"
                ]
            )

        for num, seq in tqdm(enumerate(sequences)):
            if num in skipped:
                continue
            text = ""
            rel = seq[1][0][0]

            label = label_candidates_all[rel][num]

            if rel == "<xNeed>":
                text += " ".join(seq[0]) + " because PersonX needed"
            elif rel == "<xIntent>":
                text += " ".join(seq[0]) + " because PersonX wanted"
            elif rel == "<xWant>":
                text += " ".join(seq[0]) + " , as a result, PersonX wants to"
            elif rel == "<xEffect>":
                text += " ".join(seq[0]) + " , as a result, PersonX"

            if fill == "bert":
                # best word to fill in according to vocab
                vocab_sample = list(
                    random.sample(light_vocab, int(len(light_vocab) / 10))
                )
                text = _bert_fill(fitbert, text, "<blank>", vocab_sample)
            elif fill == "rand":
                text = _rand_fill(
                    text,
                    "<blank>",
                    (
                        light_entities["characters"]
                        + light_entities["rooms"]
                        + light_entities["objects"]
                    ),
                )
            text = _rand_fill(text, "PersonX", light_entities["characters"])
            text = _rand_fill(text, "PersonY", light_entities["characters"])

            label_candidates = utils.get_fixed_candidates(
                list(label_candidates_all[rel]), [label], not_n_all[rel]
            )
            assert "none" not in label_candidates
            output_file.write(
                msg_to_str(
                    {
                        "text": text,
                        "labels": label,
                        "label_candidates": label_candidates,
                        "episode_done": True,
                    }
                )
                + "\n"
            )
        output_file.close()

    for spl in ["train", "dev", "test"]:
        _write_data(spl)


def build(opt):
    # Download base atomic and LIGHT db
    full_dpath, version = download(opt, "atomic")
    atomic_basepath = os.path.join(full_dpath, "base")

    # Find build options
    fill = opt["fill"]
    out_dpath = os.path.join(full_dpath, fill)

    # Build extended atomic if necessary
    if not build_data.built(out_dpath, version_string=version):
        if build_data.built(out_dpath):
            # an older version exists, so remove these outdated files.
            build_data.remove_dir(out_dpath)

        build_atomic(atomic_basepath, out_dpath, opt)
        build_data.mark_done(out_dpath, version)
