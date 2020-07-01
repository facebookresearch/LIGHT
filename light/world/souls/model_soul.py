#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.world.souls.soul import Soul

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.graph.world.world import World
    from light.graph.events.base import GraphEvent


class ModelSoul(Soul):
    """
    A ModelSoul is responsible for passing it's observations back to
    a model that decides what to do. This class will likely have utility
    methods for loading shared models and some shared behavior between
    classes, for now is a stub.
    """

    pass
