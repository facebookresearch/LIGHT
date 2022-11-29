#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Collect data from the Mephisto task and input it into the json file,
if it doesn't already exist. Requries that the data is approved.
"""

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.agent import AgentState

import os
import json
import shutil

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
TARGET_FILE = os.path.join(TASK_DIRECTORY, "../collect_narrations/out_data/results.json")
BACKUP_FILE = TARGET_FILE + ".bak"

def main():
    if os.path.exists(BACKUP_FILE):
        print("Backup file still exists, perhaps something went wrong last run? Check and remove before continuing")
        return
    results = {}
    if os.path.exists(TARGET_FILE):
        shutil.copyfile(TARGET_FILE, BACKUP_FILE)
        with open(TARGET_FILE, 'r') as target_file:
            results = json.load(target_file)

    current_results_len = len(results)
    print("Existing narrations: ", current_results_len)
    current_results_len_json = len(json.dumps(results))

    # find entries for the task
    task_name = input("Task name to search for: ")

    db = LocalMephistoDB()
    task = db.find_tasks(task_name=task_name)[0]
    agents = [u.get_assigned_agent() for u in db.find_units(task_id=task.db_id)]
    agents = [a for a in agents if a is not None]
    approved_agents = [a for a in agents if a.get_status() == AgentState.STATUS_APPROVED]

    print("Approved agents in this batch: ", len(approved_agents))
    skipped = 0
    for a in approved_agents:
        data = a.state.get_data()
        inputs = data["inputs"]
        data_id = inputs['id']
        if results[data_id]['edit_data'] is not None:
            skipped += 1
            continue # already did this one
        outputs = data["outputs"]
        results[data_id]['edit_data'] = outputs
    print(f"{skipped} already loaded agents skipped")

    # Write out results
    with open(TARGET_FILE, "w+") as target_file:
        json.dump(results, target_file, indent=2)

    # Before we clear backup, ensure we didn't accidentally delete data
    assert len(results) >= current_results_len
    assert len(json.dumps(results)) >= current_results_len_json
    print("Collected narrations: ", len(results))
    if os.path.exists(BACKUP_FILE):
        os.remove(BACKUP_FILE)

if __name__ == '__main__':
    main()