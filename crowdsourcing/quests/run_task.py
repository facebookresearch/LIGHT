#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import time
import shlex
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.operations.operator import Operator
from mephisto.operations.utils import get_root_dir
from parlai.core.params import ParlaiParser

import random

from light.data_model.light_database import LIGHTDatabase
from light.graph.builders.starspace_all import StarspaceBuilder
from light.graph.events.graph_events import (
    GoEvent,
    FollowEvent,
    HitEvent,
    HugEvent,
    GetObjectEvent,
    PutObjectInEvent,
    DropObjectEvent,
    StealObjectEvent,
    GiveObjectEvent,
    EquipObjectEvent,
    WearEvent,
    WieldEvent,
    RemoveObjectEvent,
    IngestEvent,
    EatEvent,
    DrinkEvent,
    LookEvent,
    InventoryEvent,
)

ACTION_LIST = [
    x.NAMES[0]
    for x in [
        GoEvent,
        FollowEvent,
        HitEvent,
        HugEvent,
        GetObjectEvent,
        PutObjectInEvent,
        DropObjectEvent,
        StealObjectEvent,
        GiveObjectEvent,
        WearEvent,
        WieldEvent,
        # RemoveObjectEvent,
        EatEvent,
        DrinkEvent,
    ]
]

USE_LOCAL = True
LAUNCH_LIVE = False

db = LocalMephistoDB()

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# ARG_STRING goes through shlex.split twice, hence be careful if these
# strings contain anything which needs quoting.
task_title = "Determining character motivations in a Fantasy Text World"
task_description = (
    "In this task, you'll be given a scenario and a character. You'll write a few sentences describing "
    "why the character might be motivated to take the given action, and give possible previous and next actions."
)

requester_name = (
    "test_requester"
    if USE_LOCAL
    else ("NoahTurk1027" if LAUNCH_LIVE else "NoahTurk1027_sandbox")
)
architect_type = "local" if USE_LOCAL else "heroku"

# The first time round, need to call the following here.
# TODO make this more user friendly than needing to uncomment script lines
# db.new_requester("<some_email_address>", "mock")
# db.new_requester("<your_email_address>_sandbox", "mturk_sandbox")

if LAUNCH_LIVE:
    USE_LOCAL = False
    input(
        f"You are about to launch tasks live with requester {requester_name},"
        " is this what you want? Press enter to continue"
    )

assert (
    USE_LOCAL or LAUNCH_LIVE or requester_name.endswith("_sandbox")
), "Should use a sandbox for testing"

# The first time using mturk, need to call the following here
# requester.register()

ARG_STRING = (
    "--blueprint-type static_react_task "
    f"--architect-type {architect_type} "
    f"--requester-name {requester_name} "
    f'--task-title "\\"{task_title}\\"" '
    f'--task-description "\\"{task_description}\\"" '
    "--task-reward 2.75 "
    "--task-tags creative,writing,fantasy,text,motivations "
    f'--task-source "{TASK_DIRECTORY}/webapp/build/bundle.js" '
    f"--units-per-assignment 1 "
    f"--task-name light-quest-pilot-test "
    f"--onboarding-qualification can-write-light-quests-sandbox "
)

REVERSE_TIMES = [
    "5 minutes ago",
    "10 minutes ago",
    "15 minutes ago",
    "30 minutes ago",
    "1 hour ago",
    "2 hours ago",
    "4 hours ago",
    "8 hours ago",
]

FORWARD_TIMES = [
    "5 minutes from now",
    "10 minutes from now",
    "15 minutes from now",
    "30 minutes from now",
    "1 hour from now",
    "2 hours from now",
    "4 hours from now",
    "8 hours from now",
]


def get_random_times():
    times = []
    rev_idx = random.randint(0, 1)
    times.append(REVERSE_TIMES[rev_idx])
    rev_idx += random.randint(1, 3)
    times.append(REVERSE_TIMES[rev_idx])
    rev_idx += random.randint(1, 3)
    times.append(REVERSE_TIMES[rev_idx])
    times.reverse()
    fwd_idx = random.randint(0, 1)
    times.append(FORWARD_TIMES[fwd_idx])
    fwd_idx += random.randint(1, 3)
    times.append(FORWARD_TIMES[fwd_idx])
    fwd_idx += random.randint(1, 3)
    times.append(FORWARD_TIMES[fwd_idx])
    return times


def construct_tasks(num_tasks):
    tasks = []
    parser = ParlaiParser()
    StarspaceBuilder.add_parser_arguments(parser)
    opt, _unknown = parser.parse_and_process_known_args()
    opt["map_size"] = 1
    opt["light_db_file"] = "/Users/jju/ParlAI/data/light/database3.db"
    opt["light_model_root"] = "/Users/jju/Desktop/LIGHT/LIGHT_models/"
    opt["hybridity_prob"] = 1
    opt["suggestion_type"] = "hybrid"
    ldb = LIGHTDatabase(opt["light_db_file"])
    builder = StarspaceBuilder(ldb, opt=opt)
    random.seed(88)
    while len(tasks) < num_tasks:
        g, world = builder.get_graph()
        while len(world.oo_graph.agents) == 0:
            print("no agents in room")
            g, world = builder.get_graph()
        possible_agents = list(world.oo_graph.agents.values())
        random.shuffle(possible_agents)
        for character in possible_agents:
            actions = world.get_possible_actions(
                character.node_id, use_actions=ACTION_LIST
            )
            if len(actions) < 3:
                print("less than 3 actions")
                continue
            use_action = random.choice(actions)
            look_event = LookEvent(character)
            look_event.execute(world)
            room_desc = look_event.view_as(character)
            room_desc += (
                f"\nYou are {world.view.get_inventory_text_for(character.node_id)}"
            )
            if "torture" in room_desc.lower():
                continue
            tasks.append(
                {
                    "character": character.get_prefix_view(),
                    "persona": character.persona,
                    "description": room_desc,
                    "goal": use_action,
                    "char_id": character.db_id,
                    "room_id": character.get_room().db_id,
                    "time": get_random_times(),
                }
            )
            if len(tasks) == num_tasks:
                break
    return tasks


extra_args = {"static_task_data": construct_tasks(15)}


operator = Operator(db)

try:
    operator.parse_and_launch_run(shlex.split(ARG_STRING), extra_args=extra_args)
    print("task run supposedly launched?")
    print(operator.get_running_task_runs())
    while len(operator.get_running_task_runs()) > 0:
        print(f"Operator running {operator.get_running_task_runs()}")
        time.sleep(30)
except Exception as e:
    import traceback

    traceback.print_exc()
except (KeyboardInterrupt, SystemExit) as e:
    pass
finally:
    operator.shutdown()
