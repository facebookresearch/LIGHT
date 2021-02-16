#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import unittest, os, sys
from light.graph.builders.starspace_all import StarspaceBuilder
from parlai.core.params import ParlaiParser
import parlai.utils.misc as parlai_utils
import pytest

sys.modules["parlai.core.utils"] = parlai_utils
from light.graph.structured_graph import OOGraph
import random
from light.data_model.light_database import (
    DB_EDGE_IN_CONTAINED,
    DB_EDGE_EX_CONTAINED,
    DB_EDGE_CONTAINED_IN,
    DB_EDGE_WORN,
    DB_EDGE_WIELDED,
    DB_EDGE_NEIGHBOR,
    DB_TYPE_ROOM,
    DB_TYPE_OBJ,
    DB_TYPE_CHAR,
    DB_TYPE_BASE_CHAR,
    DB_TYPE_CHAR,
    DB_TYPE_BASE_OBJ,
    DB_TYPE_OBJ,
    DB_TYPE_BASE_ROOM,
    DB_TYPE_ROOM,
    LIGHTDatabase,
)


@pytest.mark.slow
class TestStarspaceBuilder(unittest.TestCase):
    def setUp(self):
        random.seed(20)
        parser = ParlaiParser()
        here = os.path.abspath(os.path.dirname(__file__))
        self.dbpath = "/checkpoint/light/data/database3.db"
        parlai_datapath = os.path.join(parser.parlai_home, "data")
        ldb = LIGHTDatabase(self.dbpath)
        model_dir = os.path.join(parlai_datapath, "models", "light", "")
        self.testBuilder = StarspaceBuilder(
            ldb,
        )
        self.testGraph, _ = self.testBuilder.get_graph()

    def test_arg_parser(self):
        parser = ParlaiParser()
        parlai_datapath = os.path.join(parser.parlai_home, "data")
        self.assertEqual(self.testBuilder.opt.get("light_db_file"), self.dbpath)
        self.assertEqual(self.testBuilder.opt.get("filler_probability"), 0.3)
        self.assertEqual(self.testBuilder.opt.get("map_size"), 6)
        self.assertEqual(self.testBuilder.opt.get("suggestion_type"), "model")
        self.assertEqual(self.testBuilder.map_size, 6)
        self.assertEqual(self.testBuilder.filler_probability, 0.3)

    def test_room_similiarity(self):
        loc1 = (3, 3, 0)
        loc2 = (3, 3, 0)
        self.assertEqual(
            self.testBuilder.room_similarity(loc1, loc2), 0
        )  # should return 0 because it's the same room

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

    def test_single_suggestion_graph_builder(self):
        self.testBuilder.use_best_match = True
        farmer = self.testBuilder.get_similar_character("servant")
        best_matches = [
            e.name
            for e in self.testBuilder.get_element_relationship(
                "servant", DB_TYPE_CHAR, DB_EDGE_IN_CONTAINED
            )
        ]
        contained = [
            e.name
            for e in self.testBuilder.get_contained_items(farmer.db_id, DB_TYPE_CHAR)
        ]
        self.assertEqual(best_matches, contained)

        box = self.testBuilder.get_similar_object("bandana satchel")
        best_matches = [
            e.name
            for e in self.testBuilder.get_element_relationship(
                "bandana satchel", DB_TYPE_OBJ, DB_EDGE_IN_CONTAINED
            )
        ]
        existing_obj_id = box.db_id
        contained = [
            e.name
            for e in self.testBuilder.get_contained_items(existing_obj_id, DB_TYPE_OBJ)
        ]
        self.assertEqual(best_matches, contained)
        room = self.testBuilder.get_similar_room("library")
        best_matches = [
            e.setting
            for e in self.testBuilder.get_element_relationship(
                "library", DB_TYPE_ROOM, DB_EDGE_NEIGHBOR
            )
        ]
        neighbors = [
            room.setting for room in self.testBuilder.get_neighbor_rooms(room.db_id)
        ]
        self.assertEqual(best_matches, neighbors)
        best_matches = [
            e.name
            for e in self.testBuilder.get_element_relationship(
                "library", DB_TYPE_CHAR, DB_EDGE_IN_CONTAINED + " char"
            )
        ]
        contained_chars = [
            char.name for char in self.testBuilder.get_contained_characters(room.db_id)
        ]
        self.assertEqual(best_matches, contained_chars)

    # TODO: More tests for room validitiy, such as containment hierarchy


if __name__ == "__main__":
    unittest.main()
