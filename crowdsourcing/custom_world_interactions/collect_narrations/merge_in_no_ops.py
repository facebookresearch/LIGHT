#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Merge no-ops file results into the main results. Assumes no-ops have been properly
validated.
"""
import os
import json
import shutil

TARGET_FILE = os.path.join(os.path.dirname(__file__), "out_data", "results.json")
BACKUP_FILE = TARGET_FILE + ".bak"

NO_OP_FILE = os.path.join(os.path.dirname(__file__), "out_data", "no-op-actions.json")
BACKUP_NO_OP_FILE = NO_OP_FILE + ".bak"

def main():
    if os.path.exists(BACKUP_FILE):
        print("Backup file still exists, perhaps something went wrong last run? Check and remove before continuing")
        return
    results = {}
    if os.path.exists(TARGET_FILE):
        shutil.copyfile(TARGET_FILE, BACKUP_FILE)
        with open(TARGET_FILE, 'r') as target_file:
            results = json.load(target_file)
    no_ops_results = {}
    if os.path.exists(NO_OP_FILE):
        shutil.copyfile(NO_OP_FILE, BACKUP_NO_OP_FILE)
        with open(NO_OP_FILE, 'r') as target_file:
            no_ops_results = json.load(target_file)

    current_results_len = len(results)
    print("Existing narrations: ", current_results_len)
    current_results_len_json = len(json.dumps(results))

    for no_op_data in no_ops_results.values():
        results[no_op_data['id']] = no_op_data

    # Write out results
    with open(TARGET_FILE, "w+") as target_file:
        json.dump(results, target_file, indent=2)

    # Write out results
    if (len(no_ops_results) > 0):
        with open(NO_OP_FILE, "w+") as target_file:
            json.dump(no_ops_results, target_file, indent=2)
        if os.path.exists(BACKUP_NO_OP_FILE):
            os.remove(BACKUP_NO_OP_FILE)

    # Before we clear backup, ensure we didn't accidentally delete data
    assert len(results) >= current_results_len
    assert len(json.dumps(results)) >= current_results_len_json
    print("Collected narrations: ", len(results))
    if os.path.exists(BACKUP_FILE):
        os.remove(BACKUP_FILE)

if __name__ == '__main__':
    main()