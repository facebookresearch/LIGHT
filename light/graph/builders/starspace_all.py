#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import sys

from parlai.core.params import ParlaiParser
from parlai.core.agents import create_agent, create_agent_from_shared
from light.world.world import World
from light.graph.viz.html_map import generate_html_map
from light.graph.structured_graph import OOGraph
from light.graph.elements.graph_nodes import GraphNode
from light.graph.events.graph_events import ArriveEvent
from light.graph.builders.base import (
    DBGraphBuilder,
    SingleSuggestionGraphBuilder,
)
from light.world.content_loggers import (
    RoomInteractionLogger,
)
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
)
from light.graph.builders.base_elements import (
    DBRoom,
    DBObject,
    DBCharacter,
)
from light.data_model.filler_rooms import (
    build_filler_rooms_from_categories,
    FillerRoom,
)
import pickle
import os
import random
import copy
import numpy as np

random.seed(6)
np.random.seed(6)

MAX_EXTRA_AGENTS_PER_ROOM = 2
INV_DIR = {'east': 'west', 'west': 'east', 'north': 'south', 'south': 'north'}
NEIGHBOR = DB_EDGE_NEIGHBOR
WEARING = DB_EDGE_WORN
WIELDING = DB_EDGE_WIELDED
WEARING = DB_EDGE_IN_CONTAINED
CONTAINING = DB_EDGE_IN_CONTAINED
CONTAINED_BY = DB_EDGE_CONTAINED_IN
CHAR_CONTAINING = DB_EDGE_IN_CONTAINED + " char"
RELATIONSHIP_TYPES = [
    NEIGHBOR,
    WIELDING,
    WEARING,
    CONTAINING,
    CONTAINED_BY,
    CHAR_CONTAINING,
]
POSSIBLE_NEW_ENTRANCES = [
    "somewhere you can't see",
    "an undiscernable place",
    "a puff of smoke",
    "behind the shadows",
    "nowhere in particular",
    "a flash of light",
]


