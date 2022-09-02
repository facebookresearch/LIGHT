#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

###########################################################
# This helper file is called by get_use_event_dataset_from_mephisto.py
# and parses the mephisto data into usable information for 
# the commonsense teachers
###########################################################

from light.data_model.light_database import LIGHTDatabase
import random
import parlai_internal.tasks.light_common_sense.constants as consts
import pickle
import copy

# NOTE: this may be outdated with new dataset system
LIGHT_DB_PATH = "~/ParlAI/data/light/environment/db/d3/database3.db"
db = LIGHTDatabase(LIGHT_DB_PATH)
with db as ldb:
    all_objects = [dict(obj) for obj in ldb.get_object()]
    
ALL_OBJECTS = []
for obj in all_objects:
    obj['desc'] = obj['physical_description']
    ALL_OBJECTS.append(obj)
# to retrieve the 
DESC_TO_OBJECTS = {p['desc']:p for p in ALL_OBJECTS}

def get_useful_data_from_use_event(data):
    # input data is structured like a mephisto data-point from the ground-constraint task
    task_state = data['data']['outputs']['this_task_state']
    
    is_secondary_held = task_state['isSecondaryHeld']
    raw_action = task_state['rawAction']
    narration = task_state['interaction']
    object1 = task_state['object1']['name']
    object2 = task_state['object2']['name']
    non_actor_narration = task_state["broadcastMessage"]
    # fix some common small mistakes in narrations (and object names)
    for key, replacement in [
        ("villager", "ACTOR"), 
        ("OBJECT1", object1), 
        ("OBJECT2", object2)]:
        narration = narration.replace(key, replacement)
        non_actor_narration = non_actor_narration.replace(key, replacement)
    if narration.startswith("I "):
        narration = "You " + narration[3:]
    if non_actor_narration.startswith("I "):
        non_actor_narration = "You " + non_actor_narration[3:]

    ##################################################################
    # get constraints and attributes graph change lines
    # skips step in 
    ##################################################################
    constraints = data['data']['outputs']['constraints']
    attributes = data['data']['outputs']['events']
    constraint_lines = []
    attribute_lines = []
    for c in constraints:
        # filter for comparison constraints, other constraints aren't relevant here
        if 'attribute_compare_value' not in c['type']:
            continue
        # print(c)
        attr_name = c['params']['key']
        negated = c['params']['cmp_type'] == "neq"
        attr_val = f"not {attr_name}" if negated else attr_name
        attr_val = attr_val.replace("not not ", "")
        object_name = data['data']['outputs']['this_task_state']['object1']['name']
        if "secondary" in c['type']:
            object_name = data['data']['outputs']['this_task_state']['object2']['name']
        # the constraint row is name -=- HAS_ATTRIBUTE -=- value
        row = consts.GRAPH_TUPLES_DELIM.join([object_name, consts.GraphEdges.HAS_ATTRIBUTE.name, attr_val])
        constraint_lines.append(row)

    misc_created_attrs = []
    for c in attributes:
        if 'modify_attribute' not in c['type']:
            continue
        if 'location' in c['type']:
            # an object changes location
            obj = 'object1' if "primary" in c['type'] else 'object2'
            object_name = data['data']['outputs']['this_task_state'][obj]['name']
            target_obj = data['data']['outputs']['this_task_state']['object2']['name']
            location = target_obj # in_used_target_item
            if c['params']['value'] == 'in_used_item':
                location = data['data']['outputs']['this_task_state']['object2']['name']
            elif c['params']['value'] == 'in_actor':
                location = "actor"
            elif c['params']['value'] == 'in_room':
                location = "room"

            # object -=- IS_INSIDE -=- location
            row = consts.GRAPH_TUPLES_DELIM.join([object_name, consts.GraphEdges.IS_INSIDE.name, location])

            attribute_lines.append(row)
        elif "description" in c["type"]:
            # one of the objects changes description
            obj = 'object1' if "primary" in c['type'] else 'object2'
            object_name = data['data']['outputs']['this_task_state'][obj]['name']
            new_desc = c['params']['value']
            # filer some of the new descriptions which were poor or accidentally added
            if len(new_desc) <= 20:
                continue
            # row = f"{object_name} -=- HAS_DESCRIPTION -=- {new_desc}"
            row = consts.GRAPH_TUPLES_DELIM.join([object_name, consts.GraphEdges.HAS_DESCRIPTION.name, new_desc])
            attribute_lines.append(row)
        elif "create_entity" in c['type']:
            # create entity is handled further down
            continue
        elif "modify_attribute_created" in c['type']:
            # modify attribute of created object
            if 'value' not in c['params']:
                c['params']['value'] = True
            attr_name = c['params']['key']
            negated = not c['params']['value']
            attr_val = f"not {attr_name}" if negated else attr_name
            attr_val = attr_val.replace("not not ", "")
            # get created_entity since we are modifying a created object
            created_entity = task_state['createdEntity']
            created_name = created_entity['name']
            # created_name -=- HAS_ATTRIBUTE -=- attr
            row = consts.GRAPH_TUPLES_DELIM.join([created_name, consts.GraphEdges.HAS_ATTRIBUTE.name, attr_val])
            misc_created_attrs.append(row)
        else:
            # modifying one of two given objects
            attr_name = c['params']['key']
            negated = not c['params']['value']
            attr_val = f"not {attr_name}" if negated else attr_name
            attr_val = attr_val.replace("not not ", "")
            object_name = data['data']['outputs']['this_task_state']['object1']['name']
            if "secondary" in c['type']:
                object_name = data['data']['outputs']['this_task_state']['object2']['name']
            # row = f"{object_name} -=- HAS_ATTRIBUTE -=- {attr_val}"
            row = consts.GRAPH_TUPLES_DELIM.join([object_name, consts.GraphEdges.HAS_ATTRIBUTE.name, attr_val])
            attribute_lines.append(row)

    task_state = data['data']['outputs']['this_task_state']
    
    timesRemaining = task_state['timesRemaining'][0]
    remaining_uses = "inf"
    if timesRemaining == "ONCE":
        remaining_uses = 1
    elif timesRemaining == "A FEW TIMES":
        remaining_uses = 3

    interaction_description = task_state['interaction']
    secondary_object = task_state['object2']['name']
    # primary_object = task_state['object1']['name']

    obj1_db = DESC_TO_OBJECTS[task_state['object1']['desc']]
    obj2_db = DESC_TO_OBJECTS[task_state['object2']['desc']]


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
        create_event = {
            "type": "create_entity",
            "params": {
                "type": "in_room",
                "object": {
                    "desc": created_entity['desc'],
                    "is_food": 0.0,
                    "is_wearable": False,
                    "name": created_entity['name'],
                    "name_prefix": "an" if created_entity['name'][0].lower() in "aeiou" else "a",
                    }
                }
            }
        events.append(create_event)

    # NOTE: on_use doesn't currently handle the constraints very well since the attributes
    # are made up by workers, so be mindful when simulating that this does everything you 
    # need it too
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
                'contains_from_db':[],
                consts.IS_IN_ROOM:True,
                "agent": False,
                "classes": [
                    "object"
                ],
                "contain_size": 0,
                "contained_nodes": {},
                "container": False,
                "container_node": {
                    "target_id": None
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
                "name_prefix": "an" if obj1_db['name'][0].lower() in "aeiou" else "a",
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
                'contains_from_db':[],
                consts.IS_IN_ROOM:True,
                "agent": False,
                "classes": [
                    "object"
                ],
                "contain_size": 0,
                "contained_nodes": {},
                "container": False,
                "container_node": {
                    "target_id": None
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
                "name_prefix": "an" if obj2_db['name'][0].lower() in "aeiou" else "a",
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
                "wieldable": obj2_db['is_weapon'] > 0.5,
    }
    
    obj1['misc_attrs'] = []
    obj2['misc_attrs'] = []
    obj1['misc_constrs'] = []
    obj2['misc_constrs'] = []

    for attribute_line in attribute_lines:
        name = attribute_line.split(consts.GRAPH_TUPLES_DELIM)[0]
        relevant_obj = obj1
        if name == obj2['name']:
            relevant_obj = obj2
        prior_miscellaneous_attrs = relevant_obj.get('misc_attrs', [])
        prior_miscellaneous_attrs.append(attribute_line)
        relevant_obj['misc_attrs'] = prior_miscellaneous_attrs

    for constraint_line in constraint_lines:
        name = constraint_line.split(consts.GRAPH_TUPLES_DELIM)[0]
        relevant_obj = obj1
        if name == obj2['name']:
            relevant_obj = obj2
        prior_miscellaneous_constrs = relevant_obj.get('misc_constrs', [])
        prior_miscellaneous_constrs.append(constraint_line)
        relevant_obj['misc_constrs'] = prior_miscellaneous_constrs
    

    created_object = None
    if is_creating == True:
        created_object = copy.deepcopy(obj2)
        created_name = created_entity['name']
        # container node is unknown, but set so its clear it should be changed
        created_object["container_node"] = {"target_id":None}
        created_object["desc"] = created_entity['desc']
        created_object["misc_attrs"] = [line.replace("CREATED_OBJ", created_name) for line in misc_created_attrs]
        created_object["misc_constrs"] = []
        created_object["name"] = created_name
        created_object['node_id'] = created_name
        created_object["name_prefix"] = "an" if created_name[0].lower() in "aeiou" else "a"

    misc_use_action_data = {
        "raw_action":raw_action,
        "narration":narration,
        "constraint_lines":constraint_lines,
        "attribute_lines":attribute_lines, 
        "object1":object1,
        "object2":object2,
        "created_object": created_object,
        "non_actor_narration": non_actor_narration,
        "is_secondary_held":is_secondary_held,
    }

    return {
        "obj1": obj1, 
        "obj2": obj2, 
        "created_object": created_object, 
        "misc_use_action_data": misc_use_action_data
        }
