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
    POSSIBLE_NEW_ENTRANCES,
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

    def _props_from_char(self, char):
        '''Given a dict representing a character in the world, extract the
        required props to create that object in the world
        '''
        use_classes = ['agent']
        props = {
            'agent': True,
            'size': 20,
            'contain_size': 20,
            'health': 2,
            'food_energy': 1,
            'aggression': 0,
            'speed': 5,
            'char_type': char.char_type,
            'desc': char.desc,
            'persona': char.persona,
        }
        props['classes'] = use_classes
        props['name_prefix'] = char.name_prefix
        if char.is_plural == 1:
            props['is_plural'] = True
        else:
            props['is_plural'] = False
        return props

    def heuristic_name_cleaning(self, use_desc):
        if use_desc.lower().startswith('a '):
            use_desc = use_desc[2:]
        if use_desc.lower().startswith('an '):
            use_desc = use_desc[3:]
        if use_desc.lower().startswith('the '):
            use_desc = use_desc[4:]
        return use_desc

    def add_object_to_graph(self, g, obj, container, extra_props={}):
        if type(obj) == int:
            with self.db as ldb:
                obj = ldb.get_object(id=obj)  # find actual object from id
        obj['description'] = random.choice(obj['description']).capitalize()
        if obj['is_plural'] == 1:
            if extra_props.get('not_gettable', False) != True:
                return None  # skip this. TODO: find nearest object that is singular.
            else:
                # modify object description to make plural work. TODO: fix in data
                desc = obj['description']
                desc = 'You peer closer at one of them. ' + desc
                obj['description'] = desc

        use_desc = obj['name']
        props = self.props_from_obj(obj)
        for k, v in extra_props.items():
            props[k] = v
        props['name_prefix'] = obj['name_prefix']
        object_ = g.oo_graph.add_agent(use_desc, props, db_id=obj.db_id)
        object_.force_move_to(container)
        return object_

    def add_new_agent_to_graph(self, g, char, pos_room):
        if 'is_banned' in char:
            print("skipping BANNED character! " + char['name'])
            return
        if char['is_plural'] > 0:
            print("skipping PLURAL character! " + char['name'])
            return
        use_desc = (
            char['name'] if char['is_plural'] == 0 else random.choice(char['base_form'])
        )
        use_desc = self.heuristic_name_cleaning(use_desc)
        if use_desc in [node.name for node in g.get_npcs()]:
            # Don't create the same agent twice.
            return None
        agent = g.add_agent(use_desc, self.props_from_char(char), db_id=char.db_id)
        agent_id = agent.node_id

        # Is this necesary?  I have never seen these attributes...
        agent.force_move_to(pos_room)
        objs = {}
        for obj in char['carrying_objects']:
            objs[obj] = 'carrying'
        for obj in char['wearing_objects']:
            objs[obj] = 'equipped'
        for obj in char['wielding_objects']:
            objs[obj] = 'equipped'
        for obj in objs:
            object_ = self.add_object_to_graph(g, obj, agent_id)
            obj_id = object_.node_id
            if obj_id is not None:
                if objs[obj] == 'equipped':
                    g.set_prop(obj_id, 'equipped')
        return agent_id

    def add_random_new_agent_to_graph(self, world):
        # pick a random room
        g = world.oo_graph
        id = random.choice(list(g.rooms.keys()))
        pos_room = g.all_nodes[id]
        char = self.get_random_char()
        agent_id = self.add_new_agent_to_graph(g, char, pos_room)
        if agent_id is None:
            return

        # Send message notifying people in room this agent arrived.
        arrival_event = ArriveEvent(agent, text_content=random.choice(POSSIBLE_NEW_ENTRANCES))
        arrival_event.execute(world)

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
