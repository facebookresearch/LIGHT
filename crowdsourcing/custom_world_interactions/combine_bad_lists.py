##!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import random
import shutil
import subprocess
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import load_db_and_process_config
from mephisto.abstractions.blueprint import BlueprintArgs
from mephisto.abstractions.blueprints.static_react_task.static_react_blueprint import (
    BLUEPRINT_TYPE_STATIC_REACT as BLUEPRINT_TYPE,
)
from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    SharedStaticTaskState,
)
from light.data_model.light_database import LIGHTDatabase
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.data_model.worker import Worker
from mephisto.data_model.unit import Unit

import hydra
import json
import random
from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import List, Any

from mephisto.utils.qualifications import make_qualification_dict
from mephisto.data_model.qualification import QUAL_EXISTS
from parlai_internal.crowdsourcing.projects.reverse_persona.utils.dataloading_utils import (
    get_block_list,
)
from mephisto.abstractions.providers.mturk.utils.script_utils import (
    direct_soft_block_mturk_workers,
)

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LIGHT_DB_PATH = "~/ParlAI/data/light/environment/db/d3/database3.db"

ALL_BAD_USER_FILES = [
    "/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/ground_events/users_who_didnt_get_it.txt",
    "/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/collect_narrations/users_who_didnt_get_it.txt",
    "/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/ground_attributes/users_who_didnt_get_it.txt",
    "/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/ground_constraints/users_who_didnt_get_it.txt"
    ]

# for fname in ALL_BAD_USER_FILES:
#     get_block_list(fname)

all_bad_users = get_block_list(ALL_BAD_USER_FILES)

with open("/checkpoint/light/common_sense/all_bad_users.txt", 'w') as f:
    # for w in all_bad_users:
    #     f.write(w + '\n')
    f.write("\n".join(all_bad_users))