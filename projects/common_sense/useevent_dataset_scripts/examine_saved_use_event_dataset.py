#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#################################################################
# This script generates some statistics about the use-events
# dataset. NOTE: This is *not* the script to examine raw 
# mephisto task data and to accept/reject data points. 
# Those scripts (per annotation task) can be found in the relevant 
# crowdsourcing directories.
#################################################################

import pickle
import pandas as pd
import random

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

def get_data_for_task_names(task_names):
    # get mephisto data for each task
    units = []
    for t in task_names:
        new_units = mephisto_data_browser.get_units_for_task_name(t)
        units.extend(new_units)
    return units

def get_count_stats_from_units(units):
    # Inputs should be mephisto units from get_data_for_task_names
    # Returns column-value table of relevant stats, expand as needed
    data = []

    num_units = len(units)
    data.append(["# Total", num_units])
    
    accepted_units = [u for u in units if u.get_status() == "accepted"]
    num_accepted = len(accepted_units)
    data.append(["# Accepted", num_accepted])

    # only count workers who contributed to the accepted dataset
    workers = [unit.get_assigned_agent().get_worker() for unit in accepted_units]
    worker_names = set([worker.worker_name for worker in workers])

    data.append(["# Unique Workers", len(worker_names)])

    df = pd.DataFrame(data=data, columns=["Name", "Value"])
    return df


############################
# Collect Narrations
############################

print("-"*100)
print("Collect Narrations")
print("-"*100)

# mephisto tasks for ground constraints task
task_names = ["objects-interaction-task-allowlist-collection-2"]

event_data = get_data_for_task_names(task_names)
print(get_count_stats_from_units(event_data))

############################
# Ground Events
############################

print("-"*100)
print("Ground Events")
print("-"*100)

# mephisto tasks for ground constraints task
task_names = ["objects-interaction-task-allowlist-events-1"]

event_data = get_data_for_task_names(task_names)
print(get_count_stats_from_units(event_data))

############################
# Ground Attributes
############################

print("-"*100)
print("Ground Attributes")
print("-"*100)

# mephisto tasks for ground constraints task
task_names = ["objects-interaction-task-allowlist-attributes-1"]

attribute_data = get_data_for_task_names(task_names)
print(get_count_stats_from_units(attribute_data))

############################
# Ground Constraints
############################

print("-"*100)
print("Ground Constraints")
print("-"*100)

# mephisto tasks for ground constraints task
task_names = ["objects-interaction-task-allowlist-constraints-3"]

constraint_data = get_data_for_task_names(task_names)
print(get_count_stats_from_units(constraint_data))

############################
# Final Dataset
############################

print("-"*100)
print("FINAL DATASET")
print("-"*100)

# get finalized dataset
save_fname = "/checkpoint/light/common_sense/use_event_data"
with open(save_fname, 'rb') as f:
    BY_SPLIT_USE_EVENT_DATA = pickle.load(f)

count_data = []
total = 0
for split, use_events in BY_SPLIT_USE_EVENT_DATA.items():
    cur_len = len(use_events)
    count_data.append([split, cur_len])
    total += cur_len

    random_use_event = random.choice(use_events)
    misc_use_action_data = random_use_event['misc_use_action_data']
    print("-"*20)
    print(f"Example from split: {split}")
    object1 = misc_use_action_data["object1"]
    object2 = misc_use_action_data["object2"]
    raw_action = misc_use_action_data["raw_action"]
    narration = misc_use_action_data["narration"]
    print(f"Use {object1} with {object2}")
    print(f"Action: {raw_action}")
    print(f"Narration: {narration}")
count_data.append(["Total", total])

count_df = pd.DataFrame(data=count_data, columns=["Split", "#"])
print(count_df)
