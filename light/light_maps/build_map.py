#!/usr/bin/env python3
# Builds a LIGHT map using a StarSpace model to connect locations.
# Is not currently connected to the LIGHT text adventure game API
#  (but should be straight-forward).

from parlai.core.params import ParlaiParser
from parlai.core.agents import create_agent
from parlai_internal.tasks.light_maps.builder import load_world_db
from parlai_internal.projects.light.light_maps.html_map import generate_html_map
from parlai_internal.projects.light.light_maps.filler_rooms import build_filler_rooms
import parlai_internal.tasks.graph_world3.graph as graph
import random
import copy
import numpy as np


class BuildLightMap():
    def __init__(self, debug=True):
        parser = ParlaiParser(True, True, 'blah')
        self.opt = parser.parse_args(print_args=False)
        self.dpath = self.opt['datapath'] + '/light_maps'
        self.db = load_world_db(self.dpath, 'light_data.db')
        self.debug = debug
        self.filler_rooms, self.filler_room_names = build_filler_rooms(self.db)
        self.filler_probability = 0.3
        self.load_models()
        self.build_world()

    def props_from_obj(self, obj):
        use_classes = ['object']
        props = {
            'object': True,
            'size': 1,
            'food_energy': 0,
            'value': 1,
            'desc': random.choice(obj['descriptions'])
        }
        if obj['is_surface'] > 0.5:
            props['container'] = True
            props['contain_size'] = 3
            props['surface_type'] = 'on'
            use_classes.append('container')
        if obj['is_container'] > 0.5:
            props['container'] = True
            props['contain_size'] = 3
            props['surface_type'] = 'on'
            use_classes.append('container')
        if obj['is_drink'] > 0.5:
            props['drink'] = True
            use_classes.append('drink')
        if obj['is_food'] > 0.5:
            props['food'] = True
            use_classes.append('food')
        if obj['is_gettable'] < 0.33:
            use_classes.append('not_gettable')
        if obj['is_wearable'] > 0.5:
            props['wearable'] = True
            props['stats'] = {
                'attack': 1
            }
            use_classes.append('wearable')
        if obj['is_weapon'] > 0.5:
            props['wieldable'] = True
            props['stats'] = {
                'attack': 1
            }
            use_classes.append('wieldable')

        props['classes'] = use_classes

        return props

    def props_from_char(self, char):
        use_classes = ['agent']
        props = {
            'agent': True,
            'size': 20,
            'contain_size': 20,
            'health': 1,
            'food_energy': 1,
            'aggression': 0,
            'speed': 5,
            'char_type': char['char_type'],
            'desc': random.choice(char['personas']),
        }

        props['classes'] = use_classes

        return props

    def get_graph(self):
        g = graph.Graph(self.opt)
        room_ids = []

        # Create base rooms
        for pos_room in self.grid.values():
            if pos_room['setting'] == 'EMPTY':
                continue
            pos_room['g_id'] = g.add_node(
                pos_room['setting'],
                {
                    'room': True,
                    'desc': pos_room['description'],
                    'extra_desc': pos_room['background'],
                    'room': True,
                    'contain_size': 2000,  # TODO turk room sizes
                    'name_prefix': "the",
                    'surface_type': "in",
                    'classes': {'room'},
                }
            )
            room_ids.append(pos_room['g_id'])

        # attach rooms to neighbors
        for (i, j, k), pos_room in self.grid.items():
            if pos_room['setting'] == 'EMPTY':
                continue
            if pos_room.get('north'):
                other_room = self.grid[(i, j-1, k)]
                g.add_one_path_to(
                    pos_room['g_id'], other_room['g_id'], 'north')
            if pos_room.get('south'):
                other_room = self.grid[(i, j+1, k)]
                g.add_one_path_to(
                    pos_room['g_id'], other_room['g_id'], 'south')
            if pos_room.get('east'):
                other_room = self.grid[(i+1, j, k)]
                g.add_one_path_to(
                    pos_room['g_id'], other_room['g_id'], 'east')
            if pos_room.get('west'):
                other_room = self.grid[(i-1, j, k)]
                g.add_one_path_to(
                    pos_room['g_id'], other_room['g_id'], 'west')

        # add player to a random room
        player_id = g.add_node(
            'player',
            {
                'agent': True,
                'size': 20,
                'contain_size': 20,
                'health': 1,
                'food_energy': 1,
                'aggression': 0,
                'speed': 25,
                'classes': {'agent'},
            },
            is_player=True,
            uid='player',
        )
        # don't add player to a boring room at the start
        non_filler_room_ids = list(filter(lambda x: x.split("_")[0] not in self.filler_room_names, room_ids))
        g.move_object(player_id, random.choice(non_filler_room_ids))


        # add objects and characters to rooms
        for pos_room in self.grid.values():
            if pos_room['setting'] == 'EMPTY':
                continue
            for item_id in pos_room['ex_objects']:
                if random.random() > 0.5:
                    continue
                obj = self.db['objects'][item_id]
                use_desc = obj['name'] if obj['is_plural'] == 0 \
                    else random.choice(obj['base_form'])
                obj_id = g.add_node(use_desc, self.props_from_obj(obj))
                g.move_object(obj_id, pos_room['g_id'])
            for item_id in pos_room['in_objects']:
                obj = self.db['objects'][item_id]
                use_desc = obj['name'] if obj['is_plural'] == 0 \
                    else random.choice(obj['base_form'])
                props = self.props_from_obj(obj)
                props['classes'].append('described')
                obj_id = g.add_node(use_desc, props)
                g.move_object(obj_id, pos_room['g_id'])
                # mark interactable in the description:
                old_desc = g._node_to_prop[pos_room['g_id']]['desc']
                new_desc = old_desc.replace(obj['name'],
                                            '*{}*'.format(obj['name']))
                # dedupe stars
                new_desc = new_desc.replace('**', '*')
                g._node_to_prop[pos_room['g_id']]['desc'] = new_desc
            for char_id in pos_room['ex_characters']:
                if random.random() > 0.5:
                    continue
                char = self.db['characters'][char_id]
                use_desc = char['name'] if char['is_plural'] == 0 \
                    else random.choice(char['base_form'])
                g_id = g.add_node(use_desc, self.props_from_char(char))
                g.move_object(g_id, pos_room['g_id'])
            for char_id in pos_room['in_characters']:
                char = self.db['characters'][char_id]
                use_desc = char['name'] if char['is_plural'] == 0 \
                    else random.choice(char['base_form'])
                props = self.props_from_char(char)
                props['classes'].append('described')
                props['speed'] = 0
                g_id = g.add_node(use_desc, props)
                g.move_object(g_id, pos_room['g_id'])
                # mark interactable in the description:
                old_desc = g._node_to_prop[pos_room['g_id']]['desc']
                new_desc = old_desc.replace(char['name'],
                                            '*{}*'.format(char['name']))
                # dedupe stars
                new_desc = new_desc.replace('**', '*')
                g._node_to_prop[pos_room['g_id']]['desc'] = new_desc

        return g

    def load_models(self):
        # load model
        mf = '/checkpoint/jase/20181022/light_maps1/lr=0.05_inputdropout=0.9_jobid=4/model'
        opt = copy.deepcopy(self.opt)
        opt['model_file'] = mf
        self.agents = {}
        opt['fixed_candidates_file'] = self.dpath + '/room_full_cands.txt'
        opt['override'] = {
            'fixed_candidates_file': opt['fixed_candidates_file'],
            'dict_file': '/Users/jju/Desktop/LIGHT_maps/model.dict',
        }
        self.agents['room'] = create_agent(opt, requireModelExists=True)
        self.agent = self.agents['room']

    def get_random_room(self):
        ind = random.choice(list(self.db['id_to_roomfeats'].keys()))
        return copy.deepcopy(self.db['rooms'][ind])

    def build_world(self, html_visualization_filename="/tmp/gridtmp.html"):
        self.grid = {}
        r = self.get_random_room()
        loc = (3, 3, 0)
        r['loc'] = loc
        self.grid[loc] = r
        self.map_size = 6
        # block off part of the map at random
        for _i in range(15):
            randloc = (random.randint(0, self.map_size),
                       random.randint(0, self.map_size), 0)
            if randloc == (3, 3, 0):
                continue
            if self.debug:
                print("blocked:" + str(randloc))
            self.grid[randloc] = {'setting': 'EMPTY'}
        # import pdb; pdb.set_trace()
        self.banned_rooms = set()
        self.banned_rooms.add(r['ind'])
        self.stack = []
        self.stack.append(r)
        while True:
            r1 = self.stack.pop()
            self.add_exits(r1)
            if len(self.stack) == 0:
                break
        generate_html_map(html_visualization_filename, self.grid)

    def new_grid_position(self, loc):
        # get a random direction within the map not already filled
        # with another location
        valid = False
        l2 = None
        src_dir = None
        for _i in range(1, 8):
            # pick random direction
            direction = random.randint(0, 3)
            if direction == 0:
                l2 = (loc[0]-1, loc[1], loc[2])
                src_dir = 'west'
            if direction == 1:
                l2 = (loc[0]+1, loc[1], loc[2])
                src_dir = 'east'
            if direction == 2:
                l2 = (loc[0], loc[1]-1, loc[2])
                src_dir = 'north'
            if direction == 3:
                l2 = (loc[0], loc[1]+1, loc[2])
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
        # Get prediction from StarSpace model.
        self.agents['room'].reset()
        txt_feats = self.db['id_to_roomfeats'][self.grid[loc1]['ind']]
        sim_feats = self.db['id_to_roomfeats'][self.grid[loc2]['ind']]
        msg = {'text': txt_feats, 'episode_done': True}
        self.agents['room'].observe(msg)
        response = self.agents['room'].act()
        score = 100000
        for i, k in enumerate(response['text_candidates']):
            if k == sim_feats:
                score = i
                break
        return score

    def possibly_connect_to_neighbor(self, loc1, loc2, src_dir):
        if (loc2 not in self.grid or self.grid[loc2]['setting'] == 'EMPTY'
                or src_dir in self.grid[loc1]):
            # nothing there or it is already connected
            return
        else:
            # compute similarity of rooms:
            sim = self.room_similarity(loc1, loc2)
            if sim > 100:
                # if not in the top 40 most similar rooms, no connection.
                return
            # make connection
            inv_dir = {'east': 'west', 'west': 'east',
                       'north': 'south', 'south': 'north'}
            self.grid[loc2][inv_dir[src_dir] + "*"] = True
            self.grid[loc1][src_dir + "*"] = True

    def possibly_connect_to_neighbors(self, loc):
        self.possibly_connect_to_neighbor(loc, (loc[0]-1, loc[1], loc[2]), 'west')
        self.possibly_connect_to_neighbor(loc, (loc[0]+1, loc[1], loc[2]), 'east')
        self.possibly_connect_to_neighbor(loc, (loc[0], loc[1]-1, loc[2]), 'north')
        self.possibly_connect_to_neighbor(loc, (loc[0], loc[1]+1, loc[2]), 'south')

    def add_room(self, room, loc, src_loc, src_dir):
        self.grid[loc] = room
        room['loc'] = loc
        inv_dir = {'east': 'west', 'west': 'east',
                   'north': 'south', 'south': 'north'}
        self.grid[loc][inv_dir[src_dir]] = True
        self.grid[src_loc][src_dir] = True
        self.banned_rooms.add(room['ind'])
        self.possibly_connect_to_neighbors(loc)
        self.stack.append(room)

    def add_exits(self, r):
        for e in r['neighbors']:
            l1, src_dir = self.new_grid_position(r['loc'])
            if l1 is not None:
                exit_desc = self.db['neighbors'][e]
                exit_text = exit_desc['destination'] + " " + r['category']
                r1 = self.get_similar_room(exit_text)
                if r1 is not None:
                    if self.debug:
                        print(str(r['loc']) + " " + r['setting'] + " -> " + exit_text +
                              " REPLACED-WITH: " + r1['setting'] + " " + str(l1))
                    p = np.random.uniform(0, 1, 1)
                    if p[0] < self.filler_probability and r1['category'] in self.filler_rooms:
                        # choose random room in this category as filler
                        category_filler_rooms = self.filler_rooms[r1['category']]
                        # need to copy exits, or will create small closed loops in the game
                        filler_room = random.choice(category_filler_rooms)
                        filler_room["neighbors"] = r1["neighbors"]
                        self.add_room(filler_room, l1, r['loc'], src_dir)
                    else:
                        self.add_room(r1, l1, r['loc'], src_dir)

    def get_similar_room(self, txt_feats):
        # Get prediction from StarSpace model.
        self.agents['room'].reset()
        msg = {'text': txt_feats,  'episode_done': True}
        self.agents['room'].observe(msg)
        response = self.agents['room'].act()
        ind = 0
        while True:
            key = response['text_candidates'][ind]
            if key in self.db['roomfeats_to_id']:
                rind = self.db['roomfeats_to_id'][key]
                if rind not in self.banned_rooms:
                    return self.db['rooms'][rind]
            ind = ind + 1
            if len(response['text_candidates']) <= ind:
                return None


if __name__ == '__main__':
    random.seed(6)
    m = BuildLightMap()
