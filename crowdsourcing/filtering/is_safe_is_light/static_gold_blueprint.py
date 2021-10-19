#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.assignment import InitializationData
from dataclasses import dataclass, field
from omegaconf import MISSING
from mephisto.abstractions.blueprints.mixins.use_gold_unit import (
    UseGoldUnit,
    UseGoldUnitArgs,
    GoldUnitSharedState,
)
from mephisto.abstractions.blueprints.static_react_task.static_react_blueprint import (
    StaticReactBlueprint,
    StaticReactBlueprintArgs,
)
from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    SharedStaticTaskState,
)
from mephisto.operations.registry import register_mephisto_abstraction


import os
import time
import csv

from typing import ClassVar, List, Type, Any, Dict, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.blueprint import AgentState, TaskRunner, TaskBuilder
    from mephisto.data_model.assignment import Assignment
    from argparse import _ArgumentGroup as ArgumentGroup
    from mephisto.abstractions.blueprint import BlueprintArgs

BLUEPRINT_TYPE = "static_react_with_gold"


@dataclass
class StaticGoldBlueprintArgs(UseGoldUnitArgs, StaticReactBlueprintArgs):
    _blueprint_type: str = BLUEPRINT_TYPE


class StaticGoldSharedState(GoldUnitSharedState, SharedStaticTaskState):
    pass


@register_mephisto_abstraction()
class StaticGoldBlueprint(UseGoldUnit, StaticReactBlueprint):
    """
    Blueprint for a task that runs off of a built react javascript
    bundle, with gold units
    """

    ArgsClass = StaticGoldBlueprintArgs
    SharedStateClass = StaticGoldSharedState
    BLUEPRINT_TYPE = BLUEPRINT_TYPE
