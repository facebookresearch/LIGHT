#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.examine_utils import run_examine_or_review, print_results
from mephisto.data_model.worker import Worker
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from collections import Counter

db = LocalMephistoDB()

mephisto_data_browser = MephistoDataBrowser(db=db)
# task_names = ["objects-interaction-task-pilot-5", "objects-interaction-task-pilot-4"]
# task_names = ["objects-interaction-task-collection-1"]
task_names = ["objects-interaction-narration-task-pilot"]


def format_data_for_printing(data):
    worker_name = Worker.get(db, data["worker_id"]).worker_name
    contents = data["data"]
    duration = data["task_end"] - data["task_start"]
    metadata_string = (
        f"Worker: {worker_name}\nUnit: {data['unit_id']}\n"
        f"Duration: {duration / 60} (pay/hr: {0.85 * 60 / (duration / 60)})\nStatus: {data['status']}\n"
    )

    inputs_string = ""
    outputs_string = ""

    if contents["inputs"] is not None and contents["outputs"] is not None:
        inputs = contents["inputs"]
        # outputs = contents["outputs"]["final_data"]
        outputs = contents["outputs"]
        primary = outputs["primaryObject"]
        primaryDesc = outputs["primaryDescription"]
        secondary = outputs["secondaryObject"]
        secondary_object_map = {
            i["name"]: i["desc"] for i in inputs["secondary_object_list"]
        }
        secondary_object_stringlist = list(secondary_object_map.keys())
        inputs_string = (
            f"Input:\n"
            f"\tSecondary Object List: {secondary_object_stringlist}\n"
            f"\tSelected Context:\n"
            f"\t\t{primary}: {primaryDesc}\n"
            f"\t\t{secondary}: {secondary_object_map[secondary]}\n\n"
        )
        outputs_string = f"Output:\n\tUse {primary} with {secondary}\n\n\tRaw Action: {outputs.get('rawAction')}\n\tAction Description: {outputs['actionDescription']}\n"

    return f"-------------------\n{metadata_string}{inputs_string}{outputs_string}"


def main():
    db = LocalMephistoDB()
    run_examine_or_review(db, format_data_for_printing)


if __name__ == '__main__':
    main()
