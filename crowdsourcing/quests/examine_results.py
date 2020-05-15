from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.data_model.worker import Worker

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

units = mephisto_data_browser.get_units_for_task_name(input("Input task name: "))

tasks_to_show = input("Tasks to see? (a)ll/(u)nreviewed: ")
if (tasks_to_show in ['all', 'a']):
    pass
else:
    units = [u for u in units if u.get_status() == 'completed']


def format_action(action_obj):
    action_type = action_obj['action_type']
    action_vals = action_obj['values']
    if action_type in ['hit', 'hug', 'drop', 'wield', 'wear', 'eat', 'drink', 'follow', 'go']:
        return f"{action_type} {action_vals[0]}"
    if action_type == 'give':
        return f"give {action_vals[0]} to {action_vals[1]}"
    if action_type == 'steal':
        return f"steal {action_vals[0]} from {action_vals[1]}"
    if action_type == 'use':
        return f"use {action_vals[0]} with {action_vals[1]}"
    if action_type == 'get':
        if action_vals[2] == '0':
            return f"get {action_vals[0]}"
        return f"get {action_vals[0]} from {action_vals[1]}"
    if action_type == 'put':
        split_word = "on" if action_vals[2] == "0" else "in"
        return f"put {action_vals[0]} {split_word} {action_vals[1]}"


def get_timeline_string(times, values):
    timeline_string = ""
    for idx, t in enumerate(times):
        timeline_string += (
            f"   -- {t}\n"
            f"     -- {format_action(values[idx])}\n"
        )
    return timeline_string


def format_for_printing_data(data):
    worker_name = Worker(db, data['worker_id']).worker_name
    contents = data['data']
    duration = contents['times']['task_end'] - contents['times']['task_start']
    metadata_string = f"Worker: {worker_name}\nDuration: {int(duration)}\n"

    inputs = contents['inputs']
    setting_split = ' '.join(inputs['description'].split('\n'))
    inputs_string = (
        f"Character: {inputs['character']}\nPersona: {inputs['persona']}\n"
        f"Setting: {setting_split}\nGoal text: {inputs['goal']}\n"
    )

    outputs = contents['outputs']['final_data']
    output_string = (
        f"   Short term goal: {outputs['text_values'][0]}\n"
        f"   Mid term goal: {outputs['text_values'][1]}\n"
        f"   Long term goal: {outputs['text_values'][2]}\n"
        f"   Timeline:\n"
        f"{get_timeline_string(inputs['time'], outputs['actions'])}\n"
    )
    return f"-------------------\n{metadata_string}{inputs_string}{output_string}"

for unit in units:
    print(format_for_printing_data(mephisto_data_browser.get_data_from_unit(unit)))
    # TODO can add review stuff if desired?