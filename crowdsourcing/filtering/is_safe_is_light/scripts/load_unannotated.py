#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
This script takes in newline separated entries to annotate, and outputs
to the annotation directory a target file of lines to annotate.

It also checks against the existing targets directory to ensure
that no duplicates are created.
"""


import os
from dataclasses import dataclass, field
import hydra
import pandas as pd
import numpy as np
from omegaconf import DictConfig, MISSING
from hydra.core.config_store import ConfigStoreWithProvider
from typing import List, Optional, Any, Set

TASK_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_FOLDER = os.path.join(TASK_DIRECTORY, "data", "targets")


@dataclass
class LoadScriptConfig:
    source_path: str = MISSING
    target_filename: str = MISSING
    target_directory: str = TARGET_FOLDER


config = ConfigStoreWithProvider("LIGHT")
config.store(name="scriptconfig", node=LoadScriptConfig)


def get_existing_targets(target_directory: str) -> List[str]:
    """
    Return a list of target paths from the given directory
    (full paths to all .csv in the given directory)
    """
    pos_names = os.listdir(target_directory)
    return [os.path.join(target_directory, n) for n in pos_names if n.endswith(".csv")]


def remove_overlap(target_path: str, new_contents: Set[str]) -> Set[str]:
    """
    Load data at the target filename, and remove overlap from
    the new contents
    """
    existing = pd.read_csv(target_path)

    vals = set(existing["text"].values)
    new_contents.difference_update(vals)
    return new_contents


def build_target_file(target_path: str, new_contents: Set[str]):
    """
    Write out the given new contents to a new file at the given
    target path
    """
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    rows = [
        {
            "text": c,
            "annotations": 0,
            "launched": 0,
            "is_safe": 0,
            "is_light": 0,
            "pred_safe": 0,
            "pred_light": 0,
        }
        for c in new_contents
    ]
    if len(rows) == 0:
        print("No unique lines to write, skipping")
        return
    df = pd.DataFrame(rows)
    df.to_csv(f"{target_path}.csv", index=False)


@hydra.main(config_path="../hydra_configs", config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    source_path = os.path.join(TASK_DIRECTORY, cfg.source_path)
    target_filename = cfg.target_filename
    target_directory = cfg.target_directory
    target_path = os.path.join(target_directory, target_filename)

    assert not os.path.exists(
        target_path
    ), f"Cannot write to existing filepath {target_path}"

    with open(source_path, "r") as source_fd:
        new_lines = source_fd.readlines()

    stripped_lines = [l.strip() for l in new_lines]
    stripped_set = set(l for l in stripped_lines if len(l) > 0)

    for other_target in get_existing_targets(target_directory):
        stripped_set = remove_overlap(other_target, stripped_set)

    build_target_file(target_path, stripped_set)


if __name__ == "__main__":
    main()
