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
    new_units = mephisto_data_browser.get_units_for_task_name(t)
    print(t)
    print(Counter([u.get_status() for u in new_units]))
    units.extend(new_units)

print(f"prev len: {len(units)}")
print(Counter([u.get_status() for u in units]))

accepted_units = [u for u in units if u.get_status() == "accepted"]


import pickle

with open('./test_graph_from_build.pkl', 'rb') as f:
    GRAPH = pickle.load(f)

ROOM_ID = GRAPH['rooms'][0]

disqualification_name = None
for unit in accepted_units:
    data = mephisto_data_browser.get_data_from_unit(unit)
    # print(data.keys())
    task_state = data['data']['outputs']['this_task_state']
    raw = task_state['rawAction']
    # if not raw.lower().startswith('use'):
    #     print(raw.lower())
    timesRemaining = task_state['timesRemaining'][0]
    remaining_uses = "inf"
    if timesRemaining == "ONCE":
        remaining_uses = 1
    elif timesRemaining == "A FEW TIMES":
        remaining_uses = 3

    interaction_description = task_state['interaction']
    secondary_object = task_state['object2']
    primary_object = task_state['object1']

    created_entity = task_state['createdEntity']
    is_creating = task_state['isCreatingEntity']
    # if created_entity != "":
    events = [
            {
                "type": "broadcast_message",
                "params": {
                    "self_view": interaction_description
                }
                }
    ]
    if is_creating == True:
        # print(task_state)
        # print()
        # print(created_entity)
        create_event = {
            "type": "create_entity",
            "params": {
                "type": "in_room",
                "object": {
                    "desc": created_entity['desc'],
                    "is_food": 0.0,
                    "is_wearable": False,
                    "name": created_entity['name'],
                    "name_prefix": "a"
                    }
                }
            }
        events.append(create_event)
        # break
    
    

    on_use = [
            {
            "remaining_uses": remaining_uses,
            "events": events,
            "constraints": [
                {
                "type": "is_holding",
                "params": {
                    "complement": "used_item"
                }
                },
                {
                "type": "used_with_item_name",
                "params": {
                    "item": secondary_object
                }
                }
            ]
            }
        ]

    # print(on_use)

    

    break
    

