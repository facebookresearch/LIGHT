#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.data_model.worker import Worker
from mephisto.data_model.unit import Unit
from mephisto.abstractions.providers.mturk.mturk_utils import get_assignments_for_hit

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

DO_REVIEW = True

units = mephisto_data_browser.get_units_for_task_name(input("Input task name: "))

tasks_to_show = input("Tasks to see? (a)ll/(u)nreviewed: ")
if tasks_to_show in ["all", "a"]:
    DO_REVIEW = False
else:
    units = [u for u in units if u.get_status() == "completed"]
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


def format_for_printing_data(data):
    # Custom tasks can define methods for how to display their data in a relevant way
    worker_name = Worker(db, data["worker_id"]).worker_name
    contents = data["data"]
    duration = contents["times"]["task_end"] - contents["times"]["task_start"]
    metadata_string = (
        f"Worker: {worker_name}\nUnit: {data['unit_id']}\n"
        f"Duration: {int(duration)}\nStatus: {data['status']}\n"
    )

    inputs = contents["inputs"]
    inputs_string = f"Character: {inputs['character_name']}\nDescription: {inputs['character_description']}\n"

    outputs = contents["outputs"]
    output_string = f"   Rating: {outputs['rating']}\n"
    found_files = outputs.get("files")
    if found_files is not None:
        file_dir = Unit(db, data["unit_id"]).get_assigned_agent().get_data_dir()
        output_string += f"   Files: {found_files}\n"
        output_string += f"   File directory {file_dir}\n"
    else:
        output_string += f"   Files: No files attached\n"
    return f"-------------------\n{metadata_string}{inputs_string}{output_string}"

units_with_data = [(unit, mephisto_data_browser.get_data_from_unit(unit)) for unit in units]
print("Units found: ", len(units_with_data))
workers = set([ud[1]['worker_id'] for ud in units_with_data])
workers_arrays = {w_id: [] for w_id in workers}
for (u, d) in units_with_data:
    workers_arrays[d['worker_id']].append((u, d))

print("Total workers so far: ", len(workers_arrays))

def repair_results(u_data):
    u_id = u_data['unit_id']
    unit = Unit(db, u_id)
    input_data = unit.get_assignment().get_assignment_data().shared

    hit_id = unit.get_mturk_hit_id()
    if hit_id is None:
        print("Could not repair unit", u_id)
        return
    requester = unit.get_requester()
    client = unit._get_client(requester._requester_name)
    assignment_data = get_assignments_for_hit(client, hit_id)
    content = assignment_data[0]['Answer']
    true_false_string = content.split('<FreeText>')[1].split('</FreeText>')[0]
    true_false_array = [t == 'true' for t in true_false_string.split(',')]
    paired_array = [true_false_array[i:i + 2] for i in range(0, len(true_false_array), 2)]
    output_data = {'final_data': {'ratings': paired_array}}
    agent = unit.get_assigned_agent()
    agent.state.state['inputs'] = input_data
    agent.state.state['outputs'] = output_data
    agent.state.save_data()

def display_results(u_data):
    if u_data['data']['outputs'] is None:
        print('Repairing', u_data['unit_id'])
        repair_results(u_data)
        return 0, []
    ratings = u_data['data']['outputs']['final_data']['ratings']
    input_to_output = zip(u_data['data']['inputs']['text_lines'], ratings)
    false_count = 20 - sum([sum([int(t) for t in turn_ratings]) for turn_ratings in ratings])
    display_lines = [f"{v[0]} {v[1]}: {l}" for (l, v) in input_to_output] 
    return false_count, display_lines

def get_avg_false_count(work):
    falses = 0
    processed = [display_results(w[1]) for w in work]
    false_array = [p[0] for p in processed]
    return sum(false_array) / len(false_array)

def approve_all_for_id(worker_id):
    for (unit, _stuff) in workers_arrays[worker_id]:
        unit.get_assigned_agent().approve_work()

id_to_avg = {w_id: (len(workers_arrays[w_id]), get_avg_false_count(workers_arrays[w_id])) for w_id in workers_arrays.keys()}
print("\n".join([f"{k}: {v}" for k, v in id_to_avg.items()]))
good_ids = [w_id for (w_id, (count, av)) in id_to_avg.items() if av <= 5]
bad_ids = [w_id for (w_id, (count, av)) in id_to_avg.items() if av > 5]

def approve_all_for_id(worker_id):
    for (unit, _stuff) in workers_arrays[worker_id]:
        unit.get_assigned_agent().approve_work()

import code
code.interact(local=locals())

raise NotImplementedError()

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
