#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.graph.builders.starspace_assisted import StarspaceBuilder
from light.world.world import World
from light.graph.structured_graph import OOGraph


class ExampleBuilder(StarspaceBuilder):
    """
    Graph builder that extends the StarspaceBuilder to provide a mock
    simple graph building setup, demonstrating how to manually use
    the graph concepts to build contents in the LIGHT world.

    The StarspaceBuilder this inherits from is a direct example of
    using models to assist the process.
    """

    def __init__(self, ldb, debug=True, opt=None):
        self.use_simple = opt["use_simple"]
        self.opt = opt
        super().__init__(ldb, debug=debug, opt=opt)

    def load_models(self):
        """Skip model loading for simple"""
        if self.use_simple:
            return
        super().load_models()

    @staticmethod
    def add_parser_arguments(parser):
        StarspaceBuilder.add_parser_arguments(parser)
        parser.add_argument("--use-simple", action="store_true")

    def get_graph(self):
        """Create a graph"""
        if not self.use_simple:
            return super().get_graph()
        else:
            g = OOGraph(self.opt)

            # Create a room
            r = self.get_random_room()  # Method that pulls a random room from ldb
            # Raw add the room to the graph, as we don't have a helper for this
            room_node = g.add_room(
                r.setting,
                {
                    "room": True,
                    "desc": r.description,
                    "extra_desc": r.background,
                    "name_prefix": "the",
                    "surface_type": "in",
                    "classes": {"room"},
                },
                db_id=r.db_id,
            )

            # Create a character in the room
            char = self.get_random_char()
            use_desc = char.name if char.is_plural == 0 else char.base_form
            use_desc = self._heuristic_name_cleaning(use_desc)
            # raw add the agent to the graph, but using a helper for convenience
            # to extract the props.
            agent_node = g.add_agent(
                use_desc, self._props_from_char(char), db_id=char.db_id
            )
            agent_node.move_to(room_node)

            # Create an object in the room
            obj = self.get_random_obj()
            # Use the really complete helper, because we have it.
            # TODO it could be nice to add your own helpers like this
            # if you find yourself directly editing graphs.
            self._add_object_to_graph(g, obj, room_node)

            # Create another room, connected to the first
            r = self.get_random_room()  # Method that pulls a random room from ldb
            # Raw add the room to the graph, as we don't have a helper for this
            other_room = g.add_room(
                r.setting,
                {
                    "room": True,
                    "desc": r.description,
                    "extra_desc": r.background,
                    "name_prefix": "the",
                    "surface_type": "in",
                    "classes": {"room"},
                },
                db_id=r.db_id,
            )
            g.add_paths_between(
                room_node,
                other_room,
                "a path over there",  # room 1 -> room 2
                "a path aways over",  # room 2 -> room 1
            )

            world = World(self.opt, self)
            world.oo_graph = g
            return g, world
