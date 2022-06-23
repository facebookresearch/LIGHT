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
task_names = ["objects-interaction-task-allowlist-attributes-1"]

units = []
for t in task_names:
    units.extend(mephisto_data_browser.get_units_for_task_name(t))

print(f"prev len: {len(units)}")
print(Counter([u.get_status() for u in units]))

bad_users = set()
#with open('./users_who_didnt_get_it.txt', 'r') as f:
#    d = f.read()
#    bad_users.update(d.split("\n"))

user_to_count = {}
user_to_data = {}

for unit in units:
    status = unit.get_db_status()
    data = mephisto_data_browser.get_data_from_unit(unit)
    outputs = data['data']['outputs']
    # rawAction = outputs['rawAction']
    # actionDescription = outputs['actionDescription']
    # if any("wear" in word.lower() for word in rawAction.split(" ")):
    #     continue
    worker = unit.get_assigned_agent().get_worker()
    worker_name = worker.worker_name
    cur_counts = user_to_count.get(worker_name, (0, 0))
    accepted, total = cur_counts
    accepted = accepted + int(status == "accepted")
    user_to_count[worker_name] = (accepted, total + 1)
    # user_to_data[worker_name] = [(rawAction, actionDescription), *user_to_data.get(worker_name, [])]

print("-"*100)
print('ALL USERS: ')
all_accepted = sum([w[0] for w in user_to_count.values()])
all_total = sum([w[1] for w in user_to_count.values()])
print(f"Accepted: {all_accepted}")
print(f"Total: {all_total}")
pct = all_accepted / all_total * 100
print(f"% Acc: {pct:0.3f}%")

print("-"*100)
print('GOOD USERS: ')
all_accepted = sum([w[0] for name, w in user_to_count.items() if name not in bad_users])
all_total = sum([w[1] for name, w in user_to_count.items() if name not in bad_users])
print(f"Accepted: {all_accepted}")
print(f"Total: {all_total}")
pct = all_accepted / all_total * 100
print(f"% Acc: {pct:0.3f}%")

print("-"*100)
print('GOOD USERS Over 80%: ')
all_accepted = sum([w[0] for name, w in user_to_count.items() if name not in bad_users and w[0]/w[1] > 0.8])
all_total = sum([w[1] for name, w in user_to_count.items() if name not in bad_users and w[0]/w[1] > 0.8])
print(f"Accepted: {all_accepted}")
print(f"Total: {all_total}")
pct = all_accepted / all_total * 100
print(f"% Acc: {pct:0.3f}%")

print("*"*100)
print("Extra Good Users")
for name, count in user_to_count.items():
    if name not in bad_users and count[0]/count[1] > 0.8:
        print(name)
print("*"*100)
print("Less Good Users")
for name, count in user_to_count.items():
    if name in bad_users or count[0]/count[1] <= 0.8:
        print(name)

items = sorted(user_to_count.items(), key=lambda x: x[1][0]/x[1][1])
print(items)

# for name, items in user_to_data.items():
#     print("-"*100)
#     print(f"NAME: {name}")
#     print(items)
    # for rA, aD in items:
    #     print(rA, aD)

