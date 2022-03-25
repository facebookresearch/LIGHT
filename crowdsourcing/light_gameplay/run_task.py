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


def get_salted_hash(in_string, salt):
    """Return a hash string for the given string using sha-256"""
    salted_string = in_string + salt + in_string
    return hashlib.sha256(salted_string.encode("utf-8")).hexdigest()[:20]


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
    )

    task_dir = cfg.task_dir
    build_custom_bundle(task_dir)

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
