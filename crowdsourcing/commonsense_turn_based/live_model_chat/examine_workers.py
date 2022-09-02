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

# task_names = ["model_chat"]
# task_names = ["commonsense_model_chat_pilot"]
# task_names = ["commonsense_model_chat_pilot_2"]
# task_names = ["commonsense_model_chat_pilot_3"]
# task_names = ["commonsense_model_chat_bart_grounded_1"]
# task_names = ["commonsense_model_chat_bart_nongrounded_3"]
# task_names = ["commonsense_model_chat_bart_grounded_3"]
# task_names = ["commonsense_model_chat_bart_nongrounded_1"]

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
unit = units[0]
message_data = []
model_files = []
model_file_to_data = {}
r_keys = ['inconsistent_setting', 'inconsistent_action', 'disfluent', 'none_all_good']
for unit in units:
    data = mephisto_data_browser.get_data_from_unit(unit)

    # model_file = data['data']['save_data']['custom_data']['task_description']['model_file']
    if data['data']['save_data'] is None:
        model_file = "UNKNOWN"
    else:
        model_file = data['data']['save_data']['custom_data']['task_description']['model_file']
    model_files.append(model_file)
    submission_data = data['data']['final_submission']['all_ratings']
    # print(data['data'])
    # print(data)
    # eval_label = data['data']['initial_data']['eval_labels'][0]
    # print(submission_data.keys())
    # print(submission_data)
    action = submission_data['messages']['2'][1]
    response = submission_data['messages']['3'][1]
    
    if '3' not in submission_data['checkboxValues']:
        continue

    ratings = [submission_data['checkboxValues']['3'].get(k, None) for k in r_keys]
    error_text = submission_data['textFieldValues'].get('3', {}).get('why_error', None)
    better_narration = submission_data['textFieldValues'].get('3', {}).get('better_narration', None)

    none_or_disfluent = not any(ratings[:-1])
    # print(submission_data)
    message_data.append([action, response, *ratings, none_or_disfluent, error_text, better_narration])
    if model_file not in model_file_to_data:
        model_file_to_data[model_file] = []
    model_file_to_data[model_file].append(message_data[-1])

for model_file, message_data in model_file_to_data.items():
    print("-"*100)
    print(f"MODEL FILE: {model_file}")
    df = pd.DataFrame(message_data, columns=["action", "response", *r_keys, "none_or_disfluent", "error_text", "better_narration"])

    # print(df)

    # for c in ['action', 'response', 'error_text', 'better_narration']:
    #     df[c] = df[c].str.wrap(30)
    print(df)
    # for i, row in df[df["disfluent"] == True].iterrows():
    for i, row in df.iterrows():
        print(row['action'])
        print(row['response'])
        print(row[r_keys])
        print("-"*100)
    model_name = model_file.split("/")[-2]
    df.to_csv(f"./{model_name}.csv", index=False)
    # print(data)
    # print()
    # print(data.keys())

    # for i, row in df.iterrows():
    #     print("-"*100)
    #     print(f"Action: {row['action']}")
    #     print(f"Response: {row['response']}")
    #     print("why error: ", row['error_text'])
    #     print("better: ", row['better_narration'])
    #     print([r_keys[i] for i, k in enumerate(r_keys) if row[k]])

    print(f"Means from {len(df)} results")
    print(df[[*r_keys, "none_or_disfluent"]].mean())

    print(f"Extra note: model files for tasks: {task_names}")
    print(Counter(model_files))