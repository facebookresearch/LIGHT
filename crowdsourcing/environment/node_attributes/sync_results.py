#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.agent import AgentState
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
import os
import pandas as pd
import numpy as np
import time

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
REMAINING_TASKS_DIRECTORY = os.path.join(TASK_DIRECTORY, 'tasks')

def get_last_update_time():
    with open(os.path.join(REMAINING_TASKS_DIRECTORY, "last_sync.txt"), "r") as sync_file:
        return float(sync_file.read().strip())


def mark_accepted(csv_dfs, unit_data):
    try:
        target_type = unit_data['data']['inputs']["taskType"]
    except:
        target_type = {"objects": "objs", "locations": "rooms", "characters": "chars"}[unit_data['data']['inputs']['itemCategory']]
    target_df = csv_dfs[target_type]
    selections = unit_data['data']['inputs']['selection']
    for s in selections:
        target_df.loc[target_df['id'] == s['id'], ['annotated']] += 1


def mark_rejected(csv_dfs, unit_data):
    try:
        target_type = unit_data['data']['inputs']["taskType"]
    except:
        target_type = {"objects": "objs", "locations": "rooms", "characters": "chars"}[unit_data['data']['inputs']['itemCategory']]
    target_df = csv_dfs[target_type]
    selections = unit_data['data']['inputs']['selection']
    for s in selections:
        target_df.loc[target_df['id'] == s['id'], ['assigned']] -= 1


def main():
    db = LocalMephistoDB()
    mephisto_data_browser = MephistoDataBrowser(db=db)
    last_update = get_last_update_time()
    task_name = "fantasy-entity-attribute-annotation-pilot-1" #input("Enter task name to sync from:\n>> ")
    units = mephisto_data_browser.get_units_for_task_name(task_name)

    # Find the units that haven't gone through to be synced just yet
    units_and_data = [(u, mephisto_data_browser.get_data_from_unit(u)) for u in units]
    unprocessed_units = [d for d in units_and_data if d[1]['data']['times']['task_end'] > last_update]

    unreviewed_units = [d for d in unprocessed_units if d[0].get_status() == AgentState.STATUS_COMPLETED]
    if len(unreviewed_units) != 0:
        print("This script can only be run if there are no tasks that need to be reviewed!")
        return

    if len(unprocessed_units) == 0:
        print("Everything appears to be synced!")
        return

    accepted_units = [d for d in unprocessed_units if d[0].get_status() == AgentState.STATUS_ACCEPTED]
    rejected_units = [d for d in unprocessed_units if d[0].get_status() != AgentState.STATUS_ACCEPTED]
    print(f"Processing {len(accepted_units)} accepted units and {len(rejected_units)} passed or rejected units.")

    csv_names = ['objs', 'chars', 'rooms', 'containers', 'weapons', 'wearable', 'consumable']
    csv_dfs = {name: pd.read_csv(os.path.join(REMAINING_TASKS_DIRECTORY, f"{name}.csv")) for name in csv_names}

    for (u, d) in accepted_units:
        mark_accepted(csv_dfs, d)

    for (u, d) in rejected_units:
        mark_rejected(csv_dfs, d)

    for csv_name, df in csv_dfs.items():
        df.to_csv(os.path.join(REMAINING_TASKS_DIRECTORY, f"{csv_name}.csv"), index=False)
    
    with open(os.path.join(REMAINING_TASKS_DIRECTORY, "last_sync.txt"), "w+") as sync_file:
        sync_file.truncate(0)
        sync_file.write(str(time.time()))

if __name__ == "__main__":
    main()