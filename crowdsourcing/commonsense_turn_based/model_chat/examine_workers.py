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
task_names = ["commonsense_model_chat_pilot_3"]

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
r_keys = ['inconsistent_setting', 'inconsistent_action', 'disfluent', 'none_all_good']
for unit in units:
    data = mephisto_data_browser.get_data_from_unit(unit)
    submission_data = data['data']['final_submission']['all_ratings']
    # print(submission_data.keys())
    action = submission_data['messages']['2'][1]
    response = submission_data['messages']['3'][1]
    ratings = [submission_data['checkboxValues']['3'].get(k, None) for k in r_keys]
    error_text = submission_data['textFieldValues'].get('3', {}).get('why_error', None)
    better_narration = submission_data['textFieldValues'].get('3', {}).get('better_narration', None)

    # print(submission_data)
    message_data.append([action, response, *ratings, error_text, better_narration])

df = pd.DataFrame(message_data, columns=["action", "response", *r_keys, "error_text", "better_narration"])

# print(df)

# for c in ['action', 'response', 'error_text', 'better_narration']:
#     df[c] = df[c].str.wrap(30)
print(df)
# print(data)
# print()
# print(data.keys())

for i, row in df.iterrows():
    print("-"*100)
    print(row['action'])
    print(row['response'])
    print("why error: ", row['error_text'])
    print("better: ", row['better_narration'])
    print([r_keys[i] for i, k in enumerate(r_keys) if row[k]])
