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

# units = mephisto_data_browser.get_units_for_task_name(input("Input task name: "))
# We're only examining this task with this file, but in the future could rely on mephisto.tools.examine_utils.run_examine_or_review
# task_names = ["ground-stage-3-task-1", "ground-stage-3-task-2"]
# task_names = ["objects-interaction-task-allowlist-contraints-1"]
# task_names = ["objects-interaction-task-allowlist-constraints-2"]
task_names = ["objects-interaction-task-allowlist-constraints-3"]

units = []
for t in task_names:
    new_units = mephisto_data_browser.get_units_for_task_name(t)
    print(t)
    print(Counter([u.get_status() for u in new_units]))
    units.extend(new_units)

INPUT_FILE_TASKS = ["objects-interaction-task-allowlist-attributes-1"]
input_units = []
for t in INPUT_FILE_TASKS:
    new_units = mephisto_data_browser.get_units_for_task_name(t)
    print(t)
    print(Counter([u.get_status() for u in new_units]))


print(f"len: {len(units)}")
print(Counter([u.get_status() for u in units]))

accepted = [u for u in units if u.get_status() == "accepted"]

obj_name_tuples = []
for unit in accepted:
    inputs = mephisto_data_browser.get_data_from_unit(unit)["data"]['inputs']
    o1 = inputs['object1']['name']
    o2 = inputs['object2']['name']
    obj_name_tuples.append((o1, o2))

print(f"len(obj_name_tuples): {len(obj_name_tuples)}")
print(f"len(set(obj_name_tuples)): {len(set(obj_name_tuples))}")


tasks_to_show = input("Tasks to see? (a)ll/(u)nreviewed: ")
if tasks_to_show in ["all", "a"]:
    DO_REVIEW = False
    print(f"NOT REVIEWING TASKS")
else:
    units = [u for u in units if u.get_status() == "completed"]
    print(f"len: {len(units)}")
    print(
        "You will be reviewing actual tasks with this flow. Tasks that you either Accept or Pass "
        "will be paid out to the worker, while rejected tasks will not. Passed tasks will be "
        "specially marked such that you can leave them out of your dataset. \n"
        "When you pass on a task, the script gives you an option to disqualify the worker "
        "from future tasks by assigning a qualification. If provided, this worker will no "
        "longer be able to work on tasks where the set --block-qualification shares the same name.\n"
        "You should only reject tasks when it is clear the worker has acted in bad faith, and "
        "didn't actually do the task. Prefer to pass on tasks that were misunderstandings."
    )


def nice_location_name(new_location, primary_name, secondary_name):
    # Convert location name to a more readable format
    new_location_name = new_location
    if new_location == "in_room":
        new_location_name = "room"
    elif new_location == "in_actor":
        new_location_name = "held by actor"
    elif new_location == "in_used_item":
        new_location_name = "in/on " + primary_name
    elif new_location == "in_used_target_item":
        new_location_name = "in/on " + secondary_name
    return new_location_name


def obj_from_key(key, primary_obj, secondary_obj):
    # separated in case of naming convention change
    # currently in_used_item refers to the primary object, in_used_target_item refers to the secondary object
    return primary_obj if key == "in_used_item" else secondary_obj


