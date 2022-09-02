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

DO_REVIEW = True

task_sets = [
    # ["objects-interaction-task-allowlist-collection-2"],
    ["objects-interaction-task-allowlist-events-1"],
    ["objects-interaction-task-allowlist-attributes-1"],
    ["objects-interaction-task-allowlist-constraints-3"]
    ]

for task_names in task_sets:
    units = []
    for t in task_names:
        units.extend(mephisto_data_browser.get_units_for_task_name(t))
    print(task_names)
    print(f"prev len: {len(units)}")
    print(Counter([u.get_status() for u in units]))
    units= [u for u in units if u.get_status() == "accepted"]
    # units= [u for u in units if u.get_status() == "accepted"]

    previously_seen = set()
    total_to_delete = 0
    for unit in units:
        status = unit.get_db_status()
        # contents = unit["data"]
        data = mephisto_data_browser.get_data_from_unit(unit)
        inputs = data["data"]['inputs']
        o1 = inputs['object1']['name']
        o2 = inputs['object2']['name']
        if (o1, o2) in previously_seen:
            total_to_delete += 1
            # unit.set_db_status("soft_rejected")
            
        previously_seen.add((o1, o2))
    print(f"deleted: {total_to_delete}")