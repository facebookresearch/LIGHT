#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.examine_utils import run_examine_or_review, print_results
from mephisto.data_model.worker import Worker
from mephisto.operations.logger_core import set_mephisto_log_level
from static_gold_blueprint import (
    BLUEPRINT_TYPE,
    StaticGoldBlueprint,
    StaticGoldBlueprintArgs,
    StaticGoldSharedState,
)
from typing import List, Dict, Any
import random

db = LocalMephistoDB()

PAY = 0.37

def format_worker_for_printing(
    worker: Worker, 
    unit_data: List[Dict[str, Any]], 
    valid_data: List[Dict[str, Any]],
) -> str: 
    validation_results = []
    for idx, d in enumerate(valid_data):
        subresults = [f"{x['safety']} - {x['context']} - {x['sentence']}" for x in d['data']['outputs']['final_data'].values()]
        joined_subresults = "\n".join(subresults)
        duration = d['data']['times']['task_end'] - d['data']['times']['task_start']
        validation_results.append(f"**Validation {idx + 1}** duration: {duration:.2f}\n{joined_subresults}")
    joined_validations = "\n".join(validation_results)
    validation_details = f"Total validations: {len(valid_data)}\n{joined_validations}"

    total_time = 0
    examples = {
        'safe': [],
        'unsafe': [],
        'unsure': [],
        'fantasy': [],
        'reality': [],
        'either': [],
    }
    total_count = 0
    for u_data in unit_data:
        duration = u_data['data']['times']['task_end'] - u_data['data']['times']['task_start']
        total_time += duration
        for sub_u in u_data['data']['outputs']['final_data'].values():
            examples[sub_u['safety']].append(sub_u)
            examples[sub_u['context']].append(sub_u)
            total_count += 1
    
    for key in examples.keys():
        random.shuffle(examples[key])

    if total_count == 0:
        return f"Only did validations:\n{validation_details}"

    count_safe, prop_safe = len(examples['safe']), len(examples['safe']) / total_count
    count_unsafe, prop_unsafe = len(examples['unsafe']), len(examples['unsafe']) / total_count
    count_unsure, prop_unsure = len(examples['unsure']), len(examples['unsure']) / total_count
    count_fantasy, prop_fantasy = len(examples['fantasy']), len(examples['fantasy']) / total_count
    count_reality, prop_reality = len(examples['reality']), len(examples['reality']) / total_count
    count_either, prop_either = len(examples['either']), len(examples['either']) / total_count
    
    total_payout = (len(unit_data) + len(valid_data)) * PAY

    overall_stats = (
        f"Overall Stats - Count: {total_count}\n"
        f"safe-unsafe-unsure : ({count_safe} / {count_unsafe}/ {count_unsure}) - "
        f"({prop_safe:.4f} / {prop_unsafe:.4f} / {prop_unsure:.4f})\n"
        f"fantasy-reality-either : ({count_fantasy} / {count_reality}/ {count_either}) - "
        f"({prop_fantasy:.4f} / {prop_reality:.4f} / {prop_either:.4f})\n"
        f"Average Duration: {total_time / total_count:.4f}\n"
        f"Pay: ${total_payout:.2f}. Hourly: ${total_payout / (total_time / (60 * 60)):0.2f}"
    )

    def show_examples(example_list):
        used_examples = example_list[:3]
        written_examples = [f"{x['safety']} - {x['context']} - {x['sentence']}" for x in used_examples]
        return "\n".join(written_examples)

    display_examples = [
        f"**{key} examples** \n{show_examples(val)}" for key, val in examples.items()
    ]

    all_examples = "\n".join(display_examples)

    return (
        f"{overall_stats}\n{validation_details}\n{all_examples}\n\n"
    )


def format_data_for_printing(data):
    # Custom tasks can define methods for how to display their data in a relevant way
    worker_name = Worker(db, data["worker_id"]).worker_name
    contents = data["data"]
    return f"{contents}"
    print(contents)
    raise AssertionError("OOPS")
    duration = contents["times"]["task_end"] - contents["times"]["task_start"]
    metadata_string = (
        f"Worker: {worker_name}\nUnit: {data['unit_id']}\n"
        f"Duration: {int(duration)}\nStatus: {data['status']}\n"
    )

    inputs_string = ""
    outputs_string = ""

    if contents["inputs"] is not None and contents["outputs"] is not None:
        inputs = contents["inputs"]
        inputs_string = f"Input:\n\tPrimary Object List: {inputs['primary_object_list']}\n\tSecondary Object List: {inputs['secondary_object_list']}\n\n"

        outputs = contents["outputs"]["final_data"]
        outputs_string = f"Output:\n\tUse {outputs['primaryObject']} with {outputs['secondaryObject']}\n\tAction: {outputs['actionDescription']}\n"

    return f"-------------------\n{metadata_string}{inputs_string}{outputs_string}"


def main():
    db = LocalMephistoDB()
    set_mephisto_log_level(level='WARNING')
    run_examine_or_review(
        db, 
        format_data_for_printing=format_data_for_printing, 
        format_worker_for_printing=format_worker_for_printing,
    )


if __name__ == '__main__':
    main()
