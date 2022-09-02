#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.data_model.worker import Worker
from mephisto.data_model.unit import Unit
from collections import Counter

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

# from mephisto.utils.qualifications import find_or_create_qualification

# find_or_create_qualification(db, "collect_narrations_task_allow")

DO_REVIEW = True

TASKS = ["objects-interaction-task-pilot-4", "objects-interaction-task-pilot-5"]
TASKS.extend(["ground-stage-2-pilot-2", "ground-stage-2-pilot-3"])
TASKS.extend(["ground-stage-1-pilot-3", "ground-stage-1-pilot-4"])
TASKS.extend(["ground-stage-3-task-1", "ground-stage-3-task-2"])


good_workers = set()

for task_name in TASKS:

    # units = mephisto_data_browser.get_units_for_task_name("objects-interaction-task-pilot-4")
    units = mephisto_data_browser.get_units_for_task_name(task_name)

    print(f"prev len: {len(units)}")
    print(Counter([u.get_status() for u in units]))
    # units = [u for u in units if u.get_status() == "completed"]
    # units = [u for u in units if u.get_status() == "completed"]
    # print(f"len: {len(units)}")

    workers_to_res = {}
    worker_name_to_worker = {}

    for unit in units:
        worker = unit.get_assigned_agent().get_worker()
        worker_name = worker.worker_name
        worker_name_to_worker[worker_name] = worker
        status = unit.get_db_status()
        workers_to_res[worker_name] = [status, *workers_to_res.get(worker_name, [])]

    # print({k:v for k, v in workers_to_res.items() if len(v) > 1})
    for k, v in workers_to_res.items():
        if len(v) <= 0:
            continue
        counted =  Counter(v)
        # if counted.get("accepted", 0) >= counted.get('soft_rejected', 0) * 2:
        if counted.get("accepted", 0) == len(v):
            worker = worker_name_to_worker[k]
            good_workers.add(k)
            # worker.grant_qualification("collect_narrations_task_allow")
            # print(k)
            # worker.grant_qualification("collect_narrations_task_block", 0)
            # print(worker_name_to_worker[k], counted.get("accepted", 0), counted.get('soft_rejected', 0))


with open('./add_good_workers.txt', 'w') as f:
    f.write("\n".join(good_workers))