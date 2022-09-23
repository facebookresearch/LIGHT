from mephisto.abstractions.databases.local_database import LocalMephistoDB

db = LocalMephistoDB()

BONUS_LIST = [
    ('', 0.0, ""),
]

task = db.find_tasks(task_name="objects-interaction-narration-task-full-collection")
all_units = db.find_units(task_id=task[0].db_id)
all_units = [u for u in all_units if u.get_assigned_agent() is not None]
units_by_worker = {}
for u in all_units:
    worker_db_id = u.get_assigned_agent().get_worker().db_id
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

