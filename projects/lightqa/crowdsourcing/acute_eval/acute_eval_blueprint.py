#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from dataclasses import dataclass, field
from typing import ClassVar, Type, TYPE_CHECKING, Dict, Any

from mephisto.operations.registry import register_mephisto_abstraction
from parlai.crowdsourcing.tasks.acute_eval.fast_acute_blueprint import (
    FastAcuteBlueprint,
    FastAcuteBlueprintArgs,
)
from parlai_internal.projects.light.lightqa.crowdsourcing.acute_eval.acute_eval_builder import (
    LightQAAcuteBuilder,
)

if TYPE_CHECKING:
    from mephisto.abstractions.blueprint import TaskBuilder

LIGHTQA_FAST_BLUEPRINT_TYPE = "lightqa_fast_acute_eval"


@dataclass
class LightQAFastAcuteBlueprintArgs(FastAcuteBlueprintArgs):
    _blueprint_type: str = LIGHTQA_FAST_BLUEPRINT_TYPE
    additional_task_description_prefix: str = field(
        default="Thats the default",
        metadata={
            "help": "Additional text to show on the left pane in the beginning of the text."
        },
    )
    dialogues_input_dir: str = field(
        default="",
        metadata={"help": "Input directory from which to load the dialogue files."},
    )
    add_history: bool = field(
        default=False,
        metadata={"help": "Add a history to the chat."},
    )
    add_knowledge: bool = field(
        default=True,
        metadata={"help": "Add knowledge to the chat."},
    )


@register_mephisto_abstraction()
class LightQAFastAcuteBlueprint(FastAcuteBlueprint):
    """
    Subclass of FastAcuteEvalBlueprint with params for fast ACUTE runs.
    """

    TaskBuilderClass: ClassVar[Type["TaskBuilder"]] = LightQAAcuteBuilder
    ArgsClass = LightQAFastAcuteBlueprintArgs
    BLUEPRINT_TYPE = LIGHTQA_FAST_BLUEPRINT_TYPE

    def get_frontend_args(self) -> Dict[str, Any]:
        """
        Specifies what options within a task_config should be forwarded to the client
        for use by the task's frontend.
        """
        return {
            **super().get_frontend_args(),
            **{
                "additional_task_description_prefix": self.args.blueprint.additional_task_description_prefix,
            },
        }
