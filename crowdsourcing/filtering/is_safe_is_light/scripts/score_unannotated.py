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
from tqdm import tqdm
from dataclasses import dataclass, field
import hydra
from omegaconf import DictConfig, MISSING
from hydra.core.config_store import ConfigStoreWithProvider

from parlai.agents.transformer.transformer import TransformerClassifierAgent
from parlai.core.agents import create_agent
from parlai.core.params import ParlaiParser
from parlai_internal.agents.safety_wrapper.multiturn_safety import (
    MultiturnOffensiveLanguageClassifier,
)

TASK_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_FOLDER = os.path.join(TASK_DIRECTORY, "data", "targets")

from typing import List, Dict, Any

tqdm.pandas()

def get_safety_model(safety_model_path: str):
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
                model_file=safety_model_path,
                print_scores=True,
                split_lines=True,
                model_parallel=False,
                bs=1,
            )
            safety_opt = parser.parse_args([])
            return create_agent(safety_opt, requireModelExists=True)
    
    return AdversarialOffensiveLanguageClassifier()


def get_light_model(light_model_path: str):
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
                model_file=light_model_path,
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

    return IsLIGHTClassifier()



@dataclass
class ScoreScriptConfig:
    is_light_model_path: str = '/private/home/jju/models/is_light/is_light_classifier_model'
    is_safe_model_path: str = 'zoo:bot_adversarial_dialogue/multi_turn/model'
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
    Score entries for safety and light-ness with the given models
    """
    existing = pd.read_csv(target_path)
    print(f"Scoring {target_path} entries for safety...")
    existing.loc[existing["annotations"] == 0, ["pred_safe"]] = existing.progress_apply(
        lambda row: get_safety_confidence(safety_model, row["text"]),
        axis=1,
    )
    existing.to_csv(target_path, index=False)
    print(f"Scoring {target_path} entries for light-ness...")
    existing.loc[existing["annotations"] == 0, ["pred_light"]] = existing.progress_apply(
        lambda row: get_light_confidence(light_model, row["text"]),
        axis=1,
    )
    existing.to_csv(target_path, index=False)


# TODO update confidence methods with loading a model
def get_safety_confidence(model, utterance):
    """
    Determine how safe the model thinks the given utterance is
    """
    not_safe, thresh = model.contains_offensive_language(utterance)
    return thresh


def get_light_confidence(model, utterance):
    """
    Determine how light-relevant the model thinks the given utterance is
    """
    is_light, thresh = model.utterance_is_light(utterance)
    return thresh


@hydra.main(config_path="../hydra_configs", config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    print("Adding score predictions for all unannotated targets")
    safety_model = get_safety_model(cfg.is_safe_model_path)
    light_model = get_light_model(cfg.is_light_model_path)
    target_directory = cfg.target_directory
    for target in get_existing_targets(target_directory):
        score_entries(target, safety_model, light_model)
    print("Completed!")


if __name__ == "__main__":
    main()
