#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
This script reads in the results from a task, as checked from the
targets file, and converts a portion of them into golds.

Allows randomly sampling some set, or direct selection via key entry
"""

import os
from dataclasses import dataclass, field
import hydra
import pandas as pd
import numpy as np
import time
import json
import csv
from collections import defaultdict
from datetime import datetime
from omegaconf import DictConfig, MISSING
from hydra.core.config_store import ConfigStoreWithProvider
from typing import List, Dict, Optional, Any, Set, Tuple
from mephisto.abstractions.databases.local_singleton_database import MephistoSingletonDB
from mephisto.tools.data_browser import DataBrowser
from static_gold_blueprint import BLUEPRINT_TYPE

# TASK_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
TARGET_FOLDER = os.path.join(TASK_DIRECTORY, "data", "targets")
LAST_LOAD_TIMES = os.path.join(TASK_DIRECTORY, "data", 'last_loads.json')

# Label values
IS_LIGHT = 1
IS_SAFE = 1
UNSAFE = 0
REALITY = 0
EITHER = 0.5
UNSURE = 0.25
LABEL_MAPPING = {
    'safe': IS_SAFE,
    'unsafe': UNSAFE,
    'unsure': UNSURE,
    'fantasy': IS_LIGHT,
    'reality': REALITY,
    'either': EITHER,
}

# Typing
Decision = Tuple[str, str]   # ('safe', 'fantasy')
Outcome = Tuple[int, int, float, float]  # [units processed, annotations completed, is_safe, is_light]


SQLITE_TIME_FORMAT='%Y-%m-%d %H:%M:%S'

@dataclass
class LoadScriptConfig:
    task_name: str = MISSING
    gold_filename: str = MISSING


config = ConfigStoreWithProvider("LIGHT")
config.store(name="scriptconfig", node=LoadScriptConfig)


def get_existing_targets(target_directory: str) -> List[str]:
    """
    Return a list of target paths from the given directory
    (full paths to all .csv in the given directory)
    """
    pos_names = os.listdir(target_directory)
    return [os.path.join(target_directory, n) for n in pos_names if n.endswith(".csv") and n != 'light_test.csv']


def as_timestamp(sqlite_timestring: str) -> float:
    return datetime.strptime(sqlite_timestring, SQLITE_TIME_FORMAT).timestamp()


def add_texts_for_unit(text_to_unit: Dict[str, List["Unit"]], unit: "Unit"):
    try:
        data = unit.get_assignment_data().shared
    except AssertionError as e:
        print(f"Could not find data for {unit}, skipping...")
        return
    texts = data['texts']
    for text_obj in data['texts']:
        text = text_obj['text']
        if text not in text_to_unit:
            text_to_unit[text] = []
        text_to_unit[text].append(unit)


def get_text_to_outcome_map(unit: "Unit"):
    """returns a map from the text utterance to the annotation for a given unit"""
    try:
        data = unit.get_assigned_agent().state.get_data()
        subresults = data['outputs']['final_data'].values()
    except Exception as e:
        print(f"Could not find data for {unit} due to {e}, skipping...")
        return {}
    return {
        x['sentence']: (x['safety'], x['context']) for x in subresults
    }


def construct_outcome_map(
    text_to_unit: Dict[str, List["Unit"]], 
    relaunchable_units: Set[str], 
    accepted_units: Dict[str, Dict[str, Decision]]
) -> Dict[str, Outcome]:
    """
    Creates a mapping from the input text string to the outcome: ints for
    the number addressed, the number successfully annotated, and the annotation values.
    """
    outcome_map = {}
    for addressed_text, units in text_to_unit.items():
        num_addressed = 0
        annotation_count = 0
        is_safe_value = 0
        is_light_value = 0
        for unit in units:
            db_id = unit.db_id
            if db_id in relaunchable_units:
                num_addressed += 1
            elif db_id in accepted_units:
                num_addressed += 1
                if addressed_text not in accepted_units[db_id]:
                    print(f"Data access issue on unit {db_id} for key {addressed_text}, skipping")
                else:
                    safe_label, light_label = accepted_units[db_id][addressed_text]
                    is_safe_value += LABEL_MAPPING[safe_label]
                    is_light_value += LABEL_MAPPING[light_label]
                    annotation_count += 1
        outcome_map[addressed_text] = (num_addressed, annotation_count, is_safe_value, is_light_value)
    return outcome_map


def apply_outcomes(
    outcome_map: Dict[str, Outcome],
):
    """
    Traverse the targets folders, finding applicable lines and applying outcomes
    """
    target_files = get_existing_targets(TARGET_FOLDER)
    for target_file in target_files:
        df = pd.read_csv(target_file)
        df_dict_list = df.to_dict("records")
        for curr_idx, entry in enumerate(df_dict_list):
            if not entry["launched"]:
                continue # No outstanding launched values to check
            text = entry['text']
            if text not in outcome_map:
                continue # No entry for this annotation
            num_addressed, num_annotated, is_safe, is_light = outcome_map[text]
            df.at[curr_idx, "launched"] = df.at[curr_idx, "launched"] - num_addressed
            df.at[curr_idx, "annotations"] = df.at[curr_idx, "annotations"] + num_annotated
            df.at[curr_idx, "is_safe"] = df.at[curr_idx, "is_safe"] + is_safe
            df.at[curr_idx, "is_light"] = df.at[curr_idx, "is_light"] + is_light
        
        df.to_csv(target_file, index=False)

def get_grouped_examples(
    accepted_units: Dict[str, Dict[str, Decision]]
) -> Dict[Tuple[str, str], List[str]]:
    """
    Iterate through the accepted units, and create a list of text by decision
    """
    grouped_examples = defaultdict(lambda: [])
    for unit in accepted_units.values():
        for text, decision in unit.items():
            grouped_examples[decision].append(text)
    return grouped_examples


def parse_good_examples(
    grouped_examples: Dict[Tuple[str, str], List[str]]
) -> List[Tuple[str, int, int]]:
    """
    Given the grouped examples, allow directly approving or rejecting 
    gold examples
    """
    val_map = {
        'safe': 1,
        'unsafe': 0,
        'fantasy': 1,
        'either': 1,
        'reality': 0,
    }
    safe_light_gold_labels = [('safe', 'fantasy'), ('safe', 'either')]
    added_examples = []
    for (is_safe, is_light), examples in grouped_examples.items():
        print(f"Found {len(examples)} of {(is_safe, is_light)}")
        if is_safe == 'unsure':
            continue
        if (is_safe, is_light) in safe_light_gold_labels:
            continue # We can add more of these golds at the end
        for example in examples:
            retain = input(f"{is_safe} - {is_light}: {example}\nRetain: (y/n): ")
            if retain == 'y':
                added_examples.append((example, val_map[is_safe], val_map[is_light]))
            if retain == 'D':
                break

    non_safe_light_count = len(added_examples)
    target_golds = non_safe_light_count * 1.3
    for example in grouped_examples[('safe', 'fantasy')]:
        retain = input(f"safe - fantasy: {example}\nRetain: (y/n): ")
        if retain == 'y':
            added_examples.append((example, val_map['safe'], val_map['fantasy']))
        if retain == 'D':
            break
        if len(added_examples) > target_golds:
            break

    return added_examples


@hydra.main(config_path="./hydra_configs", config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    task_name = cfg.task_name
    gold_filename = cfg.gold_filename

    db = MephistoSingletonDB()
    task_id = db.find_tasks(task_name=task_name)[0].db_id

    units = db.find_units(task_id=task_id)

    # Check against a last reviewed time
    if not os.path.exists(LAST_LOAD_TIMES):
        last_load_dict = {}
    else:
        with open(LAST_LOAD_TIMES, 'r') as last_loads:
            last_load_dict = json.load(last_loads)
    last_review_time = last_load_dict.get(task_name, 0.0)

    # Construct a text -> outcome map for everything not yet reviewed
    new_units = [u for u in units if as_timestamp(u.get_task_run().start_time) > last_review_time]
    new_units = [u for u in new_units if u.unit_index >= 0]

    # Find task runs without created units
    task_runs = {}
    run_times = {}
    for u in new_units:
        task_run = u.get_task_run()
        run_id = u.get_task_run().db_id
        if run_id not in task_runs:
            task_runs[run_id] = True # Mark as a valid task run
            run_times[run_id] = as_timestamp(task_run.start_time)
        if not task_runs[run_id]:
            continue # Already decided these units aren't valid
        if u.get_status() in ['created', 'completed']:
            task_runs[run_id] = False  # This run is ongoing or not fully judged!

    actionable_units = [u for u in new_units if task_runs[u.get_task_run().db_id]]
    for key, start_time in run_times.items():
        if task_runs[key] and start_time > last_review_time:
            last_review_time = start_time + 1

    # Construct a text -> outcome map for everything not yet reviewed
    text_to_unit = {}
    for unit in actionable_units:
        add_texts_for_unit(text_to_unit, unit)

    relaunchable_unit_ids = {u.db_id for u in actionable_units if u.get_status() in ['expired', 'rejected', 'soft_rejected']}
    accepted_units = {u.db_id: get_text_to_outcome_map(u) for u in actionable_units if u.get_status() == 'accepted'}

    outcome_map = construct_outcome_map(text_to_unit, relaunchable_unit_ids, accepted_units)

    # Iterate through all of the targets (launched), and update with an outcome.
    apply_outcomes(outcome_map)

    last_load_dict[task_name] = last_review_time
    with open(LAST_LOAD_TIMES, 'w+') as last_loads:
        json.dump(last_load_dict, last_loads)

    # Create a list of new examples to add
    examples_per_group = get_grouped_examples(accepted_units)
    examples = parse_good_examples(examples_per_group)

    with open(os.path.join(TASK_DIRECTORY, 'data', 'golds', gold_filename), 'w+') as gold_file:
        writer = csv.writer(gold_file)
        writer.writerow(['text', 'is_safe', 'is_light'])
        writer.writerows(arr)


if __name__ == "__main__":
    main()