class StarspaceBuilder(DBGraphBuilder, SingleSuggestionGraphBuilder):
    '''Builds a LIGHT map using a StarSpace model to connect everything.'''

    def __init__(self, debug=True, opt=None):
        '''Initializes required models and parameters for this graph builder'''
        if opt is None:
            parser = ParlaiParser(
                True, True, 'Arguments for building a LIGHT world with Starspace'
            )
            self.add_parser_arguments(parser)
            opt, _unknown = parser.parse_and_process_known_args()


        self.parlai_datapath = opt['datapath']
        self.db_path = os.path.join(opt['datapath'], 'light', 'database3.db')
        if opt.get("light_db_file", "") != "":
            self.db_path = opt.get("light_db_file")
        self.model_path = opt.get("light_model_root")
        DBGraphBuilder.__init__(self, self.db_path)
        SingleSuggestionGraphBuilder.__init__(self, opt, model_path=self.model_path)
        self.dpath = self.parlai_datapath + '/light_maps'
        self.debug = debug

        category_set = set(self.get_room_categories())
        self.filler_rooms, self.filler_room_names = build_filler_rooms_from_categories(
            category_set
        )

        self.filler_probability = self.opt.get('filler_probability')
        self._no_npc_models = not self.opt.get('use_npc_models')
        self.load_models()
        self.use_best_match = self.opt.get('use_best_match_model')
        self.suggestion_type = self.opt.get('suggestion_type')
        # Cache for retrieved room/ char/ obj dicts from the database
        self.roomid_to_db = {}
        self.roomid_to_feats = {}
        self.feats_to_roomid = {}
        self.objid_to_feats = {}
        self.feats_to_objid = {}
        self.charid_to_feats = {}
        self.feats_to_charid = {}
        # paramter to control the hybridity of the model
        self.prob_skip_ex_objects = self.opt.get('hybridity_prob')
        self.prob_skip_ex_char = self.opt.get('hybridity_prob')
        # grid of 3d coordinates to room dicts that exist there
        self.grid = {}
        # List of rooms that are already selected
        self.banned_rooms = set()

    @staticmethod
    def add_parser_arguments(parser):
        """
        Add arguments to a parser to be able to set the required options for 
        this builder
        """
        parser.add_argument(
            '--suggestion-type',
            type=str,
            default='model',
            help="Input 'model', 'human', or 'hybrid', for the suggestion type",
        )
        parser.add_argument(
            '--hybridity-prob',
            type=float,
            default=0.5,
            help="Set probability how often ex-object or character is skipped",
        )
        parser.add_argument(
            '--use-best-match-model',
            type='bool',
            default=False,
            help="use human suggestions for predicting placement of objects, characters, and room",
        )
        parser.add_argument(
            '--light-db-file',
            type=str,
            default="/checkpoint/light/data/database3.db",
            help="specific path for light database",
        )
        parser.add_argument(
            '--light-model-root',
            type=str,
            default="/checkpoint/light/models/",
            help="specific path for light models",
        )
        parser.add_argument(
            '--filler-probability',
            type=float,
            default=0.3,
            help="probability for retrieving filler rooms",
        )
        parser.add_argument(
            '--use-npc-models',
            type='bool',
            default=True,
            help="whether to use NPC model ",
        )
        parser.add_argument(
            '--map-size', type=int, default=6, help="define the size of the map"
        )
        parser.add_argument(
            '--is-logging',
            type='bool',
            default=True,
            help="Log events with interaction loggers",
        )
        parser.add_argument(
            '--log-path',
            type=str,
            default=''.join([os.path.abspath(os.path.dirname(__file__)), "/../../../logs"]),
            help="Write the events logged to this path",
        )

    def load_models(self):
        '''Load starspace models for building the map'''
        # TODO load from zoo when launched
        opt = copy.deepcopy(self.opt)
        if not self.opt.get('use_npc_models'):
            self._no_npc_models = True
        mf = os.path.join(self.model_path, 'starspace/angela_starspace/model4')
        opt['model_file'] = mf
        # Create room agent
        opt['fixed_candidates_file'] = self.dpath + '/room_title_cands.txt'
        opt['override'] = {'fixed_candidates_file': opt['fixed_candidates_file']}
        self.agents['room'] = create_agent(opt, requireModelExists=True)
        # Model Params are added as new fields to opt dict, Are there better ways around this?
        opt = self.agents['room'].opt.copy()
        opt['fixed_candidates_file'] = self.dpath + '/object_full_cands.txt'
        opt['override'] = {'fixed_candidates_file': opt['fixed_candidates_file']}
        share_dict = self.agents['room'].share()
        share_dict['opt'] = opt
        self.agents['object'] = create_agent_from_shared(share_dict)
        opt = self.agents['room'].opt.copy()
        opt['fixed_candidates_file'] = self.dpath + '/character_full_cands.txt'
        opt['override'] = {'fixed_candidates_file': opt['fixed_candidates_file']}
        share_dict = self.agents['room'].share()
        share_dict['opt'] = opt
        self.agents['character'] = create_agent_from_shared(share_dict)
        self.agent = self.agents['room']

    def _props_from_obj(self, obj):
        '''Given a DBObject representing an object in the world, extract the
        required props to create that object in the world
        '''
        use_classes = ['object']
        props = {
            'object': True,
            'size': 1,
            'food_energy': 0,
            'value': 1,
            'desc': obj.description,
        }
        if obj.is_surface > 0.5:
            props['container'] = True
            props['contain_size'] = 3
            props['surface_type'] = 'on'
            use_classes.append('container')
        if obj.is_container > 0.5:
            props['container'] = True
            props['contain_size'] = 3
            props['surface_type'] = 'on'
            use_classes.append('container')
        if obj.is_drink > 0.5:
            props['drink'] = True
            use_classes.append('drink')
        if obj.is_food > 0.5:
            props['food'] = True
            use_classes.append('food')
        if obj.is_gettable < 0.33:
            use_classes.append('not_gettable')
        if obj.is_wearable > 0.5:
            props['wearable'] = True
            props['stats'] = {'attack': 1}
            use_classes.append('wearable')
        if obj.is_weapon > 0.5:
            props['wieldable'] = True
            props['stats'] = {'attack': 1}
            use_classes.append('wieldable')

        props['classes'] = use_classes
        if obj.is_plural == 1:
            props['is_plural'] = True
        else:
            props['is_plural'] = False

        return props

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

    def _heuristic_name_cleaning(self, use_desc):
        '''Remove some artifacts of bad data collection.'''
        # TODO deprecate after initial version of LIGHTDatabase is completed
        # with this stuff already cleaned up.
        if use_desc.lower().startswith('a '):
            use_desc = use_desc[2:]
        if use_desc.lower().startswith('an '):
            use_desc = use_desc[3:]
        if use_desc.lower().startswith('the '):
            use_desc = use_desc[4:]
        return use_desc

    def add_object_to_graph(self, g, obj, container_node, extra_props={}):
        '''Adds a particular DBObject to the given OOgraph, adding to the specific
        container node. Returns the newly created object node'''
        obj.description = obj.description.capitalize()
        if obj.is_plural == 1:
            if extra_props.get('not_gettable', False) != True:
                # TODO: figure out making plurals work better
                return None
            else:
                # modify object description to make plural work.
                # TODO: fix in data
                desc = obj.description
                desc = f'You peer closer at one of them. {desc}'
                obj.description = desc
        if self._name_not_in_graph(g, obj.name):
            obj_node = self._add_object_to_graph(g, obj, container_node)
            if obj_node.container and self.suggestion_type != 'human':
                print(
                    "Adding CONTAINED objects to CONTAINER object to ",
                    obj.name,
                    obj.db_id,
                )
                contained_objs = self.get_contained_items(obj.db_id, DB_TYPE_OBJ, 3)[1:]
                for o in contained_objs:
                    if self._name_not_in_graph(g, o.name):
                        self._add_object_to_graph(g, o, obj_node)
                # TODO: Currently only adding one layer of contained object of an object
                # Check if we want to add more layers
            return obj_node

    def _name_not_in_graph(self, g, name):
        '''check if a node with a certain name is contained in the graph'''
        return name not in [n.name for n in g.all_nodes.values()]

    def _add_object_to_graph(self, g, obj, container_node, extra_props={}):
        '''Helper for add_object_to_graph to reduce redundancy'''
        # construct props for this object
        use_desc = obj.name
        props = self._props_from_obj(obj)
        for k, v in extra_props.items():
            props[k] = v
        props['name_prefix'] = obj.name_prefix

        # Add the object to the graph
        obj_node = g.add_object(use_desc, props, db_id=obj.db_id)
        if obj_node.size <= container_node.contain_size:
            obj_node.move_to(container_node)
            return obj_node

    def add_new_agent_to_graph(self, g, char, room_node):
        '''Add the given DBcharacter  to the given room (room_node) in the
        given OOFraph. Return the new agent node on success, and None on failure'''
        if 'is_banned' in vars(char):
            print("skipping BANNED character! " + char.name)
            return None
        if char.is_plural > 0:
            print("skipping PLURAL character! " + char.name)
            return None
        use_desc = char.name if char.is_plural == 0 else char.base_form
        use_desc = self._heuristic_name_cleaning(use_desc)

        if use_desc in [node.name for node in g.get_npcs()]:
            # Don't create the same agent twice.
            return None
        agent_node = g.add_agent(use_desc, self._props_from_char(char), db_id=char.db_id)
        # added as a NPC Nothing needs to be done as agent is added as x._human = False
        agent_node.move_to(room_node)
        objs = {}
        if self.suggestion_type != 'model':
            # For the case of only using human recs and hybrid
            for obj in char.carrying_objects['db']:
                # Only use the database id objects, as add object to graph takes an obj_id
                objs[obj] = 'carrying'
            for obj in char.wearing_objects['db']:
                objs[obj] = 'equipped'
            for obj in char.wielding_objects['db']:
                objs[obj] = 'equipped'
        elif self.suggestion_type == 'model':
            objs = {
                obj.db_id: (
                    'equipped' if obj.is_wearable or obj.is_weapon else 'carrying'
                )
                for obj in self.get_contained_items(char.db_id, DB_TYPE_CHAR)
            }
        if self.suggestion_type == 'hybrid' and len(objs) == 0:
            objs = {
                obj.db_id: (
                    'equipped' if obj.is_weapon or obj.is_wearable else 'carrying'
                )
                for obj in self.get_contained_items(char.db_id, DB_TYPE_CHAR, 2)
            }

        for obj in objs:
            obj_node = self.add_object_to_graph(
                g, self.get_obj_from_id(obj), agent_node
            )
            if obj_node is not None:
                if objs[obj] == 'equipped':
                    obj_node.set_prop('equipped', True)
        return agent_node

    def add_random_new_agent_to_graph(self, world):
        '''Add a random agent to the OOGraph at a random room node'''
        g = world.oo_graph
        pos_rooms = [x for x in g.rooms.keys()]
        random.shuffle(pos_rooms)
        for pos_room_id in pos_rooms:
            if pos_room_id in self.roomid_to_db:
                break
        pos_room = self.roomid_to_db[pos_room_id]
        if pos_room.setting == 'EMPTY':
            return
        chars = pos_room.ex_characters
        if len(chars) == 0:
            return
        char = self.get_random_char()
        agent = self.add_new_agent_to_graph(g, char, g.get_node(pos_room.g_id))
        if agent is None:
            return

        # Send message notifying people in room this agent arrived.
        arrival_event = ArriveEvent(agent, text_content=random.choice(POSSIBLE_NEW_ENTRANCES))
        arrival_event.execute(world)

    def construct_grid(self, html_visualization_filename="/tmp/gridtmp.html"):
        '''Create a new stitched together environment from an empty grid'''
        # Initialize for a new grid setup
        self.grid = {}
        self.banned_rooms = set()

        r = self.get_random_room()
        loc = (3, 3, 0)
        r.loc = loc
        self.grid[loc] = r
        self.map_size = self.opt.get('map_size')
        # block off part of the map at random
        for _i in range(15):
            randloc = (
                random.randint(0, self.map_size),
                random.randint(0, self.map_size),
                0,
            )
            if randloc == (3, 3, 0):
                continue
            if self.debug:
                print("blocked:" + str(randloc))
            self.grid[randloc] = FillerRoom(name="EMPTY")  # Empty room

        self.banned_rooms.add(r.db_id)
        self.stack = []
        self.stack.append(r)
        while len(self.stack) > 0:
            r1 = self.stack.pop()
            self.add_exits(r1)
        generate_html_map(html_visualization_filename, self.grid)

    def new_grid_position(self, loc):
        '''Get a random grid position and direction to get there from the
        source location. Returns None, None if all locations on the
        grid from the current location are full'''

        valid = False
        l2 = None
        src_dir = None
        directions = [0, 1, 2, 3]
        while len(directions) > 0:
            # pick random direction
            direction = directions.pop(random.randint(0, len(directions) - 1))
            if direction == 0:
                l2 = (loc[0] - 1, loc[1], loc[2])
                src_dir = 'west'
            if direction == 1:
                l2 = (loc[0] + 1, loc[1], loc[2])
                src_dir = 'east'
            if direction == 2:
                l2 = (loc[0], loc[1] - 1, loc[2])
                src_dir = 'north'
            if direction == 3:
                l2 = (loc[0], loc[1] + 1, loc[2])
                src_dir = 'south'
            valid = True
            if l2[0] < 0 or l2[0] > self.map_size:
                valid = False
            if l2[1] < 0 or l2[1] > self.map_size:
                valid = False
            if l2 in self.grid:
                valid = False
            if valid:
                break
        if valid:
            return l2, src_dir
        else:
            return None, None

    def room_similarity(self, loc1, loc2):
        '''Determine how similar the starspace model thinks two given rooms are'''
        room_1 = self.grid[loc1]
        room_2 = self.grid[loc2]
        if room_1.db_id not in self.roomid_to_feats:
            txt_feats = self.get_text_features(room_1)
        else:
            txt_feats = self.roomid_to_feats[room_1.db_id]
        if room_2.db_id not in self.roomid_to_feats:
            sim_feats = self.get_text_features(room_2)
        else:
            sim_feats = self.roomid_to_feats[room_2.db_id]
        # TODO(M2) refactor to use the builder you create for the light v1 task,
        # or to have feature calculation as a shared utility function that
        # is referenced both here and in your builder

        # Get prediction from StarSpace model.
        msg = {'text': txt_feats, 'episode_done': True}
        self.agents['room'].reset()
        self.agents['room'].observe(msg)
        response = self.agents['room'].act()
        score = 100000
        for i, k in enumerate(response['text_candidates']):
            if k == sim_feats:
                score = i
                break
        return score

    def possibly_connect_to_neighbor(self, loc1, loc2, src_dir):
        '''Connect two rooms if the model thinks they're similar enough'''
        # TODO rather than connecting if two rooms are similar, perhaps
        # we should be connecting if a room is similar to another
        # room's listed neighbor. Then we can be more strict on sim
        if (
            loc2 not in self.grid
            or self.grid[loc2].setting == 'EMPTY'
            or src_dir in self.grid[loc1].possible_connections
        ):
            # nothing there or it is already connected
            return
        else:
            # compute similarity of rooms:
            sim = self.room_similarity(loc1, loc2)
            if sim > 100:
                # if not in the top 100 most similar rooms, no connection.
                return
            # make connection, mark as model possible connection
            self.grid[loc2].possible_connections[INV_DIR[src_dir]] = True
            self.grid[loc1].possible_connections[src_dir] = True
            self.grid[loc2].possible_connections[INV_DIR[src_dir] + "*"] = True
            self.grid[loc1].possible_connections[src_dir + "*"] = True

    def possibly_connect_to_neighbors(self, loc):
        '''Try to connect a room to all of its possible neighbors'''
        self.possibly_connect_to_neighbor(loc, (loc[0] - 1, loc[1], loc[2]), 'west')
        self.possibly_connect_to_neighbor(loc, (loc[0] + 1, loc[1], loc[2]), 'east')
        self.possibly_connect_to_neighbor(loc, (loc[0], loc[1] - 1, loc[2]), 'north')
        self.possibly_connect_to_neighbor(loc, (loc[0], loc[1] + 1, loc[2]), 'south')

    def add_room(self, room, loc, src_loc, src_dir):
        '''Add a room as the neighbor of the room at src_loc'''
        self.grid[loc] = room
        room.loc = loc
        self.grid[loc].possible_connections[INV_DIR[src_dir]] = True
        self.grid[src_loc].possible_connections[src_dir] = True
        self.banned_rooms.add(room.db_id)
        self.possibly_connect_to_neighbors(loc)
        self.stack.append(room)

    def add_exits(self, r):
        '''Try to add all possible exits to a given room'''
        if type(r) is FillerRoom:
            # This is needed as neighbors used to be the field in filler_room
            neighbors = r.neighbors
        elif self.use_best_match:
            neighbors = r.get_text_edges(DB_EDGE_NEIGHBOR)
        else:
            # Not using best match model but the starspace model for model prediction
            neighbors = [
                e.setting
                for e in self.get_neighbor_rooms(
                    room_id=r.db_id, banned_rooms=self.banned_rooms
                )
            ]
        for e in neighbors:
            l1, src_dir = self.new_grid_position(r.loc)
            if l1 is not None:
                exit_text = e + " " + r.category
                r1 = self.get_similar_room(exit_text)
                if r1 is not None:
                    if self.debug:
                        print(
                            str(r.loc)
                            + " "
                            + r.setting
                            + " -> "
                            + exit_text
                            + " REPLACED-WITH: "
                            + r1.setting
                            + " "
                            + str(l1)
                        )
                    p = np.random.uniform(0, 1, 1)

                    if (
                        p[0] < self.filler_probability
                        and r1.category in self.filler_rooms
                    ):
                        # choose random room in this category as filler
                        category_filler_rooms = self.filler_rooms[r1.category]
                        # need to copy exits, or will create small closed loops in the game
                        filler_room = copy.deepcopy(
                            random.choice(category_filler_rooms)
                        )
                        filler_room.db_id = 'f' + str(r1.db_id)
                        # FillerRoom is using the db_id of the room it substitute's
                        filler_room.neighbors = r1.get_text_edges(DB_EDGE_NEIGHBOR)
                        # Filler rooms inherit neighbors from the real room they replace
                        self.add_room(filler_room, l1, r.loc, src_dir)
                    else:
                        self.add_room(r1, l1, r.loc, src_dir)

    ##########For best match model###################
    def get_similar_element(self, txt_feats, element_type):
        ''' Given a text feature, and the corresponding Database type
        return an DBElement of the DB type'''
        agent_type = None
        banned_items = {}
        feats_to_id = None
        get_x_from_id = None
        if element_type == DB_TYPE_ROOM:
            agent_type = 'room'
            banned_items = self.banned_rooms
            feats_to_id = self.roomfeats_to_id
            get_x_from_id = self.get_room_from_id
        elif element_type == DB_TYPE_OBJ:
            agent_type = 'object'
            feats_to_id = self.objfeats_to_id
            get_x_from_id = self.get_obj_from_id
        elif element_type == DB_TYPE_CHAR:
            agent_type = 'character'
            feats_to_id = self.charfeats_to_id
            get_x_from_id = self.get_char_from_id
        if agent_type != None:
            self.agents[agent_type].reset()
            msg = {'text': txt_feats, 'episode_done': True}
            self.agents[agent_type].observe(msg)
            response = self.agents[agent_type].act()
            ind = 0
            while ind < len(response['text_candidates']):
                key = response['text_candidates'][ind]
                rind = feats_to_id(key)
                if rind is not None and rind not in banned_items:
                    return get_x_from_id(rind)
                ind = ind + 1
            return None

    def get_similar_room(self, txt_feats):
        '''Find a similar room to the text room given
        based on a starspace prediction'''
        return self.get_similar_element(txt_feats, DB_TYPE_ROOM)

    def get_similar_object(self, txt_feats):
        '''Find a similar object to the text given 
        based on starspace prediciton'''
        return self.get_similar_element(txt_feats, DB_TYPE_OBJ)

    def get_similar_character(self, txt_feats):
        '''Find a similar object to the text given 
        based on starspace prediciton'''
        return self.get_similar_element(txt_feats, DB_TYPE_CHAR)

    ###################################################

    def get_neighbor_rooms(self, room_id, num_results=5, banned_rooms=None):
        '''get prediction of neighbor room with StarSpaceModel, return DBRoom Object '''
        if banned_rooms is None:
            banned_rooms = [room_id]
        if room_id not in self.roomid_to_feats:
            txt_feats = self.get_text_features(self.get_room_from_id(room_id))
            # This is added due to the new model prediction for neighbors
        else:
            txt_feats = self.roomid_to_feats[room_id]
        response = self.agent_recommend(txt_feats, 'room')
        ind = 0
        results = []
        while len(results) < num_results:
            key = response['text_candidates'][ind]
            if key in self.feats_to_roomid:
                rind = self.feats_to_roomid[key]
            else:
                rind = self.roomfeats_to_id(key)
            if rind not in banned_rooms:
                results.append(self.get_room_from_id(rind))
            ind = ind + 1
            if len(response['text_candidates']) <= ind:
                if len(results) == 0:
                    return None
                else:
                    return results
        return results

    def get_graph(self):
        '''Construct a graph using the grid created with build_world after
        selecting new characters and objects to place within.
        '''
        self.construct_grid()
        g = OOGraph(self.opt)
        self.g = g
        room_ids = []

        # Create base rooms
        self.roomid_to_db = {}
        for pos_room in self.grid.values():
            if pos_room.setting == 'EMPTY':
                continue
            pos_room.g_id = g.add_room(
                pos_room.setting,
                {
                    'room': True,
                    'desc': pos_room.description,
                    'extra_desc': pos_room.background,
                    'size': 2000,  # TODO turk room sizes
                    'contain_size': 2000,  # TODO turk room sizes
                    'name_prefix': "the",
                    'surface_type': "in",
                    'classes': {'room'},
                },
                db_id=pos_room.db_id,
            ).node_id
            room_ids.append(pos_room.g_id)
            # store link between graph and underlying db so we can create more characters, etc.
            self.roomid_to_db[pos_room.g_id] = pos_room

        # attach rooms to neighbors
        for (i, j, k), pos_room in self.grid.items():
            pos_room_node = g.get_node(pos_room.g_id)
            if pos_room.setting == 'EMPTY':
                continue
            if pos_room.possible_connections.get('north', False):
                other_room = g.get_node(self.grid[(i, j - 1, k)].g_id)
                g.add_paths_between(pos_room_node, other_room, 'a path to the north', 'a path to the south')
            if pos_room.possible_connections.get('south', False):
                other_room = g.get_node(self.grid[(i, j + 1, k)].g_id)
                g.add_paths_between(pos_room_node, other_room, 'a path to the south', 'a path to the north')
            if pos_room.possible_connections.get('east', False):
                other_room = g.get_node(self.grid[(i + 1, j, k)].g_id)
                g.add_paths_between(pos_room_node, other_room, 'a path to the east', 'a path to the west')
            if pos_room.possible_connections.get('west', False):
                other_room = g.get_node(self.grid[(i - 1, j, k)].g_id)
                g.add_paths_between(pos_room_node, other_room, 'a path to the west', 'a path to the east')

        # add objects and characters to rooms
        for pos_room in self.grid.values():
            is_filler_room = type(pos_room.db_id) is str
            if pos_room.setting == 'EMPTY' or is_filler_room:
                continue
            no_human_suggestions_obj = True
            no_human_suggestions_char = True
            if self.suggestion_type != 'model':
                # for either human suggestions and hybrid case
                if 'db' in pos_room.ex_objects:
                    for item_id in pos_room.ex_objects['db']:
                        if random.random() > self.prob_skip_ex_objects:
                            continue
                        obj = self.get_obj_from_id(item_id)
                        if obj is not None:
                            room_node = g.get_node(pos_room.g_id)
                            no_human_suggestions_obj = False
                            objid = self.add_object_to_graph(g, obj, room_node)
                if 'db' in pos_room.in_objects:
                    for item_id in pos_room.in_objects['db']:
                        obj = self.get_obj_from_id(item_id)
                        props = {}
                        props['not_gettable'] = True
                        props['classes'] = ['described']
                        if obj is not None:
                            room_node = g.get_node(pos_room.g_id)
                            no_human_suggestions_obj = False
                            obj_node = self.add_object_to_graph(
                                g, obj, room_node, props
                            )
                if 'db' in pos_room.ex_characters:
                    cnt = 0
                    for char_id in pos_room.ex_characters['db']:
                        if (
                            random.random() > self.prob_skip_ex_char
                            or cnt > MAX_EXTRA_AGENTS_PER_ROOM
                        ):
                            continue
                        char = self.get_char_from_id(char_id)
                        if char is not None:
                            room_node = g.get_node(pos_room.g_id)
                            no_human_suggestions_char = False
                            self.add_new_agent_to_graph(g, char, room_node)
                            cnt += 1
                if 'db' in pos_room.in_characters:
                    for char_id in pos_room.in_characters['db']:
                        continue
                        # TODO return to this once stationary npc_model exists
                        char = self.get_char_from_id(char_id)
                        use_desc = char.name if char.is_plural == 0 else char.base_form
                        props = self._props_from_char(char)
                        props['classes'].append('described')
                        props['speed'] = 0
                        no_human_suggestions_char = False
                        room_node = g.get_node(pos_room.g_id)
                        char_node = g.add_node(use_desc, props)
                        char_node.move_to(room_node)
            if self.suggestion_type != 'human':
                # For model suggestions and hybrid
                if self.suggestion_type == 'model' or no_human_suggestions_obj:
                    predicted_objects = self.get_contained_items(
                        container_id=pos_room.db_id, container_type=DB_TYPE_ROOM
                    )
                    for o in predicted_objects:
                        if o is not None:
                            room_node = g.get_node(pos_room.g_id)
                            self.add_object_to_graph(g, o, room_node)
                if self.suggestion_type == 'model' or no_human_suggestions_char:
                    predicted_characters = self.get_contained_characters(
                        room_id=pos_room.db_id, num_results=2
                    )
                    for c in predicted_characters:
                        if c is not None:
                            room_node = g.get_node(pos_room.g_id)
                            self.add_new_agent_to_graph(g, c, room_node)

        for room in g.rooms:
            g.room_id_to_loggers[room] = RoomInteractionLogger(g, room)

        world = World(self.opt, self)
        world.oo_graph = g
        return g, world

    def get_contained_items(
        self, container_id, container_type, num_results=5, banned_items=[]
    ):
        '''
        Get prediction of contained items from StarSpace model
        given a container's database id and container type.
        '''
        must_be_gettable = True
        if container_type == DB_TYPE_ROOM:
            must_be_gettable = False
            if container_id in self.roomid_to_feats:
                txt_feats = self.roomid_to_feats[container_id]
            else:
                txt_feats = self.get_text_features(self.get_room_from_id(container_id))
        elif container_type == DB_TYPE_OBJ:
            if container_id in self.objid_to_feats:
                txt_feats = self.objid_to_feats[container_id]
            else:
                txt_feats = self.get_text_features(self.get_obj_from_id(container_id))
        elif container_type == DB_TYPE_CHAR:
            if container_id in self.charid_to_feats:
                txt_feats = self.charid_to_feats[container_id]
            else:
                txt_feats = self.get_text_features(self.get_char_from_id(container_id))
        response = self.agent_recommend(txt_feats, 'object')
        ind = 0
        results = []
        while len(results) < num_results and ind < len(response['text_candidates']):
            key = response['text_candidates'][ind]
            if '{{}}' in key:
                ind = ind + 1
                continue
            oid = self.objfeats_to_id(key)
            if oid is not None and oid not in banned_items:
                obj = self.get_obj_from_id(oid)
                if obj.is_gettable or not must_be_gettable:
                    results.append(obj)
            ind = ind + 1
        return results

    def get_contained_characters(self, room_id, num_results=5, banned_characters=[]):
        ''' Get prediction of contained characters in given room_id from StarSpace model.'''
        if type(room_id) is str and room_id[0] == 'f':
            # To check for filler_rooms, if it is filler_room, using the db_id of the room it has replaced
            room_id = room_id[1:]
        if room_id in self.roomid_to_feats:
            txt_feats = self.roomid_to_feats[room_id]
        else:
            txt_feats = self.get_text_features(self.get_room_from_id(room_id))
        response = self.agent_recommend(txt_feats, 'character')
        ind = 0
        results = []
        while len(results) < num_results:
            key = response['text_candidates'][ind]

            if 'wench' in key:
                ind = ind + 1
                continue
            cind = self.charfeats_to_id(key)
            if cind is not None and cind not in banned_characters:
                results.append(self.get_char_from_id(cind))
            ind = ind + 1
            if len(response['text_candidates']) <= ind:
                if len(results) == 0:
                    return None
                else:
                    return results
        return results

    def get_description(self, txt_feat, element_type, num_results=5):
        '''Get description of element, given the txt_feature title'''
        response = self.agent_recommend(txt_feat, 'node_desc')
        text_results = [r['text_candidates'] for r in response][
            : min(num_results, len(response))
        ]
        return text_results

    def get_object_affordance(self, txt_feat, num_results=5):
        '''Given a text representation of an object, return its
        affordance such as wearable, gettable, wiedable etc'''
        response = self.agent_recommend(txt_feat, 'obj_afford')
        text_results = [r['text_candidates'] for r in response][
            : min(num_results, len(response))
        ]
        return text_results

    def get_character_object_relation(self, txt_feat, affordance_type, num_results=5):
        '''Get the text based object given the character name and affordance of the object'''
        query_type = 'char_' + affordance_type
        response = self.agent_recommend(txt_feat, query_type)
        text_results = [r['text_candidates'] for r in response][
            : min(num_results, len(response))
        ]
        return text_results

    def get_element_relationship(
        self,
        element_txt,
        element_type,
        relationship_type,
        context=None,
        num_results=5,
        banned_items=[],
    ):
        ''' Given a text description of a non-graph element and a type of 
        relationship to query, find closest match in database 
        and return model suggestions '''
        # TODO: context based query
        element_rel_dict = {
            CONTAINING: [DB_TYPE_OBJ, DB_TYPE_ROOM, DB_TYPE_CHAR],
            CHAR_CONTAINING: [DB_TYPE_CHAR],
            NEIGHBOR: [DB_TYPE_ROOM],
        }
        msg = "Unreasonable element-relationship query"
        assert element_type in element_rel_dict[relationship_type], msg
        if not self.use_best_match:
            return
        closest_match = None
        if element_type == DB_TYPE_OBJ:
            closest_match = self.get_similar_object(element_txt)
        elif relationship_type == CHAR_CONTAINING:
            closest_match = self.get_similar_room(element_txt)
        elif element_type == DB_TYPE_CHAR:
            closest_match = self.get_similar_character(element_txt)
        elif element_type == DB_TYPE_ROOM:
            closest_match = self.get_similar_room(element_txt)
            banned_items.extend(self.banned_rooms)
        if closest_match is None:
            return
        if relationship_type == NEIGHBOR:
            return [
                r
                for r in self.get_neighbor_rooms(closest_match.db_id, num_results)
                if r not in banned_items
            ]
        elif relationship_type == CONTAINING:
            return self.get_contained_items(
                closest_match.db_id, element_type, num_results
            )
        elif relationship_type == CHAR_CONTAINING:
            return self.get_contained_characters(closest_match.db_id, num_results)

    def get_text_features(self, c, full=False):
        '''Return text feature given a candidate and return and cache the text feature'''
        feat = ''
        if type(c) is DBRoom:
            feat = c.room_features(full)
            self.feats_to_roomid[feat] = c.db_id
            self.roomid_to_feats[c.db_id] = feat
        if type(c) is FillerRoom:
            feat += c.setting
            if full:
                feat += '. '
                feat += c.category
                feat += '. '
                feat += c.description
                feat += ' '
                feat += c.background
                feat += ' '
            feat = feat.rstrip()
            self.feats_to_roomid[feat] = c.db_id
            self.roomid_to_feats[c.db_id] = feat
        if type(c) is DBObject:
            self.feats_to_objid[feat] = c.db_id
            feat = c.object_features(full)
            self.objid_to_feats[c.db_id] = feat
        if type(c) is DBCharacter:
            feat = c.character_features(full)
            self.feats_to_charid[feat] = c.db_id
            self.charid_to_feats[c.db_id] = feat
        return feat
