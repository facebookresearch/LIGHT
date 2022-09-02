#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

###########################################################
# The goal of this script is to pull the use-x-with-y 
# dataset from the provided task names and to save a version
# with splits
###########################################################

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from use_event_utils import get_useful_data_from_use_event
import pickle

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

# mephisto tasks that contain the event data (should be final constraint task)
task_names = ["objects-interaction-task-allowlist-constraints-3"]

# modify this variable to only generate train/test, train/valid/test, etc.
desired_splits = ["train", "valid", "test", "unseen"]
# the breakdown of the splits (e.g. 70/10/10/10)
desired_split_pcts = [0.7, 0.1, 0.1, 0.1]

# where to save resulting dataset
# save_fname = "/private/home/alexgurung/ParlAI/data/light_common_sense/gameplays/use_events.pkl"
save_fname = "/checkpoint/light/common_sense/use_event_data/use_events.pkl"

############################
# get data from mephisto
############################

# get all mephisto units from the tasks
units = []
for t in task_names:
    print(f"Loading data from task [{t}]...")
    new_units = mephisto_data_browser.get_units_for_task_name(t)
    units.extend(new_units)

# only interested in units marked as accepted
accepted_units = [u for u in units if u.get_status() == "accepted"]
# get the data from each accepted unit
event_data = [mephisto_data_browser.get_data_from_unit(unit) for unit in accepted_units]

############################
# setup split indices
############################

split_end_indices = []
cur_index = 0
num_data_points = len(event_data)

# iterate over split pcts, except the last which ends with the dataset
for pct in desired_split_pcts[:-1]:
    block_size = int(pct * num_data_points)
    cur_index += block_size
    split_end_indices.append(cur_index)
# last split gets the rest of the data points
split_end_indices.append(num_data_points)

SPLITS = {}
cur_split = "train"
cur_start = 0
# iterate over splits and ending points
for split, end in zip(desired_splits, split_end_indices):
    print(f"Generating data for {split} split...")
    SPLIT_EVENT_DATA = []
    # iterate over current section and collect data
    for i in range(cur_start, end):
        data = event_data[i]
        data_for_teachers = get_useful_data_from_use_event(data)

        SPLIT_EVENT_DATA.append(data_for_teachers)
    
    cur_start = end
    SPLITS[split] = SPLIT_EVENT_DATA

# dumps data to given folder
with open(save_fname, 'wb') as f:
    pickle.dump(SPLITS, f)

print(f"Saved to {save_fname}")

