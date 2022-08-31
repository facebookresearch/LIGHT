# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.examine_utils import run_examine_or_review, print_results
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
        outputs = contents["outputs"]["final_data"]
        primary = outputs["primaryObject"]
        secondary = outputs["secondaryObject"]
        primary_object_map = {
            i["name"]: i["desc"] for i in inputs["primary_object_list"]
        }
        primary_object_stringlist = list(primary_object_map.keys())
        secondary_object_map = {
            i["name"]: i["desc"] for i in inputs["secondary_object_list"]
        }
        secondary_object_stringlist = list(secondary_object_map.keys())
        inputs_string = (
            f"Input:\n\tPrimary Object List: {primary_object_stringlist}\n"
            f"\tSecondary Object List: {secondary_object_stringlist}\n"
            f"\tSelected Context:\n"
            f"\t\t{primary}: {primary_object_map[primary]}\n"
            f"\t\t{secondary}: {secondary_object_map[secondary]}\n\n"
        )
        outputs_string = f"Output:\n\tUse {primary} with {secondary}\n\tAction: {outputs['actionDescription']}\n"

    return f"-------------------\n{metadata_string}{inputs_string}{outputs_string}"


def main():
    db = LocalMephistoDB()
    run_examine_or_review(db, format_data_for_printing)


if __name__ == "__main__":
    main()
