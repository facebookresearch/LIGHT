from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.data_model.worker import Worker


db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

DO_REVIEW = True

units = mephisto_data_browser.get_units_for_task_name(input("Input task name: "))

tasks_to_show = input("Tasks to see? (a)ll/(u)nreviewed: ")
if tasks_to_show in ["all", "a"]:
    DO_REVIEW = False
else:
    others = [u for u in units if u.get_status() != "completed"]
    units = [u for u in units if u.get_status() == "completed"]
    previous_work_by_worker = {}
    for unit in others:
        w_id = unit.worker_id
        if w_id not in previous_work_by_worker:
            previous_work_by_worker[w_id] = {
                "accepted": [],
                "soft_rejected": [],
                "rejected": [],
            }
        previous_work_by_worker[w_id][unit.get_status()].append(unit)
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


def format_action(action_obj):
    action_type = action_obj["action_type"]
    action_vals = action_obj["values"]
    if action_type in [
        "hit",
        "hug",
        "drop",
        "wield",
        "wear",
        "eat",
        "drink",
        "follow",
        "go",
    ]:
        return f"{action_type} {action_vals[0]}"
    if action_type == "give":
        return f"give {action_vals[0]} to {action_vals[1]}"
    if action_type == "steal":
        return f"steal {action_vals[0]} from {action_vals[1]}"
    if action_type == "use":
        return f"use {action_vals[0]} with {action_vals[1]}"
    if action_type == "get":
        if action_vals[2] == "0":
            return f"get {action_vals[0]}"
        return f"get {action_vals[0]} from {action_vals[1]}"
    if action_type == "put":
        split_word = "on" if action_vals[2] == "0" else "in"
        return f"put {action_vals[0]} {split_word} {action_vals[1]}"


def get_timeline_string(times, values):
    timeline_string = ""
    for idx, t in enumerate(times):
        timeline_string += f"   -- {t}\n" f"     -- {format_action(values[idx])}\n"
    return timeline_string


def format_for_printing_data(data):
    worker_name = Worker(db, data["worker_id"]).worker_name
    contents = data["data"]
    duration = contents["times"]["task_end"] - contents["times"]["task_start"]
    metadata_string = f"Worker: {worker_name}\nDuration: {int(duration)}\n"

    inputs = contents["inputs"]
    setting_split = " ".join(inputs["description"].split("\n"))
    inputs_string = (
        f"Character: {inputs['character']}\nPersona: {inputs['persona']}\n"
        f"Setting: {setting_split}\nGoal text: {inputs['goal']}\n"
    )

    outputs = contents["outputs"]["final_data"]
    output_string = (
        f"   Short term goal: {outputs['text_values'][0]}\n"
        f"   Mid term goal: {outputs['text_values'][1]}\n"
        f"   Long term goal: {outputs['text_values'][2]}\n"
        f"   Timeline:\n"
        f"{get_timeline_string(inputs['time'], outputs['actions'])}\n"
    )
    return f"-------------------\n{metadata_string}{inputs_string}{output_string}"


def get_prev_stats(worker_id):
    prev_work = previous_work_by_worker.get(worker_id)
    if prev_work is None:
        return "(First time worker!)"
    accepted_work = len(prev_work["accepted"])
    soft_rejected_work = len(prev_work["soft_rejected"])
    rejected_work = len(prev_work["rejected"])
    return f"({accepted_work} | {rejected_work + soft_rejected_work}({soft_rejected_work}) / {accepted_work + soft_rejected_work + rejected_work})"


disqualification_name = "can-write-light-quests-live-failed"  # None

units_by_worker = {}

for u in units:
    w_id = u.worker_id
    if w_id not in units_by_worker:
        units_by_worker[w_id] = []
    units_by_worker[w_id].append(u)

print(f"Need to review {len(units)} units by {len(units_by_worker)} different workers")

for w_id, w_units in units_by_worker.items():
    worker_name = Worker(db, w_id).worker_name
    apply_all_keep = None
    for idx, unit in enumerate(w_units):
        print(
            f"Reviewing for worker {worker_name}, ({idx+1}/{len(w_units)}), Previous {get_prev_stats(w_id)}"
        )
        print(format_for_printing_data(mephisto_data_browser.get_data_from_unit(unit)))
        if DO_REVIEW:
            if apply_all_keep is not None:
                keep = apply_all_keep
            else:
                keep = input(
                    "Do you want to accept this work? (a)ccept, (r)eject, (p)ass: "
                )
            if keep.lower() == "a":
                unit.get_assigned_agent().approve_work()
            elif keep.lower() == "r":
                if apply_all_keep is None:
                    reason = input("Why are you rejecting this work?")
                unit.get_assigned_agent().reject_work(reason)
            elif keep.lower() == "p":
                # General best practice is to accept borderline work and then disqualify
                # the worker from working on more of these tasks
                agent = unit.get_assigned_agent()
                agent.soft_reject_work()
                if apply_all_keep is None:
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
            if keep.lower() != keep:
                apply_all_keep = keep
