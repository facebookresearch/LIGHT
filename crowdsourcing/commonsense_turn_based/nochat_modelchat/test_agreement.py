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

# task_names = ["commonsense_nomodel_chat_allowlist_test_grouped_2"]
# task_names = ["commonsense_nomodel_chat_allowlist_test_grouped_new_training"]
task_names = ["commonsense_nomodel_chat_allowlist_test_grouped_new_training_2"]

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
worker_to_model_to_ratings = {}
for unit in units:
    worker = unit.get_assigned_agent().get_worker()
    worker_name = worker.worker_name
    if worker_name not in worker_to_model_to_ratings:
        worker_to_model_to_ratings[worker_name] = {}
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
    input_response = input_text + "RESP:" + response
    try:
        ratings = [submission_data['checkboxValues']['3'].get(k, None) for k in r_keys]
    except:
        continue
    none_or_disfluent = not any(ratings[:-1])
    if model_file not in worker_to_model_to_ratings[worker_name]:
        worker_to_model_to_ratings[worker_name][model_file] = {}
    worker_to_model_to_ratings[worker_name][model_file][input_response] = [*ratings, none_or_disfluent]

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

workers = list(worker_to_model_to_ratings.keys())
print(f"{len(workers)} workers")

all_rating_data = []

for worker, model_maps in worker_to_model_to_ratings.items():
    for model_file, input_to_ratings in model_maps.items():
        for input_response, rating_data in input_to_ratings.items():
            all_rating_data.append([worker, model_file, input_response, *rating_data])

rating_df = pd.DataFrame(data=all_rating_data, columns=["worker", "model", "input", *r_keys, "none_or_disfluent"])

print(rating_df)

for v, c in Counter(rating_df['input']).items():
    print(v.split("RESP:")[1], c)



rating_df.to_csv("rating_df.csv", index=False)

# overlapping_inputs = []
# for input_response in worker_to_model_to_ratings[mfs[0]].keys():
#     count = 0
#     for mf in mfs:
#         if input_response in input_to_ratings[mf]:
#             count += 1
#     if count == len(mfs):
#         overlapping_inputs.append(input_response)

# print(f"LEN OVERLAPPING: {len(overlapping_inputs)}")