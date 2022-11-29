from mephisto.abstractions.databases.local_database import LocalMephistoDB
import json
import os
import time

db = LocalMephistoDB()

BONUS_LIST = [
    ('A15XDLZ944Q0SH' , 0.35 , "Continued high-quality examples. Thanks for the effort in these interactions!"),
    ('A35D0B238HFOCM' , 0.15 , "Continued high-quality examples and in bulk. Thanks for all your contributions thus far"),
    ('A2ATBS6XTIZE89', 0.25 , "Continued high quality descriptions and interactions. Thanks for these!"),
    ('A2JXPT39AWRES7', 0.10 , "Continued generally high-quality and interesting descriptions. Thanks for these!"),
    ('AV4584AQEQAEN', 0.25 , "Continued high-quality creative descriptions on average. Thanks for these!"),
    ('A22VGT2F28LTWC', 0.40 , "These remain some of my favorite interactions. Thank you for your continued work here."),
    ('A1RF95TSDZDJLL', 0.15 , "For continued attention to detail on these, with high-quality interactions Thanks for your work here."),
    ('A19NGUFGC7KIGW' , 0.25 , "Continued high quality descriptions and interactions. Thanks for the creative work here!"),
    ('A17C8CUROFU495' , 0.18 , "Continued high quality and interesting interactions on average. Thanks for these!"),
    ('ABHGKLWWU61KF', 0.10 , "High-quality and interesting descriptions, often with witty humor. Thanks for these!"),
    ('AR9AU5FY1S3RO', 0.10 , "High-quality and interesting descriptions, often with witty humor. Thanks for these!"),
    ('A2FYFCD16Z3PCC', 0.15 , "High-quality work and adhering to the instructions closely. Thanks for these!"),
]

LAST_BONUS_FILE = "last_bonus.json"
if os.path.exists(LAST_BONUS_FILE):
    with open(LAST_BONUS_FILE, 'r') as bonus_file:
        last_bonus = json.load(bonus_file)['last_time']
else:
    last_bonus = 0.0

task = db.find_tasks(task_name="objects-interaction-narration-task-full-collection-2")
all_units = db.find_units(task_id=task[0].db_id)
bonus_time = time.time()
all_units = [u for u in all_units if u.get_assigned_agent() is not None]
units_by_worker = {}
for u in all_units:
    agent = u.get_assigned_agent()
    if agent.state.metadata.task_end is not None and agent.state.metadata.task_end < last_bonus:
        continue
    worker_db_id = agent.get_worker().db_id
    if worker_db_id not in units_by_worker:
        units_by_worker[worker_db_id] = []
    units_by_worker[worker_db_id].append(u)

def get_worker_and_units(worker_id):
    worker = db.find_workers(worker_name=worker_id)[0]
    my_units = units_by_worker[worker.db_id]
    return worker, my_units

for w_name, amount, reason in BONUS_LIST:
    w, units = get_worker_and_units(w_name)
    input(f"Bonus of {amount} to {w_name} for {len(units)} units? Total: ${amount*len(units)}")
    for u in units:
        try:
            w.bonus_worker(amount, reason=f"Additional quality pay. Reason: {reason}", unit=u)
        except Exception as e:
            print(f"Failed a bonus: {e}")
    print(f"Sent bonus of {amount} to {w_name}")

with open(LAST_BONUS_FILE, "w+") as bonus_file:
    json.dump({'last_time': bonus_time}, bonus_file)