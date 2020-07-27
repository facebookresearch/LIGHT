#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.abs

import pickle
import os

NEIGHBOR_FIELDS = ["destination", "direction", "connection"]


class EnvironmentCheckpointParser:
    """
    Load pickle at given path into a class that puts the dict members of the
    pickle into properties of the class, and exposes methods for counting the
    number of objects, characters, and locations in the file
    """

    def __init__(self, pklpath):
        with open(pklpath, "rb") as f:
            data = pickle.load(f)
        self.rooms = data["rooms"]
        self.neighbors = data["neighbors"]
        self.characters = data["characters"]
        self.objects = data["objects"]

    def count_objects(self):
        return len(self.objects)

    def count_characters(self):
        return len(self.characters)

    def count_locations(self):
        return len(self.rooms)

    def get_rooms(self):
        return self.rooms

    def get_characters(self):
        return self.characters

    def get_objects(self):
        return self.objects

    def get_neighbors(self):
        neighbors = []
        for _, n in self.neighbors.items():
            neighbors.append((n["room_id"], dict((k, n[k]) for k in NEIGHBOR_FIELDS)))
        return neighbors
