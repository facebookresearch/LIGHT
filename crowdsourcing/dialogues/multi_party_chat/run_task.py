#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import os
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import task_script
from mephisto.operations.hydra_config import build_default_task_config
from mephisto.abstractions.blueprints.parlai_chat.parlai_chat_blueprint import (
    SharedParlAITaskState,
)
from mephisto.data_model.qualification import QUAL_EXISTS, QUAL_NOT_EXIST
from mephisto.utils.qualifications import make_qualification_dict

from omegaconf import DictConfig
from dataclasses import dataclass, field
<<<<<<< HEAD
from light.constants import LIGHT_PATH
from light.graph.builders.one_room_builder import (
    OneRoomChatBuilder,
    OneRoomChatBuilderConfig,
)
=======
from light.constants import LIGHT_PATH, PARLAI_PATH
<<<<<<< HEAD
from light.graph.builders.one_room_builder import OneRoomChatBuilder, OneRoomChatBuilderConfig
>>>>>>> 4d43e4c1 (light path)
=======
from light.graph.builders.one_room_builder import (
    OneRoomChatBuilder,
    OneRoomChatBuilderConfig,
)
>>>>>>> 14ae0c63 (black)
from light.data_model.light_database import LIGHTDatabase
from light.registry.model_pool import ModelPool, ModelTypeName
from light.registry.models.starspace_model import MapStarspaceModelConfig


ALLOWLIST_QUALIFICATION = "multiparty-allow-prod-v2"
<<<<<<< HEAD
LIGHT_DB_PATH = os.path.join(LIGHT_PATH, "light/data_model/database.db")
=======
LIGHT_DB_PATH = os.path.join(PARLAI_PATH, "data/light/merged.db")
>>>>>>> 14ae0c63 (black)


@dataclass
class ParlAITaskConfig(build_default_task_config("dev")):  # type: ignore
    num_turns: int = field(
        default=8,
        metadata={"help": "Number of turns before a conversation is complete"},
    )
    turn_timeout: int = field(
        default=300,
        metadata={
            "help": "Maximum response time before kicking "
            "a worker out, default 300 seconds"
        },
    )
    max_acts_per_turn: int = field(
        default=5,
        metadata={
            "help": "Maximum number of messages "
            "a worker can send consecutively before"
            "someone else replies, default 5 messages"
        },
    )
    am_qualifiying_new_workers: bool = False
    allowlist_qualification: str = ALLOWLIST_QUALIFICATION


@task_script(config=ParlAITaskConfig)
def main(operator: "Operator", cfg: DictConfig) -> None:
    ldb = LIGHTDatabase(LIGHT_DB_PATH)

    pool = ModelPool()
<<<<<<< HEAD
<<<<<<< HEAD
    model_config = MapStarspaceModelConfig(
        opt_file=os.path.join(
            LIGHT_PATH, "light/registry/models/config/baseline_starspace.opt"
        )
    )
    pool.register_model(model_config, [ModelTypeName.CONNECTIONS])
=======
    model_config = MapStarspaceModelConfig(opt_file=os.path.join(LIGHT_PATH, "/light/registry/models/config/baseline_starspace.opt"))
=======
    model_config = MapStarspaceModelConfig(
        opt_file=os.path.join(
            LIGHT_PATH, "/light/registry/models/config/baseline_starspace.opt"
        )
    )
>>>>>>> 14ae0c63 (black)
    pool.register_model(model_config, [ModelTypeName.MAP_CONNECTIONS])
>>>>>>> 4d43e4c1 (light path)
    builder_config = OneRoomChatBuilderConfig(model_loader_config=model_config)

    world_opt = {
        "num_turns": cfg.num_turns,
        "turn_timeout": cfg.turn_timeout,
        "builder": OneRoomChatBuilder(ldb, pool, builder_config),
    }

    custom_bundle_path = cfg.mephisto.blueprint.get("custom_source_bundle", None)
    if custom_bundle_path is not None:
        assert os.path.exists(custom_bundle_path), (
            "Must build the custom bundle with `npm install; npm run dev` from within "
            f"the {cfg.task_dir}/webapp directory in order to demo a custom bundle "
        )
        world_opt["send_task_data"] = True

    if cfg.am_qualifiying_new_workers:
        use_qualifications = [
            make_qualification_dict(cfg.allowlist_qualification, QUAL_NOT_EXIST, None),
        ]
    else:
        use_qualifications = [
            make_qualification_dict(cfg.allowlist_qualification, QUAL_EXISTS, None),
        ]

    shared_state = SharedParlAITaskState(
        world_opt=world_opt,
        onboarding_world_opt=world_opt,
        qualifications=use_qualifications,
    )

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
