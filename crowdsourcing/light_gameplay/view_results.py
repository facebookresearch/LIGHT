#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.examine_utils import run_examine_or_review, print_results
from mephisto.data_model.worker import Worker
from light.colors import Colors as C

db = LocalMephistoDB()


def format_data_for_printing(data):
    worker_name = Worker.get(db, data["worker_id"]).worker_name
    duration = data["task_end"] - data["task_start"]
    metadata_string = (
        f"Worker: {worker_name}\nUnit: {data['unit_id']}\n"
        f"Duration: {int(duration)}\nStatus: {data['status']}\n"
    )

    dialogue_string = ""
    dialogue_data = data["data"]["final_submission"]["data"]
    feedback = data["data"]["final_submission"]["comments"]

    curr_actor = None

    says = 0
    dos = 0
    for turn in dialogue_data:
        text = turn["text"].strip()
        if turn["caller"] == "SoulSpawnEvent":
            curr_actor = turn["actor"]
            dialogue_string += f"{text}\n"
        elif turn.get("actor") is None:
            c = None
            if text.endswith('"'):
                says += 1
                c = C.BOLD_GREEN
            else:
                dos += 1
                c = C.BOLD_BLUE
            dialogue_string += f"{c}{text}{C.RESET}\n"
        elif turn.get("actor") == curr_actor:
            text = text.replace("\n", "\n    ")
            dialogue_string += f"  {text}\n"
        else:
            text = text.replace("\n", "\n    ")
            dialogue_string += f"  {C.PURPLE}{text}{C.RESET}\n"

    return (
        f"{metadata_string}"
        f"Says: {says}, Dos: {dos}\n"
        f"Feedback: {feedback}\n\n"
        f"{dialogue_string}-----------\n\n"
    )


def main():
    db = LocalMephistoDB()
    run_examine_or_review(db, format_data_for_printing)


if __name__ == "__main__":
    main()
