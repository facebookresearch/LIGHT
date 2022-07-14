#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.data_model.worker import Worker
from mephisto.data_model.unit import Unit
from collections import Counter
import pickle
from light.data_model.light_database import LIGHTDatabase
import jsonlines
import json

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
unit = accepted_units[0]


# with open('./test_graph_from_build.pkl', 'rb') as f:
#     GRAPH = pickle.load(f)
data = []
with jsonlines.open('/private/home/alexgurung/ParlAI/data/light_common_sense/gameplays/processed_test_convs.jsonl', 'r') as f:
    for line in f:
        data.append(line)
        if len(data) > 5:
            break

GRAPH = json.loads(data[0][0]['game_state_before_action'])

ROOM_ID = GRAPH['rooms'][0]

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
secondary_object = task_state['object2']['name']
primary_object = task_state['object1']['name']

LIGHT_DB_PATH = "~/ParlAI/data/light/environment/db/d3/database3.db"
def get_object_lists(db_path):
    db = LIGHTDatabase(db_path)
    with db as ldb:
        all_objects = [dict(obj) for obj in ldb.get_object()]

    primary_objects = []
    secondary_objects = []
    for obj in all_objects:
        new_obj = obj
        new_obj['desc'] = new_obj['physical_description']
        if obj["is_gettable"] > 0.5:
            primary_objects.append(new_obj)
        secondary_objects.append(new_obj)

    return primary_objects, secondary_objects

primary_objects, secondary_objects = get_object_lists(LIGHT_DB_PATH)
desc_to_objects = {p['desc']:p for p in secondary_objects}

obj1_db = desc_to_objects[task_state['object1']['desc']]
obj2_db = desc_to_objects[task_state['object2']['desc']]
print(obj1_db)


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


obj1 = {
            "agent": False,
            "classes": [
                "object"
            ],
            "contain_size": 0,
            "contained_nodes": {},
            "container": False,
            "container_node": {
                "target_id": ROOM_ID
            },
            "db_id": None,
            "dead": None,
            "desc": obj1_db['desc'],
            "drink": obj1_db['is_drink'] > 0.5,
            "equipped": False,
            "food": obj1_db['is_food'] > 0.5,
            "food_energy": 0,
            "gettable": True,
            "locked_edge": None,
            "name": obj1_db['name'],
            "name_prefix": "a",
            "names": [
                obj1_db['name']
            ],
            "node_id": obj1_db['name'],
            "object": True,
            "on_use": on_use,
            "room": False,
            "size": 1,
            "stats": {
                "damage": 0,
                "defense": 0
            },
            "surface_type": "on",
            "value": 1,
            "wearable": obj1_db['is_wearable'] > 0.5,
            "wieldable": obj1_db['is_weapon'] > 0.5
}

obj2 = {
            "agent": False,
            "classes": [
                "object"
            ],
            "contain_size": 0,
            "contained_nodes": {},
            "container": False,
            "container_node": {
                "target_id": ROOM_ID
            },
            "db_id": None,
            "dead": None,
            "desc": obj2_db['desc'],
            "drink": obj2_db['is_drink'] > 0.5,
            "equipped": False,
            "food": obj2_db['is_food'] > 0.5,
            "food_energy": 0,
            "gettable": True,
            "locked_edge": None,
            "name": obj2_db['name'],
            "name_prefix": "a",
            "names": [
                obj2_db['name']
            ],
            "node_id": obj2_db['name'],
            "object": True,
            "on_use": None,
            "room": False,
            "size": 1,
            "stats": {
                "damage": 0,
                "defense": 0
            },
            "surface_type": "on",
            "value": 1,
            "wearable": obj2_db['is_wearable'] > 0.5,
            "wieldable": obj2_db['is_weapon'] > 0.5
}

pnid = obj1['node_id']
snid = obj2['node_id']
GRAPH['objects'].append(pnid)
GRAPH['objects'].append(snid)
GRAPH['nodes'][ROOM_ID]['contained_nodes'][pnid] = {'target_id': pnid}
GRAPH['nodes'][ROOM_ID]['contained_nodes'][snid] = {'target_id': snid}
GRAPH['nodes'][pnid] = obj1
GRAPH['nodes'][snid] = obj2

with open('./use_event_test.json', 'w') as f:
    json.dump(GRAPH, f)
