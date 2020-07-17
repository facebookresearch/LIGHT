#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from parlai.core.params import ParlaiParser
import os
from light.graph.structured_graph import OOGraph
from light.graph.elements.graph_nodes import GraphNode
from light.graph.events.graph_events import ArriveEvent
from light.graph.builders.base import (
    DBGraphBuilder,
)


class UserWorldBuilder(DBGraphBuilder):
    '''Builds a LIGHT map using a predefined world saved to the light database.'''

    def __init__(self, world_id=None, debug=True, opt=None):
        '''Initializes required models and parameters for this graph builder'''
        
        if opt is None:
            parser = ParlaiParser(
                True, True, 'Arguments for building a LIGHT world with User Defined Builder'
            )
            self.add_parser_arguments(parser)

        opt, _unknown = parser.parse_and_process_known_args()
        self.parlai_datapath = opt['datapath']
        self.db_path = os.path.join(opt['datapath'], 'light', 'database3.db')
        if opt.get("light_db_file", "") != "":
            self.db_path = opt.get("light_db_file")
        self.model_path = opt.get("light_model_root")
        DBGraphBuilder.__init__(self, self.db_path)`
        self.debug = debug

        # Need world id to be non none, check that here
        self.world_id = world_id
        # grid of 3d coordinates to room dicts that exist there
        self.grid = {}

    def add_random_new_agent_to_graph(self, target_graph):
        '''Add an agent to the graph in a random room somewhere'''
        # with self.db as ldb:
            # Do things
        '''
            Idea is take an agent and put it into one of the rooms at random 
        '''
        raise NotImplementedError

    def get_graph(self):
        '''Return an OOGraph built by this builder'''
        # Use the get from id methods!
        # with self.db as ldb:
        '''
            The general structure is as follows:
                - query the db for the world, all its entities, edges, and nodes as in loading
                - rooms are top level, fill with objects, and add neighbor connections
                - done(?)
        '''
        raise NotImplementedError

