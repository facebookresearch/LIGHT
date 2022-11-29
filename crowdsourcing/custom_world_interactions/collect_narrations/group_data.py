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

# TARGET_FILE_BASE = "results"
# REJECTS_FILE_BASE = "results-soft-reject"
TARGET_FILE_BASE = "no-op-actions"
REJECTS_FILE_BASE = "results"


TARGET_FILE = os.path.join(os.path.dirname(__file__), "out_data", f"{TARGET_FILE_BASE}.json")
BACKUP_FILE = TARGET_FILE + ".bak"

SOFT_REJECTS = os.path.join(os.path.dirname(__file__), "out_data", f"{REJECTS_FILE_BASE}.json")
BACKUP_SOFT_REJECTS_FILE = SOFT_REJECTS + ".bak"

def main():
    if os.path.exists(BACKUP_FILE):
        print("Backup file still exists, perhaps something went wrong last run? Check and remove before continuing")
        return
    results = {}
    if os.path.exists(TARGET_FILE):
        shutil.copyfile(TARGET_FILE, BACKUP_FILE)
        with open(TARGET_FILE, 'r') as target_file:
            results = json.load(target_file)
    soft_rejects = {}
    if os.path.exists(SOFT_REJECTS):
        shutil.copyfile(SOFT_REJECTS, BACKUP_SOFT_REJECTS_FILE)
        with open(SOFT_REJECTS, 'r') as target_file:
            soft_rejects = json.load(target_file)

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
    soft_rejected = []
    if len(input("Enter anything to also check soft-rejects").strip()) > 0:
        soft_rejected = [a for a in agents if a.get_status() == AgentState.STATUS_SOFT_REJECTED]

    print("Approved agents in this batch: ", len(approved_agents))
    skipped = 0
    for a in approved_agents:
        if a.db_id in results:
            skipped += 1
            continue # already did this one
        data = a.state.get_data()
        inputs = data["inputs"]
        outputs = data["outputs"]
        primary = outputs["primaryObject"]
        primary_desc = outputs["primaryDescription"]
        secondary = outputs["secondaryObject"]
        secondary_object_map = {
            i["name"]: i["desc"] for i in inputs["secondary_object_list"]
        }
        secondary_desc = secondary_object_map[secondary]
        raw_action = outputs.get('rawAction')
        action_desc = outputs['actionDescription']
        results[a.db_id] = {
            'id': a.db_id,
            'primary': primary,
            'primary_desc': primary_desc,
            'secondary': secondary,
            'secondary_desc': secondary_desc,
            'raw_action': raw_action,
            'action_desc': action_desc,
            'review_status': None,
            'external_perspective': None,
            'objects_afterwards': None,
            'descriptions_afterwards': None,
            'locations_afterwards': None,
            'object_attributes': {'before': None, 'after': None},
            'edit_data': None,
        }
    print(f"{skipped} already loaded agents skipped")

    for a in soft_rejected:
        if a.db_id in results:
            skipped += 1
            continue # already did this one
        data = a.state.get_data()
        inputs = data["inputs"]
        outputs = data["outputs"]
        primary = outputs["primaryObject"]
        primary_desc = outputs["primaryDescription"]
        secondary = outputs["secondaryObject"]
        secondary_object_map = {
            i["name"]: i["desc"] for i in inputs["secondary_object_list"]
        }
        secondary_desc = secondary_object_map[secondary]
        raw_action = outputs.get('rawAction')
        action_desc = outputs['actionDescription']
        soft_rejects[a.db_id] = {
            'id': a.db_id,
            'primary': primary,
            'primary_desc': primary_desc,
            'secondary': secondary,
            'secondary_desc': secondary_desc,
            'raw_action': raw_action,
            'action_desc': action_desc,
            'review_status': None,
            'external_perspective': None,
            'objects_afterwards': None,
            'descriptions_afterwards': None,
            'locations_afterwards': None,
            'object_attributes': {'before': None, 'after': None},
            'edit_data': None,
        }

    # Write out results
    with open(TARGET_FILE, "w+") as target_file:
        json.dump(results, target_file, indent=2)

    # Write out results
    if (len(soft_rejects) > 0):
        with open(SOFT_REJECTS, "w+") as target_file:
            json.dump(soft_rejects, target_file, indent=2)
        if os.path.exists(BACKUP_SOFT_REJECTS_FILE):
            os.remove(BACKUP_SOFT_REJECTS_FILE)

    # Before we clear backup, ensure we didn't accidentally delete data
    assert len(results) >= current_results_len
    assert len(json.dumps(results)) >= current_results_len_json
    print("Collected narrations: ", len(results))
    if os.path.exists(BACKUP_FILE):
        os.remove(BACKUP_FILE)

if __name__ == '__main__':
    main()