# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import hashlib

from mephisto.operations.operator import Operator
from mephisto.tools.scripts import (
    build_custom_bundle,
    task_script,
)
from mephisto.operations.hydra_config import build_default_task_config
from mephisto.abstractions.blueprints.remote_procedure.remote_procedure_blueprint import (
    SharedRemoteProcedureTaskState,
    RemoteProcedureAgentState,
)

from omegaconf import DictConfig, MISSING
from typing import List, Any, Dict
from dataclasses import dataclass, field

MAX_INCORRECT = 3


def get_salted_hash(in_string, salt):
    """Return a hash string for the given string using sha-256"""
    salted_string = in_string + salt + in_string
    res = hashlib.sha256(salted_string.encode("utf-8")).hexdigest()[:20]
    return res


@dataclass
class BuilderTaskConfig(build_default_task_config("local")):  # type: ignore
    game_url: str = field(
        default=MISSING,
        metadata={"help": "Complete URL to use for the version of the game running"},
    )


def validate_unit(unit):
    agent = unit.get_assigned_agent()
    if agent is None:
        return

    data = agent.state.get_data()

    if data["final_submission"] is None:
        return

    final_data = data["final_submission"]["data"]

    # TODO validate
    return


@task_script(config=BuilderTaskConfig)
def main(operator: Operator, cfg: DictConfig) -> None:
    tasks: List[Dict[str, Any]] = [{"url": cfg.game_url}] * cfg.num_tasks

    def validate_onboarding(onboarding_data):
        # TODO implement once we have an onboarding
        return True

    # TODO initialize agent as necessary for the below

    def suggest_room(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ):
        # Use add_room_description and add_room_backstory to fill these
        # from a title alone
        room_graph = args["room_graph"]
        pass

    def suggest_room_contents(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ):
        room_graph = args["room_graph"]
        target_room = args["target_room"]
        # Use `add_object` and `add_character` to generate a list of suggestions for
        # objects and characters
        pass

    def suggest_character_contents(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ):
        room_graph = args["room_graph"]
        target_room = args["target_room"]
        # Use `add_character_wearing`, `add_character_wielding`, `add_character_carrying`
        # to create three lists of suggestions
        pass

    def suggest_object_contents(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ):
        room_graph = args["room_graph"]
        target_room = args["target_room"]
        # Use `add_object_contains` to create a list of object suggestions
        pass

    def fill_object(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ):
        # Fill the attributes and contents of object_id with `add_all_static_attributes`
        # and `add_all_object_attributes`
        room_graph = args["room_graph"]
        room_graph = args["object_id"]
        pass

    def fill_character(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ):
        # Fill the attributes and contents of character_id with `add_all_character_attributes`
        room_graph = args["room_graph"]
        room_graph = args["character_id"]
        pass

    def fill_room(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ):
        # Use add_object, add_character, fill_object, and fill_character to fill out this room
        room_graph = args["room_graph"]
        pass

    function_registry = {
        "suggest_room_contents": suggest_room_contents,
        "suggest_character_contents": suggest_character_contents,
        "suggest_object_contents": suggest_object_contents,
        "suggest_room": suggest_room,
        "fill_object": fill_object,
        "fill_character": fill_character,
        "fill_room": fill_room,
    }

    shared_state = SharedRemoteProcedureTaskState(
        static_task_data=tasks,
        function_registry=function_registry,
        validate_onboarding=validate_onboarding,
        on_unit_submitted=validate_unit,
    )

    task_dir = cfg.task_dir
    build_custom_bundle(task_dir)

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