def format_for_printing_data(data):
    worker_name = Worker.get(db, data["worker_id"]).worker_name
    contents = data["data"]
    duration = 0
    if "times" in contents:
        duration = contents["times"]["task_end"] - contents["times"]["task_start"]

    metadata_string = (
        f"Worker: {worker_name}\nUnit: {data['unit_id']}\n"
        f"Duration: {int(duration)}\nStatus: {data['status']}\n"
    )

    inputs = contents["inputs"]

    # get primary and secondary object for inputs and names
    primary_obj = inputs.get("object1", {})
    secondary_obj = inputs.get("object2", {})
    inputs_string = f"Inputs:\n\t(Primary Object) {primary_obj.get('name')}: {primary_obj.get('desc')}\n\t(Secondary Object) {secondary_obj.get('name')}: {secondary_obj.get('desc')}\n\tAction Description: {inputs.get('interaction')}\n\n"

    outputs = contents["outputs"]
    try:
        outputs["events"] = [e for e in outputs.get("events", []) if e is not None]
        outputs["constraints"] = [e for e in outputs.get("constraints", []) if e is not None]

        outputs_string = f"Output:\n"
        inputs_string += f"\tRaw Action:\t{outputs['this_task_state']['rawAction']}\n\n"
    except:
        return f"-------------------\n{metadata_string}{inputs_string}\nERROR"


    outputs_string += "\n\n\n"

    # want to print new narration first
    broadcast_messages = [
        e for e in outputs["events"] if e["type"] == "broadcast_message"
    ]
    if len(broadcast_messages) == 1:
        # character agnostic narration; Narration \t narration_text
        event = broadcast_messages[0]
        inputs_string += f"\tNarration:\n\t\t{event['params']['room_view']}\n\n"
    nb = outputs['this_task_state']['noBackstoryNarration'] if "noBackstoryNarration" in outputs['this_task_state'] else "N/A"
    inputs_string += f"\tReplaced Backstory:\t{nb}\n\n"
    inputs_string += f"\tBackstory Too Complex:\t{outputs['this_task_state']['hasBackstory']}\n\n"
    inputs_string += f"\tEvents:\n\n"
    for event in outputs["events"]:
        if event["type"] == "broadcast_message":
            # already added message
            continue
        elif event["type"] == "remove_object":
            # any objects removed; [Remove] (object_name)
            inputs_string += f"\t\t[Remove] ({event['params']['name']})\n\n"
        elif event["type"] == "create_entity":
            # any entities created; [Create Object] (object_name) with description: object_description
            inputs_string += f"\t\t[Create Object] ({event['params']['object']['name']}) with description: {event['params']['object']['desc']} \n\n"
        elif (
            event["type"] == "modify_attribute_primary"
            or event["type"] == "modify_attribute_secondary"
        ):
            # new/modified attributes after action; [Changed Attribute] ({object_name) \t is/isn't \t attribute
            cur_obj = obj_from_key(event['params']['type'], primary_obj, secondary_obj)
            is_isnt = "is" if event["params"].get("value") else "isn't"
            inputs_string += f"\t\t[Changed Attribute] ({cur_obj.get('name')})\t{is_isnt}\t{event['params']['key']}\n\n"
        elif (
            event["type"] == "modify_attribute_primary_description"
            or event["type"] == "modify_attribute_secondary_description"
        ):
            # new description for items; [New Description] (object_name): object_description
            cur_obj = obj_from_key(event['params']['type'], primary_obj, secondary_obj)
            inputs_string += f"\t\t[New Description] ({cur_obj.get('name')}): {event['params']['value']}\n\n"
        elif event["params"]["key"] == "location":
            # new location, map to more legible
            new_location = event["params"]["value"]
            new_location_name = nice_location_name(
                new_location, primary_obj.get("name"), secondary_obj.get("name")
            )
            cur_obj = obj_from_key(event['params']['type'], primary_obj, secondary_obj)

            inputs_string += f"\t\t[Changed Location] ({cur_obj.get('name')}): {new_location_name}\n\n"
        else:
            # malformed event, exclude
            continue

    outputs_string += f"\tConstraints:\n\n"
    for constraint in outputs["constraints"]:
        if constraint["type"] == "is_holding_secondary":
            cur_obj = obj_from_key(constraint['params']['complement'], primary_obj, secondary_obj)
            outputs_string += (
                f"\t\t[Must Hold] {cur_obj.get('name')}\n\n"
            )
        elif constraint["type"] == "in_room":
            outputs_string += f"\t\t[Required Location Description] {constraint['params']['room_name']}\n\n"
        elif (
            constraint["type"] == "attribute_compare_value_primary"
            or constraint["type"] == "attribute_compare_value_secondary"
        ):
            cur_obj = obj_from_key(constraint['params']['type'], primary_obj, secondary_obj)
            
            comparison = (
                "must be" if constraint["params"]["cmp_type"] == "eq" else "must not be"
            )
            outputs_string += f"\t\t[Constraint] {cur_obj.get('name')} \t {comparison} \t {constraint['params']['key']}\n\n"
        else:
            # malformed constraint, example
            continue
    for key in ["isSecondaryHeld",
                # "isReversible",
                "isInfinite",
                "timesRemaining",
                "isLocationConstrained",
                "constraintLocation"]:
        value = outputs['this_task_state'][key] if key in outputs['this_task_state'] else "N/A"
        outputs_string += f"\t[Constraint] {key} \t {value}\n\n"
    
    return f"-------------------\n{metadata_string}{inputs_string}{outputs_string}"

disqualification_name = None
for unit in units:
    print(format_for_printing_data(mephisto_data_browser.get_data_from_unit(unit)))
    if DO_REVIEW:
        keep = input("Do you want to accept this work? (a)ccept, (r)eject, (p)ass: ")
        if keep == "a":
            unit.get_assigned_agent().approve_work()
        elif keep == "r":
            reason = input("Why are you rejecting this work?")
            unit.get_assigned_agent().reject_work(reason)
        elif keep == "p":
            # General best practice is to accept borderline work and then disqualify
            # the worker from working on more of these tasks
            agent = unit.get_assigned_agent()
            agent.soft_reject_work()
            should_soft_block = input(
                "Do you want to soft block this worker? (y)es/(n)o: "
            )
            if should_soft_block.lower() in ["y", "yes"]:
                if disqualification_name == None:
                    disqualification_name = input(
                        "Please input the qualification name you are using to soft block for this task: "
                    )
                worker = agent.get_worker()
                worker.grant_qualification(disqualification_name, 1)
