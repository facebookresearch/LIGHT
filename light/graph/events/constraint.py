#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod


class Constraint(ABC):
    """Base abstract class to describe every constraint necessary to be met in order to execute an use event"""

    def __init__(self, target_nodes, constraint_params=None):
        self.target_nodes = target_nodes
        self.constraint_params = constraint_params

    def satisfy(self, world):
        pass


class IsHoldingConstraint(Constraint):
    """Constraint which chexks if actor is holding the useable item"""

    def satisfy(self, world):
        if self.constraint_params["complement"] == "used_item":
            return True

        target = self.target_nodes[0]
        actor = self.constraint_params["actor"]
        return target.get_container() == actor


class UsedWithItemConstraint(Constraint):
    """Constraint which checks if the useable item is used with the given object"""

    def satisfy(self, world):
        item = self.constraint_params["item"]
        return item == self.target_nodes[1].name


class UsedWithAgentConstraint(Constraint):
    """Constraint which checks if the target is an agent"""

    def satisfy(self, world):
        return self.target_nodes[1].agent
