#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import unittest, os
from parlai_internal.projects.light.v1.graph_builders.starspace_neighbor import (
    StarspaceNeighborBuilder,
)
from parlai.core.params import ParlaiParser
from parlai_internal.projects.light.v1.graph_model.structured_graph import OOGraph


class TestStarspaceNeighborBuilder(unittest.TestCase):
    def setUp(self):
        parser = ParlaiParser()
        parlai_datapath = os.path.join(parser.parlai_home, 'data')
        envir_pkl = os.path.join(
            parlai_datapath, 'light', 'environment', 'light-environment-1.2.pkl'
        )
        model_dir = os.path.join(parlai_datapath, 'models', 'light', '')
        testNeighbor = StarspaceNeighborBuilder(
            build_args=["--light-db-file", envir_pkl, "--light-model-root", model_dir]
        )
        testNeighbor.build_world()
        self.testGraph = OOGraph.from_graph(testNeighbor.get_graph())

    def test_builder_returns_graph(self):
        self.assertIsInstance(self.testGraph, OOGraph)

    def test_builder_graph_valid(self):
        self.testGraph.assert_valid()

    def test_graph_contains_room(self):
        self.assertTrue(bool(self.testGraph.rooms))

    def test_graph_contains_character(self):
        self.assertTrue(bool(self.testGraph.agents))

    def test_graph_contains_object(self):
        self.assertTrue(bool(self.testGraph.objects))


if __name__ == '__main__':
    unittest.main()
