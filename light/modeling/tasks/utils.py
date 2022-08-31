# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3


"""
Some adapted from https://github.com/atcbosselut/comet-commonsense
"""

import json
import copy
import os

import torch

import numpy as np
import contextlib

from distutils.dir_util import mkpath
import parlai.core.build_data as build_data

from tqdm import tqdm

import re


def get_fixed_candidates(data_all, data, not_n=None):
    if not_n is None:
        not_n = set()
    not_n.update([data_all.index(d) for d in data])
    rrange = np.delete(
        np.arange(0, len(data_all), dtype="int32"), np.array(list(not_n))
    )
    num_candidates = min(100 - len(data), int(0.5 * len(data_all)))
    np.random.shuffle(rrange)
    rrange = list(rrange)
    rrange = rrange[:num_candidates]
    candidates = [data_all[i] for i in rrange]
    candidates += data
    return candidates


def get_pairs(word):
    """
    Return set of symbol pairs in a word.
    word is represented as tuple of symbols (symbols being variable-length strings)
    """
    pairs = set()
    prev_char = word[0]
    for char in word[1:]:
        pairs.add((prev_char, char))
        prev_char = char
    return pairs


def clean(text):
    text = text.replace("—", "-")
    text = text.replace("–", "-")
    text = text.replace("―", "-")
    text = text.replace("…", "...")
    text = text.replace("´", "'")
    text = text.replace(".", "")
    text = re.sub(
        r"""(-+|~+|!+|"+|;+|\?+|\++|,+|\)+|\(+|\\+|\/+|\*+|\[+|\]+|}+|{+|\|+|_+)""",
        r" \1 ",
        text,
    )
    text = re.sub(r"\s*\n\s*", " \n ", text)
    text = re.sub(r"[^\S\n]+", " ", text)
    return text.strip()


def is_bool(v):
    if str(v) == "False":
        return "F"
    elif str(v) == "True":
        return "T"
    return v


def initialize_progress_bar(data_loader_list):
    num_examples = sum([len(tensor) for tensor in data_loader_list.values()])
    return set_progress_bar(num_examples)


def set_progress_bar(num_examples):
    bar = tqdm(total=num_examples)
    bar.update(0)
    return bar


def merge_list_of_dicts(L):
    result = {}
    for d in L:
        result.update(d)
    return result


def return_iterator_by_type(data_type):
    if isinstance(data_type, dict):
        iterator = data_type.items()
    else:
        iterator = enumerate(data_type)
    return iterator


@contextlib.contextmanager
def temp_seed(seed):
    state = np.random.get_state()
    np.random.seed(seed)
    try:
        yield
    finally:
        np.random.set_state(state)


def flatten(outer):
    return [el for inner in outer for el in inner]


def zipped_flatten(outer):
    return [(key, fill, el) for key, fill, inner in outer for el in inner]


def remove_none(l):
    return [e for e in l if e is not None]


def download_for_light(base_dpath, df):
    """
    Takes a DownloadableFile, extracts the basename, and downloads
    to the light datapath
    """
    target_dir = os.path.dirname(os.path.join(base_dpath, df.file_name))
    file_name = os.path.basename(df.file_name)
    df.file_name = file_name
    build_data.make_dir(target_dir)
    df.download_file(target_dir)
