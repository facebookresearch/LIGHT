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

NO_OP_RESULTS = "no-op-actions"
RGULAR_RESULTS = "results"


RESULTS_FILE = os.path.join(os.path.dirname(__file__), "out_data", f"{RGULAR_RESULTS}.json")
NO_OP_FILE = os.path.join(os.path.dirname(__file__), "out_data", f"{NO_OP_RESULTS}.json")

def main():
    results = {}
    with open(RESULTS_FILE, 'r') as target_file:
        results = json.load(target_file)
    no_op_results = {}
    with open(NO_OP_FILE, 'r') as target_file:
        no_op_results = json.load(target_file)

    current_results_len = len(results)
    print("Existing narrations: ", current_results_len)
    auto_grounded_results = [r for r in results.values() if r['object_attributes'].get('before') is not None]
    print("Auto-Grounded narrations: ", len(auto_grounded_results))
    human_grounded_results = [r for r in auto_grounded_results if r.get('edit_data') is not None]
    print("Human Grounded (completed) narrations: ", len(human_grounded_results))
    valid_results = [r for r in human_grounded_results if r['edit_data']['interactionValid'] is True]
    print("Human Validated narrations: ", len(valid_results))

    current_results_len = len(no_op_results)
    print("Existing no-op narrations: ", current_results_len)
    auto_grounded_results = [r for r in no_op_results.values() if r['object_attributes'].get('before') is not None]
    print("Auto-Grounded no-op narrations: ", len(auto_grounded_results))
    prog_validated_results = [r for r in auto_grounded_results if r.get('edit_data') is not None]
    print("Validated No-op narrations: ", len(prog_validated_results))

if __name__ == '__main__':
    main()