#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
This script checks through the targets files for unannotated
values, and scores confidence for how likely they are to be LIGHT
and how likely they are to be safe.
"""


import os
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
import hydra
from omegaconf import DictConfig, MISSING
from hydra.core.config_store import ConfigStoreWithProvider

TASK_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_FOLDER = os.path.join(TASK_DIRECTORY, "data", "targets")

from typing import List, Any


@dataclass
class ScoreScriptConfig:
    # is_light_model_path: str = MISSING
    # is_safe_model_path: str = MISSING
    target_directory: str = TARGET_FOLDER


config = ConfigStoreWithProvider("LIGHT")
config.store(name="scriptconfig", node=ScoreScriptConfig)


def get_existing_targets(target_directory: str) -> List[str]:
    """
    Return a list of target paths from the given directory
    (full paths to all .csv in the given directory)
    """
    pos_names = os.listdir(target_directory)
    return [os.path.join(target_directory, n) for n in pos_names if n.endswith(".csv")]


def score_entries(target_path: str, safety_model: Any, light_model: Any):
    """
    Load data at the target filename, and remove overlap from
    the new contents
    """
    existing = pd.read_csv(target_path)
    existing.loc[existing["annotations"] == 0, ["pred_safe"]] = existing.apply(
        lambda row: get_safety_confidence(safety_model, row["text"]),
        axis=1,
    )
    existing.loc[existing["annotations"] == 0, ["pred_light"]] = existing.apply(
        lambda row: get_light_confidence(light_model, row["text"]),
        axis=1,
    )
    existing.to_csv(target_path, index=False)


# TODO update confidence methods with loading a model
def get_safety_confidence(model, utterance):
    """
    Determine how safe the model thinks the given utterance is
    """
    return 0


def get_light_confidence(model, utterance):
    """
    Determine how light-relevant the model thinks the given utterance is
    """
    return 0


@hydra.main(config_path="../hydra_configs", config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    print("Adding score predictions for all unannotated targets")
    safety_model = None  # cfg.is_safe_model_path
    light_model = None  # cfg.is_light_model_path
    target_directory = cfg.target_directory
    for target in get_existing_targets(target_directory):
        score_entries(target, safety_model, light_model)
    print("Completed!")


if __name__ == "__main__":
    main()
