#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
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
    """Checks if actor is holding the useable item"""

    def satisfy(self, world):
        if self.constraint_params["complement"] == "used_item":
            return True

        target = self.target_nodes[0]
        actor = self.constraint_params["actor"]
        return target.get_container() == actor


class UsedWithItemConstraint(Constraint):
    """Checks if the useable item is used with the given object"""

    def satisfy(self, world):
        item = self.constraint_params["item"]
        return item == self.target_nodes[1].name


class UsedWithAgentConstraint(Constraint):
    """Checks if the target is an agent"""

    def satisfy(self, world):
        return self.target_nodes[1].agent


class InRoomConstraint(Constraint):
    """Checks if the event is happening in a specific room"""

    def satisfy(self, world):
        room_name = self.constraint_params["actor"].get_room().get_names()[0]
        return room_name == self.constraint_params["room_name"]


class AttributeCompareValueConstraint(Constraint):
    """Checks if the attribute value has a true compare to at least one of a possible list"""

    def compare(self, a, b):
        cmp_type = self.constraint_params["cmp_type"]

        if cmp_type == "eq":
            return a == b

        if cmp_type == "neq":
            return a != b

        if cmp_type == "greater":
            return a > b

        if cmp_type == "geq":
            return a >= b

        if cmp_type == "less":
            return a < b

        if cmp_type == "leq":
            return a <= b

    def satisfy(self, world):
        if self.constraint_params["type"] == "in_used_target_item":
            target = self.target_nodes[1]

        key = self.constraint_params["key"]
        params_list = self.constraint_params["list"].strip("][").split(", ")

        if not hasattr(target, key):
            return False

        key_value = getattr(target, key)

        for value in params_list:
            if isinstance(key_value, int):
                value = int(value)

            if self.compare(key_value, value):
                return True

        return False
