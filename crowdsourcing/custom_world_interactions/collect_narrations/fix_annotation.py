#!/usr/bin/env python3

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.data_model.worker import Worker
from mephisto.data_model.unit import Unit
from collections import Counter

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

DO_REVIEW = True

# task_names = ["objects-interaction-task-pilot-3", "objects-interaction-task-pilot-4", "objects-interaction-task-pilot-5"]
task_names = ["objects-interaction-task-pilot-5"]

units = []
for t in task_names:
    units.extend(mephisto_data_browser.get_units_for_task_name(t))

print(f"prev len: {len(units)}")
print(Counter([u.get_status() for u in units]))

# workers_to_res = {}
# worker_name_to_worker = {}

# for unit in units:
#     status = unit.get_db_status()
#     # contents = unit["data"]
#     data = mephisto_data_browser.get_data_from_unit(unit)
#     outputs = data['data']['outputs']
#     if "pristine looking bucket, without a mark. Must have" in outputs['rawAction']:
#         print(outputs)
#         unit.set_db_status("soft_rejected")
#         break
