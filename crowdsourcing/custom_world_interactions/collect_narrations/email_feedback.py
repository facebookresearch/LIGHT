#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Simple script to send an email to a specific worker with feedback about
the task. Allows optional revoking of the task qualification, awaiting a
response from the worker.
"""

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.providers.mturk.mturk_utils import email_worker


# TODO hydrize? Polish?
def main():
    requester_name = input("Requester: ")
    db = LocalMephistoDB()
    req = db.find_requesters(requester_name=requester_name)[0]
    client = req._get_client(req._requester_name)

    worker_id = input("Worker id: ")
    email_title = input("Email title: ")
    if email_title == "":
        email_title = "Annotate an Interaction task feedback"

    email = ""
    next_email_line = " "
    while next_email_line != "":
        next_email_line = input("Enter email body line (empty line to finish): ")
        email += next_email_line + "\n"

    email_worker(client, worker_id, email_title, email)

    if not input("Remove qual too? (y)/n").lower().startswith('n'):
        qual_name = input("Qual name: ")
        worker = db.find_workers(worker_name=worker_id)[0]
        worker.revoke_qualification(qual_name)

if __name__ == '__main__':
    main()