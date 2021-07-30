#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.examine_utils import run_examine_by_worker
from mephisto.data_model.worker import Worker


db = LocalMephistoDB()


def format_data_for_printing(data):
    worker_name = Worker(db, data["worker_id"]).worker_name
    contents = data["data"]
    duration = contents["times"]["task_end"] - contents["times"]["task_start"]
    metadata_string = (
        f"Worker: {worker_name}\nUnit: {data['unit_id']}\n"
        f"Duration: {int(duration)}\nStatus: {data['status']}\n"
    )

    inputs_string = ""
    outputs_string = ""

    if contents["inputs"] is not None and contents["outputs"] is not None:
        inputs = contents["inputs"]
        inputs_string = f"Input:\n\tPrimary Object List: {inputs['primary_object_list']}\n\tSecondary Object List: {inputs['secondary_object_list']}\n\n"

        outputs = contents["outputs"]["final_data"]
        outputs_string = f"Output:\n\tUse {outputs['primaryObject']} with {outputs['secondaryObject']}\n\tAction: {outputs['actionDescription']}\n"

    return f"-------------------\n{metadata_string}{inputs_string}{outputs_string}"


run_examine_by_worker(db, format_data_for_printing)
