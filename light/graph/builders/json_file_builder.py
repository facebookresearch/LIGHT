#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import json
import random, copy
from light.graph.structured_graph import OOGraph
from light.graph.builders.base import (
    DBGraphBuilder,
    SingleSuggestionGraphBuilder,
    POSSIBLE_NEW_ENTRANCES,
)
from light.world.world import World

class JsonFileBuilder(DBGraphBuilder):
    """Abstract GraphBuilder that has convenience functions for accessing
    the light db to find content
    """

    def __init__(self, ldb, debug, opt):
        """Initialize a GraphBuilder with access to a LIGHTDatabase class"""
        self.db = ldb
        self.opt = opt
        self._no_npc_models = True
        
    def get_graph(self):
        g = OOGraph.from_worldbuilder_json("scripts/examples/simple_world.json")
        world = World(self.opt, self)
        world.oo_graph = g
        return g, world        
