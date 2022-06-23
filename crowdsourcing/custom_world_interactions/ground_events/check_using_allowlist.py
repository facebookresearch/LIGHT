from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.examine_utils import run_examine_or_review, print_results
from mephisto.data_model.worker import Worker
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from collections import Counter

db = LocalMephistoDB()

mephisto_data_browser = MephistoDataBrowser(db=db)

task_names = ["objects-interaction-task-allowlist-events-1"]
units = []
for t in task_names:
    units.extend(mephisto_data_browser.get_units_for_task_name(t))

print(f"prev len: {len(units)}")
print(Counter([u.get_status() for u in units]))

task_workers = set()
for unit in units:
    worker = unit.get_assigned_agent().get_worker()
    task_workers.add(worker.worker_name)

qual_workers = set()

WORKER_ID_FILE = "/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/jing_allow_workers.txt"
with open(WORKER_ID_FILE, 'r') as f:
    worker_ids = f.read()
    worker_ids = worker_ids.split("\n")
    qual_workers.update(worker_ids)


WORKER_ID_FILE = "/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/collect_narrations/found_workers.txt"
with open(WORKER_ID_FILE, 'r') as f:
    worker_ids = f.read()
    worker_ids = worker_ids.split("\n")
    qual_workers.update(worker_ids)

exists = [w in qual_workers for w in task_workers]

print(Counter(exists))
print(f"num unique workers: {len(task_workers)}")