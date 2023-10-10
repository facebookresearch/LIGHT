#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid
import os
from pytz import timezone
from datetime import datetime
import numpy as np

"""
Parallel data generation for summaryqa.
"""

HOURS = 2
GPUS = 1

NOW = datetime.now(timezone("Europe/Zurich")).strftime("%a_%b_%d_%H%M")

here_path = os.path.realpath(__file__).replace(".py", "")
projects = here_path[here_path.find("/projects") :].strip("/")
projects_dir = "/".join(projects.split("/")[:-1])

SWEEP_NAME = projects.split("/")[-1] + "_" + NOW
SAVEROOT = os.path.join("/checkpoint/ladolphs", projects_dir)
PARLAI_HOME_DIR = "/private/home/ladolphs/code/ParlAI"
name_keys = {}

DATATYPE = "train"
TASK = "light_dialog_wild"
SAVE_PATH = "/checkpoint/ladolphs/projects/light/lightqa/data/summaryqa2/"

num_episodes = {
    "light_dialog_wild:train": 41131,
    "light_dialog_wild:valid": 500,
    "light_dialog_wild:test": 1000,
}[f"{TASK}:{DATATYPE}"]

max_episodes_per_task = 300
start_idxs = np.arange(0, num_episodes, max_episodes_per_task)
end_idxs = [min(idx + max_episodes_per_task, num_episodes) for idx in start_idxs]

idx_grid = [
    f"{start} --end-episode-idx {end}" for start, end in zip(start_idxs, end_idxs)
]

grid = {
    "-t": [TASK],
    "-dt": [DATATYPE],
    "--save-path": [SAVE_PATH],
    "--start-episode-idx": idx_grid,
}

if __name__ == "__main__":
    run_grid(
        grid,
        {},
        SWEEP_NAME,
        saveroot=os.path.join(SAVEROOT, SWEEP_NAME),
        PARLAI_PATH=PARLAI_HOME_DIR,
        prefix="python parlai_internal/projects/light/lightqa/data/generate_summaryqa.py",
        create_model_file=False,
        include_job_id=False,
        gpus=GPUS,
        data_parallel=True,
        copy_env=False,
        nodes=1,
        cpus=10,
        partition="learnfair",
        # partition='devlab',
        jobtime="{}:00:00".format(HOURS),
        hashname=True,
        requeue=True,
    )
