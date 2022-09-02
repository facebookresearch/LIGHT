#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.data_model.worker import Worker
from mephisto.data_model.unit import Unit
from collections import Counter
from model_chat_blueprint import *
import pandas as pd

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

DO_REVIEW = True

world_log_prefix = "/checkpoint/light/common_sense/model_data/bart_compare_largersweep_Sun_Aug_14/world_logs"
output_world_log_path = f"{world_log_prefix}/EXAMPLE_WORLD_LOG.jsonl"

task_names = ["commonsense_model_chat_allowlist_final", "commonsense_model_chat_allowlist_final_grounded"]

units = []
for t in task_names:
    new_units = mephisto_data_browser.get_units_for_task_name(t)
    print(t)
    print(Counter([u.get_status() for u in new_units]))
    units.extend(new_units)

print(f"prev len: {len(units)}")
print(Counter([u.get_status() for u in units]))

print(units[0])
fake_world_log_data = []
for unit in units:
    data = mephisto_data_browser.get_data_from_unit(unit)
    
    # model_file = data['data']['save_data']['custom_data']['task_description']['model_file']
    if data['data']['save_data'] is None:
        model_file = "UNKNOWN"
    else:
        model_file = data['data']['save_data']['custom_data']['task_description']['model_file']

    submission_data = data['data']['final_submission']['all_ratings']
    
    action = submission_data['messages']['2'][1]
    response = submission_data['messages']['3'][1]

    initial_data = data['data']['initial_data']
    game_text_dropoutless = initial_data['game_text_dropoutless']
    fake_world_log_entry = {}

    teacher_dialog = initial_data
    teacher_dialog['id'] = "fake teacher"
    teacher_dialog['action'] = action
    
    dialog = [
        [
            teacher_dialog,
            {"id":"fake response", "text":response}
        ]
    ]

    fake_world_log_entry['dialog'] = dialog
    
    fake_world_log_data.append(fake_world_log_entry)

with open(output_world_log_path, 'w') as outfile:
    for entry in fake_world_log_data:
        json.dump(entry, outfile)
        outfile.write('\n')