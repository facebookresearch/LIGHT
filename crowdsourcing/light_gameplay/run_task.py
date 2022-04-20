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
    print(f"Salting {in_string} with {salt}")
    salted_string = in_string + salt + in_string
    res = hashlib.sha256(salted_string.encode("utf-8")).hexdigest()[:20]
    print(f"Got res {res}")
    return res


@dataclass
class ParlAITaskConfig(build_default_task_config("local")):  # type: ignore
    game_url: str = field(
        default=MISSING,
        metadata={"help": "Complete URL to use for the version of the game running"},
    )
    preauth_secret: str = field(
        default=MISSING,
        metadata={
            "help": "Preauth secret key to use with hashes. Should agree with the current"
            "preauth secret on the LIGHT game site."
        },
    )


@task_script(config=ParlAITaskConfig)
def main(operator: Operator, cfg: DictConfig) -> None:
    tasks: List[Dict[str, Any]] = [{"url": cfg.game_url}] * cfg.num_tasks
    preauth_secret = cfg.preauth_secret

    def worker_did_enough_correct(onboarding_data):
        incorrect_count = 0
        questions = onboarding_data["final_submission"]
        for question in questions:
            answers = question["answers"]
            correct_ids = set(a["id"] for a in answers if a["isCorrect"])
            selected_answers = question["selectedAnswers"]
            selected_ids = set(a["id"] for a in selected_answers)
            wrong_answers = len(correct_ids.symmetric_difference(selected_ids))
            incorrect_count += wrong_answers
        return incorrect_count < MAX_INCORRECT

    def get_auth_token(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ) -> Dict[str, Any]:
        """Get an auth token for the given worker"""
        worker_id = args["worker_id"]
        agent_id = args["agent_id"]
        key_string = f"{worker_id}-{agent_id}"
        return {
            "auth_token": get_salted_hash(key_string, preauth_secret),
        }

    function_registry = {
        "get_auth_token": get_auth_token,
    }

    shared_state = SharedRemoteProcedureTaskState(
        static_task_data=tasks,
        function_registry=function_registry,
        validate_onboarding=worker_did_enough_correct,
    )

    task_dir = cfg.task_dir
    build_custom_bundle(task_dir)

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
