#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import datetime
import json
from dataclasses import dataclass, field
from typing import List, Any, Dict, Optional

import hydra
from mephisto.operations.operator import Operator
from mephisto.operations.hydra_config import register_script_config
from mephisto.tools.scripts import load_db_and_process_config
from omegaconf import DictConfig
from parlai.crowdsourcing.utils.mturk import MTurkRunScriptConfig
from parlai.crowdsourcing.tasks.acute_eval.fast_eval import (
    ACUTE_EVAL_TYPES,
    FastAcuteExecutor,
)

from parlai_internal.projects.light.lightqa.crowdsourcing.acute_eval.util import (
    TASK_DIRECTORY,
    download_parlai_worker_blocklist,
)
from parlai_internal.projects.light.lightqa.crowdsourcing.acute_eval.acute_eval_blueprint import (
    LIGHTQA_FAST_BLUEPRINT_TYPE,
)
from parlai_internal.crowdsourcing.block_list import ALLOW_LIST_QUAL_ID
from parlai_internal.projects.light.lightqa.crowdsourcing.acute_eval.acute_eval_blueprint import (
    LightQAFastAcuteBlueprint,
)

"""
Read parlai/crowdsourcing/README.md to learn how to launch
crowdsourcing tasks with this script.
"""

ACUTE_EVAL_TYPES = {
    **ACUTE_EVAL_TYPES,
    **{
        "knowledgeable": {
            "question": "If you had to say that one speaker is more knowledgeable and one is more ignorant, who is more knowledgeable?",
            "s1_choice": "<Speaker 1> is more knowledgeable",
            "s2_choice": "<Speaker 2> is more knowledgeable",
        }
    },
}


class LightFastAcuteExecutor(FastAcuteExecutor):
    def __init__(self, args: DictConfig):
        self.args = args
        self.fast_acute_args = self.args.mephisto.blueprint

        # models + task
        self.task: str = self.fast_acute_args.task
        self.pairings_filepath = None

        # question config for running ACUTE
        self.question_config: Dict[str, str] = ACUTE_EVAL_TYPES[
            self.fast_acute_args.acute_eval_type
        ]

        self.run_id = self.args.mephisto.task.task_name

        if args.mturk.worker_blocklist_paths == "parlai_standard":
            args.mturk.worker_blocklist_paths = download_parlai_worker_blocklist()

    def _load_pairings_file(self):
        """
        Load pairings file.

        Need to set:
        - self.pairings_filepath
        - self.models
        - self.combos
        """
        self.pairings_filepath = os.path.join(
            self.fast_acute_args.root_dir, "pairings_files", "pairings.jsonl"
        )
        self._load_models()

    def _load_models(self):
        with open(self.pairings_filepath, "r") as f:
            convs = [json.loads(line) for line in f]
        self.models = list(
            set([model for conv in convs for model in conv["speakers_to_eval"]])
        )
        combos = list(
            set([",".join(sorted(conv["speakers_to_eval"])) for conv in convs])
        )
        self.combos = [tuple(combo.split(",")) for combo in combos]
        self.models.sort()

    def run_acute_eval(self):
        """
        Run ACUTE Eval.
        """
        self.set_up_acute_eval()
        db, cfg = load_db_and_process_config(self.args)
        print(f"*** RUN ID: {cfg.mephisto.task.task_name} ***")
        operator = Operator(db)
        shared_state = LightQAFastAcuteBlueprint.SharedStateClass()
        shared_state.mturk_specific_qualifications = [
            {
                "QualificationTypeId": ALLOW_LIST_QUAL_ID,
                "Comparator": "Exists",
                "ActionsGuarded": "DiscoverPreviewAndAccept",
            },
        ]
        operator.validate_and_run_config(
            run_config=cfg.mephisto, shared_state=shared_state
        )
        operator.wait_for_runs_then_shutdown(
            skip_input=True, log_rate=cfg.monitoring_log_rate
        )


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
    monitoring_log_rate: int = field(
        default=30,
        metadata={
            "help": "Frequency in seconds of logging the monitoring of the crowdsourcing task"
        },
    )


register_script_config(name="lightqa_scriptconfig", module=LightQAScriptConfig)


@hydra.main(config_path="hydra_configs", config_name="lightqa_scriptconfig")
def main(cfg: DictConfig) -> None:

    runner = LightFastAcuteExecutor(cfg)
    runner.run_acute_eval()
    runner.analyze_results()


if __name__ == "__main__":
    main()
