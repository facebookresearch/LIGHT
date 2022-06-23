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

# task_names = ["objects-interaction-task-pilot-3", "objects-interaction-task-pilot-4", "objects-interaction-task-pilot-5"]
# task_names = ["objects-interaction-task-pilot-5"]
task_names = ["objects-interaction-task-allowlist-collection-2"]

units = []
for t in task_names:
    units.extend(mephisto_data_browser.get_units_for_task_name(t))

print(f"prev len: {len(units)}")
print(Counter([u.get_status() for u in units]))

# workers_to_res = {}
# worker_name_to_worker = {}

# bad_raws = ["wear cross over cotton tunic", "Use stool with gilded mirror", "drop jugs on ground"]
bad_raws = ["Use Rolling Pins on the Wooden Benches"]

for unit in units:
    status = unit.get_db_status()
    # contents = unit["data"]
    data = mephisto_data_browser.get_data_from_unit(unit)
    outputs = data['data']['outputs']
    if any(r in outputs['rawAction'] for r in bad_raws):
        print(outputs)
        unit.set_db_status("soft_rejected")
    # if "Use stool with gilded mirror" in outputs['rawAction']:
    #     print(outputs)
    #     unit.set_db_status("soft_rejected")
    #     # break
    # if "drop jugs on ground" in outputs['rawAction']:
    #     print(outputs)
    #     unit.set_db_status("soft_rejected")
    