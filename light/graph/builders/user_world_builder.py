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

    def __init__(self, world_id=None, player_id=None, debug=True, opt=None):
        '''Initializes required models and parameters for this graph builder'''
        
        if opt is None:
            parser = ParlaiParser(
                True, True, 'Arguments for building a LIGHT world with User Defined Builder'
            )
            self.add_parser_arguments(parser)

        opt, _unknown = parser.parse_and_process_known_args()
        self.opt = opt
        self.parlai_datapath = opt['datapath']
        self.db_path = os.path.join(opt['datapath'], 'light', 'database3.db')
        if opt.get("light_db_file", "") != "":
            self.db_path = opt.get("light_db_file")
        self.model_path = opt.get("light_model_root")
        DBGraphBuilder.__init__(self, self.db_path)`
        self.debug = debug

        # Need world id to be non none, check that here
        self.world_id = world_id
        self.player_id = player_id
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
        g = OOGraph(self.opt)
        self.g = g
        with self.db as ldb:
            world = ldb.get_world(self.world_id, self.player_id)
            assert len(world) == 1, "Must get a single world back to load game from it"
            resources = db.get_world_resources(self.world_id, self.player_id)

        world = world[0]
        # {world_id, name, height, width, num_floors} are keys!
        dimensions = {x: world[x] for x in world.keys() if x != 'owner_id'}
        # Do not need x/y room right?
        # Gives us the contains and neighbor edges
        edges = resources[1]
        edge_list = [dict(edge) for edge in edges]
        
        # Load the entities 
        # Need a db_id to g_id map!
        # Do not bother mapping to local here, map straight into the graph (make these nodes)
        nextID = 1
        entities = {'room': {}, 'character': {}, 'object': {},}
        db_to_g = {}
        node_to_g= {}
        type_to_entities = {'room': resources[2], 'character': resources[3], 'object':resources[4],}
        for type_ in type_to_entities.keys():
            for entity in type_to_entities[type_]:
                props = dict(entity)
                if (type_ == 'room'):
                    props['desc'] = props['description'] if 'description' in props else None
                    props['extra_desc'] = props['backstory'] if 'backstory' in props else None
                else:
                    props['desc'] = props['physical_description'] if 'physical_description' in props else None
                func = getattr(g, f'add_{type_}')
                # No uid or player for any of these
                g_id = func(props['name'], props, db_id=props['db_id'])
                db_to_g[props['db_id']] = g_id
                node_to_g[props['node_id']] = g_id

        edges = []
        for edge in edge_list:
            src = g.get_node(node_to_g[edge['src_id']])
            dst = g.get_node(node_to_g[edge['dst_id']])
            edge = edge['edge_type']
            # TODO: Link to light_database - check logic error with duplicate edges
            if edge == "neighbors to the north":
                g.add_paths_between(src, dst, 'a path to the south', 'a path to the north')
            elif edge == "neighbors to the south":
                g.add_paths_between(src, dst, 'a path to the north', 'a path to the south')
            elif edge == "neighbors to the east":
                g.add_paths_between(src, dst, 'a path to the west', 'a path to the east')
            elif edge == "neighbors to the west":
                g.add_paths_between(src, dst, 'a path to the east', 'a path to the west')
            # This cannot be right...
            elif edge == "neighbors above":
                g.add_paths_between(src, dst, 'a path to the down', 'a path to the up')
            elif edge == "neighbors below":
                g.add_paths_between(src, dst, 'a path to the up', 'a path to the down')
            elif edge == "contains":
                dst.move_to(src)


        # Now we have all the info we need - time to organize
        # Add neighbors to rooms with the edges, and add objects and characters to rooms
        world = World(self.opt, self)
        world.oo_graph = g
        return world
