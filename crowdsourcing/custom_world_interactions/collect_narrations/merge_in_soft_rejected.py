#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Collect data from the Mephisto task and input it into the json file,
if it doesn't already exist. Requries that the data is approved.
"""
import os
import json
import shutil

TARGET_FILE = os.path.join(os.path.dirname(__file__), "out_data", "results.json")
BACKUP_FILE = TARGET_FILE + ".bak"

SOFT_REJECTS = os.path.join(os.path.dirname(__file__), "out_data", "results-soft-reject.json")
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

    skipped = 0
    for sr_data in soft_rejects.values():
        if sr_data['primary_carryable'] or sr_data['secondary_carryable']:
            results[sr_data['id']] = sr_data
        else:
            skipped += 1
    print(f"Skipped {skipped} for not having carryable objects")

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