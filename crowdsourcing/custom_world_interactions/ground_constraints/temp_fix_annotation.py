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

task_names = ["objects-interaction-task-allowlist-constraints-3"]

units = []
for t in task_names:
    units.extend(mephisto_data_browser.get_units_for_task_name(t))

print(f"prev len: {len(units)}")
print(Counter([u.get_status() for u in units]))
units= [u for u in units if u.get_status() == "accepted"]

# workers_to_res = {}
# worker_name_to_worker = {}

# bad_raws = ["wear cross over cotton tunic", "Use stool with gilded mirror", "drop jugs on ground"]
bad_raws = ["There was a huge fire, I grabbed the bucket of water and poured it on the torchs."]

for unit in units:
    status = unit.get_db_status()
    # contents = unit["data"]
    data = mephisto_data_browser.get_data_from_unit(unit)
    outputs = data['data']['outputs']['this_task_state']
    try:
        if any(r in outputs['broadcastMessage'] for r in bad_raws):
            unit.set_db_status("soft_rejected")
    except:
        unit.set_db_status("soft_rejected")