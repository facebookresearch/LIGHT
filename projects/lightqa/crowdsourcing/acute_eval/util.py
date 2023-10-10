#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import List, Optional
from parlai_internal.crowdsourcing.block_list import WORKER_BLOCK_LIST

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


def download_parlai_worker_blocklist(file_name: Optional[str] = None) -> str:
    """
    Download the standard ParlAI blocklist for MTurk.

    Return the download path.
    """
    if not file_name:
        file_name = f"{TASK_DIRECTORY}/block_list.txt"
    os.makedirs("/".join(file_name.split("/")[:-1]), exist_ok=True)
    with open(file_name, "w") as f:
        f.write("\n".join(WORKER_BLOCK_LIST))
    return file_name
