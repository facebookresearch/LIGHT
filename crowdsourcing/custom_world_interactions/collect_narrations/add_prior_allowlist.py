#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.data_model.worker import Worker
from mephisto.data_model.unit import Unit
from collections import Counter
from tqdm import tqdm

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

# from mephisto.utils.qualifications import find_or_create_qualification

# find_or_create_qualification(db, "collect_narrations_task_allow")

DO_REVIEW = True

WORKER_ID_FILE = "/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/jing_allow_workers.txt"
with open(WORKER_ID_FILE, 'r') as f:
    worker_ids = f.read()
    worker_ids = worker_ids.split("\n")

# for worker_id in worker_ids:
     
#     worker.grant_qualification("collect_narrations_task_allow")
#     print(k)

good_workers = set(worker_ids)

all_workers = db.find_workers()
print(f"len workers: {len(all_workers)}")

# for w in all_workers:
#     name = w.worker_name
#     if name in good_workers:
#         print("COOL")
#         w.grant_qualification("collect_narrations_task_allow")
qual_vals = []
for w in all_workers:
    qual_vals.append(w.get_granted_qualification("collect_narrations_task_allow") is not None)

print(Counter(qual_vals))

# """
# Directly assign the soft blocking MTurk qualification that Mephisto
# associates with soft_block_qual_name to all of the MTurk worker ids
# in worker_list. If requester_name is not provided, it will use the
# most recently registered mturk requester in the database.
# """
# reqs = db.find_requesters(requester_name="alexgurung", provider_type="mturk")
# requester = reqs[-1]

# from mephisto.abstractions.providers.mturk.mturk_utils import give_worker_qualification
# mturk_client = requester._get_client(requester._requester_name)
# for worker_id in tqdm(worker_ids):
#     try:
#         give_worker_qualification(
#             mturk_client, worker_id, "collect_narrations_task_allow", value=1
#         )
#     except Exception as e:
#         print(
#             f'Failed to give worker with ID: "{worker_id}" qualification with error: {e}. Skipping.'
#         )
