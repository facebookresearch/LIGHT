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
from dataclasses import dataclass, field
import hydra
from omegaconf import DictConfig, MISSING
from hydra.core.config_store import ConfigStoreWithProvider

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
TARGET_FOLDER = os.path.join(TASK_DIRECTORY, "data", "targets")


@dataclass
class ScoreScriptConfig:
    is_light_model_path: str = MISSING
    is_safe_model_path: str = MISSING
    target_directory: str = TARGET_FOLDER


config = ConfigStoreWithProvider("LIGHT")
config.store(name="scriptconfig", node=ScoreScriptConfig)


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
