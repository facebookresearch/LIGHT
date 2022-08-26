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
# task_names = ["commonsense_model_chat_bart_nongrounded_1"]
# task_names = ["commonsense_model_chat_bart_grounded_forceinvalid_1"]
# task_names = ["commonsense_model_chat_bart_grounded_forceinvalid_2"]
# task_names = ["commonsense_model_chat_bart_nongrounded_forceinvalid_2"]
# task_names = ["commonsense_model_chat_bart_grounded_forceinvalid_2"]
# task_names = ["commonsense_model_chat_bart_nogrounded_forceinvalid_2"]
# task_names = ["commonsense_model_chat_bart_nogrounded_forceinvalid_3"]
# task_names = ["commonsense_model_chat_bart_grounded_forceinvalid_3"]

# task_names = ["commonsense_model_chat_bart_test"]
# task_names = ["commonsense_nomodel_chat_allowlist_final", "commonsense_nomodel_chat_allowlist_final_grounded"]
task_names = ["commonsense_nomodel_chat_allowlist_test_grouped"]

units = []
for t in task_names:
    new_units = mephisto_data_browser.get_units_for_task_name(t)
    print(t)
    print(Counter([u.get_status() for u in new_units]))
    # units.extend(new_units)
    for unit in new_units:
        if "grounded" not in t:
            data = mephisto_data_browser.get_data_from_unit(unit)
            if data['data']['save_data'] is None:
                model_file = "idk"
            else:
                model_file = data['data']['save_data']['custom_data']['task_description']['model_file']
            if "6c8" in model_file:
                continue
            units.append(unit)
        else:
            units.append(unit)

print(f"prev len: {len(units)}")
print(Counter([u.get_status() for u in units]))

print(units[0])
unit = units[0]
model_file_to_data = {}
message_data = []
model_files = []
r_keys = ['inconsistent_setting', 'inconsistent_action', 'disfluent', 'none_all_good']
input_to_ratings = {}
for unit in units:
    data = mephisto_data_browser.get_data_from_unit(unit)

    if data['data']['save_data'] is None:
        model_file = "idk"
    else:
        model_file = data['data']['save_data']['custom_data']['task_description']['model_file']
    model_files.append(model_file)
    submission_data = data['data']['final_submission']['all_ratings']
    # print(submission_data.keys())
    action = data['data']['initial_data']['action']
    # response = submission_data['messages']['3'][1]
    response = data['data']['initial_data']['response_text']
    eval_label = data['data']['initial_data']['eval_labels'][0]
    
    input_text = data['data']['initial_data']['game_text_dropoutless']
    input_response = input_text + response

    ratings = [submission_data['checkboxValues']['3'].get(k, None) for k in r_keys]
    none_or_disfluent = not any(ratings[:-1])
    if model_file not in input_to_ratings:
        input_to_ratings[model_file] = {}
    input_to_ratings[model_file][input_response] = [*ratings, none_or_disfluent]
    error_text = submission_data['textFieldValues'].get('3', {}).get('why_error', None)
    better_narration = submission_data['textFieldValues'].get('3', {}).get('better_narration', None)

    # print(submission_data)
    message_data.append([input_response, action, response, *ratings, none_or_disfluent, error_text, better_narration, eval_label])
    if model_file not in model_file_to_data:
        model_file_to_data[model_file] = []
    model_file_to_data[model_file].append(message_data[-1])

for model_file, message_data in model_file_to_data.items():
    print("-"*100)
    print(f"NON FIXED MODEL FILE: {model_file}")
    df = pd.DataFrame([m[1:] for m in message_data], columns=["action", "response", *r_keys, "none_or_disfluent", "error_text", "better_narration", "eval_label"])
    print(df)
    model_name = model_file.split("/")[-2]
    df.to_csv(f"./{model_name}.csv", index=False)
    print(f"Means from {len(df)} results")
    print(df[[*r_keys, "none_or_disfluent"]].mean())

    print(f"Extra note: model files for tasks: {task_names}")
    print(Counter(model_files))

print("EXPLORING RELATED RATINGS")

mfs = list(input_to_ratings.keys())
overlapping_inputs = []
for input_response in input_to_ratings[mfs[0]].keys():
    count = 0
    for mf in mfs:
        if input_response in input_to_ratings[mf]:
            count += 1
    if count == len(mfs):
        overlapping_inputs.append(input_response)

print(f"LEN OVERLAPPING: {len(overlapping_inputs)}")


no_match = []
input_to_fixed_ratings = {}
for input_response in overlapping_inputs:
    match = True
    initial_rating = input_to_ratings[mfs[0]][input_response]
    for mf in mfs:
        this_rating = input_to_ratings[mf][input_response]
        if not all(this_rating[i] == initial_rating[i] for i in range(len(initial_rating))):
            match = False
            # print("-"*100)
            nicemf = mfs[0].split("/")[-2]
            # print(f"{nicemf}: {initial_rating}")
            # print("vs")
            nicemf = mf.split("/")[-2]
            # print(f"{nicemf}: {this_rating}")
            break
    if not match:
        fixed_rating = initial_rating
        all_ratings = [input_to_ratings[mf][input_response] for mf in mfs]
        # iterate over raw annotations, don't include none or none just disfluent
        for i in range(len(fixed_rating) - 2):
            fixed_rating[i] = any(rating[i] for rating in all_ratings)
        # none_all_good is everything up to it
        fixed_rating[-2] = all(not r for r in fixed_rating[:-2])
        # none or disfluent is everything up to before disfluent
        fixed_rating[-1] = all(not r for r in fixed_rating[:-3])
        input_to_fixed_ratings[input_response] = fixed_rating
        # no_match.append(input_response)
        

print(f"LEN OVERLAP AND DONT MATCH: {len(input_to_fixed_ratings)}")

for model_file, message_data in model_file_to_data.items():
    fixed_message_data = []
    for message_row in message_data:
        input_response = message_row[0]
        ratings = message_row[3:8]
        if input_response in input_to_fixed_ratings:
            ratings = input_to_fixed_ratings[input_response]
        fixed_message_data.append(message_row[1:])
        for i in range(3, 8):
            fixed_message_data[-1][i] = ratings[i-3]

    print("-"*100)
    print(f"MODEL FILE: {model_file}")
    # df = pd.DataFrame(message_data, columns=["action", "response", *r_keys, "error_text", "better_narration"])
    df = pd.DataFrame(fixed_message_data, columns=["action", "response", *r_keys, "none_or_disfluent", "error_text", "better_narration", "eval_label"])

    for i, row in df[df['disfluent'] == True].iterrows():
        print(row['action'])
        print(row['response'])
        print(f"true: {row['eval_label']}")
        print("better", row['better_narration'])
        print("error", row['error_text'])
        print(row[r_keys])
        print("-"*100)

    # print(df)

    # for c in ['action', 'response', 'error_text', 'better_narration']:
    #     df[c] = df[c].str.wrap(30)
    print(df)
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