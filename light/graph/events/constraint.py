#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import abstractmethod


class Constraint:
    def __init__(self, target_nodes, constraint_params=None):
        self.target_nodes = target_nodes
        self.constraint_params = constraint_params

    @abstractmethod
    def satisfy(self, world):
        pass


class IsHoldingConstraint(Constraint):
    def satisfy(self, world):
        target = self.target_nodes[0]
        actor = self.constraint_params["actor"]

        # Check if actor is holding the useable item.
        return target.get_container() == actor


class UsedWithItemConstraint(Constraint):
    def satisfy(self, world):
        item = self.constraint_params["item"]

        # Check if the useable item is used with the given object.
        return item == self.target_nodes[1].name


class UsedWithAgentConstraint(Constraint):
    def satisfy(self, world):
        # Check if the target is an agent
        return self.target_nodes[1].agent
