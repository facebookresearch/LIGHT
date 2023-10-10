#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from dataclasses import dataclass, field
from typing import List, Any

import hydra
from mephisto.operations.hydra_config import register_script_config
from omegaconf import DictConfig
from parlai.crowdsourcing.utils.mturk import MTurkRunScriptConfig

from parlai_internal.projects.light.lightqa.crowdsourcing.acute_eval.util import (
    TASK_DIRECTORY,
)
from parlai_internal.projects.light.lightqa.crowdsourcing.acute_eval.run import (
    LightFastAcuteExecutor,
)
from parlai_internal.projects.light.lightqa.crowdsourcing.acute_eval.acute_eval_blueprint import (
    LIGHTQA_FAST_BLUEPRINT_TYPE,
)

from parlai_internal.projects.light.lightqa.lightqa.crowdsourcing.acute_eval.generate_pairings import (
    generate_pairings,
)

"""
Read parlai/crowdsourcing/README.md to learn how to launch
crowdsourcing tasks with this script.
"""

RUN_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class DialogLightFastAcuteExecutor(LightFastAcuteExecutor):
    def _load_pairings_file(self):
        # Generate pairings for Light-dialog-wild.
        self.pairings_filepath = os.path.join(
            self.fast_acute_args.root_dir, "pairings_files", "pairings_model.jsonl"
        )
        if os.path.exists(self.pairings_filepath):
            usr_decision = input(
                f"Pairings file {self.pairings_filepath} exists. Answer with <y> to regenerate: "
            )

        if not os.path.exists(self.pairings_filepath) or usr_decision == "y":
            print(f"Generate pairings at {self.pairings_filepath}.")
            generate_pairings(
                input_dir="/checkpoint/ladolphs/projects/light/lightqa/lightqa/crowdsource/",
                output_file=self.pairings_filepath,
            )

        self._load_models()


defaults = [
    {"mephisto/blueprint": LIGHTQA_FAST_BLUEPRINT_TYPE},
    {"mephisto/architect": "local"},
    {"mephisto/provider": "mock"},
    {"conf": "conf_fast"},
]


@dataclass
class LightQAScriptConfig(MTurkRunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY
    run_dir: str = RUN_DIRECTORY
    monitoring_log_rate: int = field(
        default=30,
        metadata={
            "help": "Frequency in seconds of logging the monitoring of the crowdsourcing task"
        },
    )


register_script_config(name="lightqa_scriptconfig", module=LightQAScriptConfig)


@hydra.main(config_path="hydra_configs", config_name="lightqa_scriptconfig")
def main(cfg: DictConfig) -> None:
    runner = DialogLightFastAcuteExecutor(cfg)

    runner.run_acute_eval()
    runner.analyze_results()


if __name__ == "__main__":
    main()
