#!/usr/bin/env python3
import parlai_internal.projects.light.v1.callbacks as Callbacks
from parlai_internal.projects.light.v1.graph_model.content_loggers import RoomConversationBuffer
from parlai_internal.projects.light.light_maps.graph_printer import GraphPrinter

from collections import Counter
from copy import deepcopy
import emoji
import os
import random
import json
# TODO don't use * imports
from parlai_internal.projects.light.v1.graph_functions import *
from parlai_internal.projects.light.v1.graph_constraints import *
from parlai_internal.projects.light.v1.npc_models import *
from parlai_internal.projects.light.v1.utils import rm

# TODO remove references to class, Graph is now deprecated
class Graph(object):
    def __init__(self, opt):

        self.callbacks = {}
        self.variables = {}
        self._opt = opt
        self._node_to_edges = {}
        self._node_to_prop = {}
        self._node_contained_in = {}
        self._node_contains = {}
        self._node_follows = {}
        self._node_followed_by = {}
        self._nodes_to_delete = []
        self._room_nodes = []
        self._player_cnt = 0
        self._playerid_to_agentid = {}
        self._agentid_to_playerid = {}
        # non-player characters that we move during update_world func.
        self._node_npcs = set()
        self._initial_num_npcs = 0
        self._npc_names = (
            set()
        )  # used to make sure we don't have two with the same name in the world
        self._node_to_desc = {}
        self._node_freeze = False
        self._cnt = 0
        self._save_fname = 'tmp.gw'
        self._node_to_text_buffer = {}
        self._node_to_observations = {}
        self._goal = []
        self.__message_callbacks = {}
        self._models = {}
        self._visited_rooms = {}
        self._last_rooms = {}
        self._graph_printer = GraphPrinter()
        self.npc_models = npc_models(opt, self)
        # Used for storage of conversation history
        self._database_location = opt.get('database_path', None)
        self._room_convo_buffers = {}  # Map from room id to RoomConversationBuffer

        # make a special void room to place things in limbo if they are nowhere else
        self.void_id = self.add_node('void', {'classes': ['room']}, is_room=True)
        self.add_contained_in(self.void_id, self.void_id)  # contained within itself

    def check_graph(self):
        ''' check the integrity of the graph in various ways, for now, check for sizes.'''
        for n in self._node_to_prop.keys():
            node = self._node_to_prop[n]
            if 'size' not in node:
                print("missing size: " + n)
                import pdb

                pdb.set_trace()

    # -- Graph properties -- #

    def copy(self):
        '''return a copy of this graph'''
        return deepcopy(self)

    def populate_ids(self):
        self.object_ids = self.get_all_by_prop('object')
        self.container_ids = self.get_all_by_prop('container')
        self.agent_ids = self.get_all_by_prop('agent')

    def unique_hash(self):
        # TODO: make it independent of specific world settings
        # TODO: Improve everything about this, it's really old
        # object_ids, agent_ids, and container_ids are set by construct_graph
        self.populate_ids()
        s = ''
        apple_s = []
        for id in self.object_ids + self.container_ids + self.agent_ids:
            cur_s = ''
            if not self.node_exists(id):
                cur_s += 'eaten'
            else:
                cur_s += self._node_contained_in[id]
                for prop in ['wielding', 'wearing', 'dead']:
                    if prop in self._node_to_prop[id]:
                        cur_s += prop
            if self.node_to_desc_raw(id) == 'apple':
                apple_s.append(cur_s)
            else:
                s += cur_s
        s += ''.join(sorted(apple_s))
        return s

    def __eq__(self, other):
        return self.unique_hash() == other.unique_hash()

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if '__message_callbacks' not in k:  # we cant copy callback anchors
                setattr(result, k, deepcopy(v, memo))
            else:
                setattr(result, k, {})
        return result

    def all_node_ids(self):
        '''return a list of all the node ids in the graph'''
        return list(self._node_to_prop.keys())

    # TODO update once goals are better defined. These should really be
    # attached to a player rather than in the graph itself.
    def goals_complete(self):
        # TODO generic goals rather than just x is in y
        if len(self._goal) == 0:
            return False
        if type(self._goal) == dict:
            self._goal = []
        for goal in self._goal:
            if not self.node_contained_in(goal[1]) == goal[0]:
                return False
        return True

    # TODO deprecate and replace with a json export
    def save_graph(self, fname):
        '''Save this graph to the file'''
        path = os.path.join(self._opt['datapath'], 'graph_world3')
        os.makedirs(path, exist_ok=True)
        if fname != '':
            self._save_fname = path + '/' + fname + '.gw3'
        members = [
            attr
            for attr in dir(self)
            if not callable(getattr(self, attr))
            and (not attr.startswith("__"))
            and (attr.startswith("_"))
        ]
        model = {}
        for m in members:
            model[m] = getattr(self, m)
        with open(self._save_fname, 'wb') as write:
            torch.save(model, write)

    # TODO deprecate and replace with a json import
    def load_graph(self, fname):
        '''load the contents of the file to this graph'''
        if fname != '':
            path = os.path.join(self._opt['datapath'], 'graph_world3')
            fname = path + '/' + fname + '.gw3'
        else:
            fname = self._save_fname
        if not os.path.isfile(fname):
            print("[graph file not found: " + fname + ']')
            return False
        print("[loading graph: " + fname + ']')
        members = [
            attr
            for attr in dir(self)
            if not callable(getattr(self, attr))
            and (not attr.startswith("__"))
            and (attr.startswith("_"))
        ]
        with open(fname, 'rb') as read:
            model = torch.load(read)
        for m in members:
            if m in model:
                setattr(self, m, model[m])
            else:
                print("[ loading: " + m + " is missing in file ]")
        self._save_fname = fname
        return True

    def freeze(self, freeze=None):
        if freeze is not None:
            self._node_freeze = freeze
        return self._node_freeze

    def version(self):
        return 3

    def add_message_callback(self, id, func):
        self.__message_callbacks[id] = func

    def clear_message_callback(self, id):
        if id in self.__message_callbacks:
            del self.__message_callbacks[id]

    @staticmethod
    # TODO make a get_from_version_3 for when new is done
    def get_from_version_2(old_g):
        '''Convert a v2 graph into a v3 graph'''
        out_graph = Graph(old_g._opt)
        # The structure of node_to_edges has changed significantly from v2 to
        # v3. V2 was node -> list of edges, where an edge is an array of the
        # edge type and the destination
        # V3 is node -> dict where the key is the a pair of the above, and
        # the rest is a dict of various options for that pair
        for node, edge_list in old_g._node_to_edges.items():
            out_graph._node_to_edges[node] = {}
            for edge in edge_list:
                out_graph._node_to_edges[node][(edge[0], edge[1])] = {
                    'label': None,
                    'examine_desc': None,
                    # TODO get these from the lock or something idk
                    'locked_desc': None,
                    'unlocked_desc': None,
                    'locked_with': None,
                    'is_locked': False,
                    'full_label': None,
                }

        out_graph._node_to_prop = old_g._node_to_prop  # No changes to struct
        # We need to add things to the prop list though make things work

        default_props = {
            'name_prefix': 'the',
            'surface_type': 'in',
            'size': 1,
            'contain_size': 200,
            'health': 1,
            'food_energy': 1,
            'aggression': 0,
            'value': 1,
            'speed': 25,
        }
        for node in out_graph._node_to_prop:
            out_graph.set_prop(node, 'names', out_graph.get_prop(node, 'names', []))
            node_classes = []
            for prop_name, prop_val in out_graph._node_to_prop[node].items():
                if prop_val is True:
                    node_classes.append(prop_name)
            out_graph.set_prop(node, 'classes', node_classes)

            for prop_name, prop_val in default_props.items():
                out_graph.set_prop(
                    node, prop_name, out_graph.get_prop(node, prop_name, prop_val)
                )
            out_graph.set_prop(node, 'size', out_graph.get_prop(node, 'size', 1))

            out_graph.set_prop(
                node, 'contain_size', out_graph.get_prop(node, 'contain_size', 20)
            )

            out_graph.set_prop(
                node, 'contain_size', out_graph.get_prop(node, 'contain_size', 20)
            )

        out_graph._node_contained_in = old_g._node_contained_in  # No changes
        out_graph._node_contains = old_g._node_contains  # No changes
        out_graph._node_follows = old_g._node_follows  # No changes
        out_graph._node_followed_by = old_g._node_followed_by  # No changes
        out_graph._node_npcs = old_g._node_npcs  # No changes
        out_graph._node_to_desc = old_g._node_to_desc  # No changes
        out_graph._node_freeze = old_g._node_freeze  # No changes
        out_graph._cnt = old_g._cnt  # No changes
        out_graph._save_fname = old_g._save_fname  # No changes
        out_graph._node_to_text_buffer = old_g._node_to_text_buffer  # Similar
        out_graph.callbacks = {}
        out_graph.variables = {}
        return out_graph

    # -- Callbacks and variables -- #

    def register_callbacks(self, callbacks, variables):
        self.callbacks = callbacks
        self.variables = variables

    def register_parser(self, file_parser):
        self.parser = file_parser

    # -- Full node editors/creators/getters/deleters -- #

    def get_player(self, id):
        '''Get the state of a player (along with everything they carry) from
        the graph
        '''
        state = {}
        state['id'] = id
        if id in self._node_to_text_buffer:
            state['node_to_text_buffer'] = self._node_to_text_buffer[id]
        if id in self._node_contains:
            state['node_contains'] = self._node_contains[id]
            state['contained_nodes'] = []
            for obj_id in self._node_contains[id]:
                props = self._node_to_prop[obj_id]
                if 'persistent' in props and props['persistent'] == 'level':
                    continue  # Leave level-based items behind
                state['contained_nodes'].append(self.get_obj(obj_id))
        if id in self._node_to_prop:
            state['node_to_prop'] = self._node_to_prop[id]
        if id in self._node_to_desc:
            state['node_to_desc'] = self._node_to_desc[id]
        return state

    def get_obj(self, id):
        '''Get the state of an object from the graph'''
        state = {}
        state['id'] = id
        if id in self._node_contains:
            state['node_contains'] = self._node_contains[id]
            state['contained_nodes'] = []
            for obj_id in self._node_contains[id]:
                state['contained_nodes'].append(self.get_obj(obj_id))
        if id in self._node_to_prop:
            state['node_to_prop'] = self._node_to_prop[id]
        if id in self._node_contained_in:
            state['node_contained_in'] = self._node_contained_in[id]
        if id in self._node_to_desc:
            state['node_to_desc'] = self._node_to_desc[id]
        return state

    def set_player(self, state):
        '''Instantiate a player into the graph with the given state'''
        id = state['id']
        if 'node_to_text_buffer' in state:
            self._node_to_text_buffer[id] = (
                state['node_to_text_buffer'] + self._node_to_text_buffer[id]
            )
        if 'node_contains' in state:
            self._node_contains[id] = state['node_contains']
            for obj_state in state['contained_nodes']:
                self.set_obj(obj_state)
        if 'node_to_prop' in state:
            self._node_to_prop[id] = state['node_to_prop']

    def set_obj(self, state):
        '''Instantiate an object into the graph with the given state'''
        id = state['id']
        self._node_to_edges[id] = []
        self._node_to_prop[id] = state['node_to_prop']
        self._node_contains[id] = state['node_contains']
        for obj_state in state['contained_nodes']:
            self.set_obj(obj_state)
        self._node_to_desc[id] = state['node_to_desc']
        self._node_contained_in[id] = state['node_contained_in']

    def add_node(self, desc, props, is_player=False, uid='', is_room=False):
        id = desc.lower()
        if not is_player:
            id = "{}_{}".format(id, self._cnt)
            if uid != '':
                id += '_{}'.format(uid)
        self._cnt = self._cnt + 1
        if id in self._node_to_edges:
            return False
        self._node_to_edges[id] = {}
        if type(props) == str:
            self._node_to_prop[id] = {}
            self._node_to_prop[id][props] = True
            self.set_prop(id, 'classes', [props])
        elif type(props) == dict:
            self._node_to_prop[id] = {}
            for p in props:
                self._node_to_prop[id][p] = props[p]
            for p in props['classes']:
                self._node_to_prop[id][p] = True
        else:
            self._node_to_prop[id] = {}
            for p in props:
                self._node_to_prop[id][p] = True
        if self._node_to_prop[id].get('names') is None:
            self._node_to_prop[id]['names'] = [desc]
        if self._node_to_prop[id].get('contain_size', None) is None:
            # set a default contain size
            if is_room:
                self._node_to_prop[id]['contain_size'] = 1000000
            else:
                self._node_to_prop[id]['contain_size'] = 0
        if self._node_to_prop[id].get('size', None) is None:
            self._node_to_prop[id]['size'] = 1  # set a default size
        self._node_to_prop[id]['is_player'] = is_player
        self._node_contains[id] = set()
        self._node_to_desc[id] = desc
        if 'agent' in self._node_to_prop[id]['classes'] or is_player:
            if not self.has_prop(id, 'health'):
                self.set_prop(id, 'health', 2)
            self.new_agent(id)
        if is_room:
            self._room_nodes.append(id)
            self._room_convo_buffers[id] = RoomConversationBuffer(
                self, self._database_location, id
            )
            # TODO fix the above!
        if hasattr(self, 'void_id'):
            # make node contained in the void, until it is put somewhere else.
            self.add_contained_in(id, self.void_id)
        return id

    # TODO rework goals entirely for task3
    def add_goal(self, id1, id2):
        # TODO generic goals rather than just x is in y
        self._goal.append([id1, id2])

    def new_agent(self, id):
        self._node_to_text_buffer[id] = ''  # clear buffer
        self._node_to_observations[id] = []  # clear buffer
        self._visited_rooms[id] = set()
        self._last_rooms[id] = None

    def delete_node(self, id):
        self._nodes_to_delete.append(id)

    def delete_nodes(self):
        for i in self._nodes_to_delete:
            self._really_delete_node(i)
        self._nodes_to_delete = []

    def _really_delete_node(self, id):
        '''Remove a node from the graph, keeping the reference for printing'''
        # Remove from the container
        loc = self.location(id)
        if loc is not None and id in self._node_contains[loc]:
            self._node_contains[self.location(id)].remove(id)
        else:
            # can't delete a node that's not in anything.
            return
        # remove size from above object, then remove contained in edge
        above_id = self.node_contained_in(id)
        if above_id is not None:
            size = self.get_prop(id, 'size')
            omax_size = self.get_prop(above_id, 'contain_size')
            omax_size = omax_size + size
            self.set_prop(above_id, 'contain_size', omax_size)
            rm(self._node_contained_in, id)
        # all things inside this are zapped too
        if id in self._node_contains:
            os = deepcopy(self._node_contains[id])
            for o in os:
                self.delete_node(o)
        # now remove edges from other rooms
        for r in self._node_to_edges[id]:
            if r[0] == 'path_to':
                self._node_to_edges[r[1]].remove(['path_to', id])
        # stop all agents from following this one
        if id in self._node_followed_by:
            ags = deepcopy(self._node_followed_by[id])
            for a in ags:
                self.set_follow(a, None)
        rm(self._node_follows, id)
        # Remove from npc list
        if id in self._node_npcs:
            self._node_npcs.remove(id)

    # -- Node-in-graph properties -- #

    def add_edge(
        self,
        id1,
        edge,
        id2,
        edge_label=None,
        locked_with=None,
        edge_desc=None,
        full_label=False,
    ):
        '''Add an edge of the given type from id1 to id2. Optionally can set
        a label for that edge
        '''
        if edge_desc is None:
            edge_desc = self.get_props_from_either(id2, id1, 'path_desc')[0]
        if (edge, id2) not in self._node_to_edges[id1]:
            self._node_to_edges[id1][(edge, id2)] = {
                'label': edge_label,
                'examine_desc': edge_desc,
                # TODO get these from the lock or something idk
                'locked_desc': edge_desc,
                'unlocked_desc': edge_desc,
                'locked_with': locked_with,
                'is_locked': False,
                'full_label': full_label,
            }

    def add_one_path_to(self, id1, id2, label=None,
                        locked_with=None, desc=None, full_label=False):
        if id1 == id2:
            return False
        self.add_edge(id1, 'path_to', id2, label, locked_with, desc,
                      full_label)
        return True

    def add_path_to(self, id1, id2, desc1=None, desc2=None, locked_with=None,
                    examine1=None, examine2=None):
        '''Create a path between two rooms'''
        if id1 == id2:
            return False
        self.add_edge(id1, 'path_to', id2, desc1, locked_with, examine1)
        self.add_edge(id2, 'path_to', id1, desc2, locked_with, examine2)
        return True

    def is_path_to(self, id1, id2):
        '''determine if there is a path from id1 to id2'''
        return ('path_to', id2) in self._node_to_edges[id1]

    def node_contains(self, loc):
        '''Get the set of all things that a node contains'''
        if loc in self._node_contains:
            return set(self._node_contains[loc])
        else:
            return set()

    def add_contained_in(self, id1, id2):
        if id1 in self._node_contained_in:
            i_am_in = self._node_contained_in[id1]
            self._node_contains[i_am_in].remove(id1)
        self._node_contained_in[id1] = id2
        self._node_contains[id2].add(id1)
        return True

    def node_contained_in(self, id):
        if id not in self._node_contained_in:
            return None
        return self._node_contained_in[id]

    def set_follow(self, id1, id2):
        '''Set id1 to be following id2, unfollowing whatever id1 followed
        before if necessary
        '''
        if id1 in self._node_follows:
            i_follow = self._node_follows[id1]
            self._node_followed_by[i_follow].remove(id1)
        if id2 is not None:
            self._node_follows[id1] = id2
            if id2 not in self._node_followed_by:
                self._node_followed_by[id2] = set()
            self._node_followed_by[id2].add(id1)
            return True
        else:
            if id1 in self._node_follows:
                self._node_follows.pop(id1)

    def get_followers(self, agent_id):
        '''Get the nodes following the given agent'''
        if agent_id in self._node_followed_by:
            return self._node_followed_by[agent_id]
        return []

    def get_following(self, agent_id):
        '''get the node that the given agent is following, if any'''
        if agent_id in self._node_follows:
            return self._node_follows[agent_id]
        return None

    # TODO deprecate and remove classed descriptions
    def combine_classed_descs(descs):
        adj_descs = [{'default': d} if type(d) is str else d for d in descs]
        last_round_descs = {'default': ''}
        for desc_set in [adj_descs]:
            round_descs = {}
            for class_name in desc_set:
                if class_name not in last_round_descs:
                    old_d = last_round_descs['default'].strip()
                    new_d = desc_set[class_name].strip()
                    round_descs[class_name] = (old_d + ' ' + new_d).strip()
                else:
                    old_d = last_round_descs[class_name].strip()
                    new_d = desc_set[class_name].strip()
                    round_descs[class_name] = (old_d + ' ' + new_d).strip()
            last_round_descs = round_descs
        return last_round_descs

    def lock_path(self, id1, id2, key_id):
        '''lock the edge from id1 to id2 using the given key'''
        self._node_to_edges[id1][('path_to', id2)]['is_locked'] = True
        self._node_to_edges[id1][('path_to', id2)]['examine_desc'] = \
            self._node_to_edges[id1][('path_to', id2)]['locked_desc']
        self._node_to_edges[id2][('path_to', id1)]['is_locked'] = True
        self._node_to_edges[id2][('path_to', id1)]['examine_desc'] = \
            self._node_to_edges[id2][('path_to', id1)]['locked_desc']

    def unlock_path(self, id1, id2, key_id):
        '''unlock the edge from id1 to id2 using the given key'''
        self._node_to_edges[id1][('path_to', id2)]['is_locked'] = False
        self._node_to_edges[id1][('path_to', id2)]['examine_desc'] = \
            self._node_to_edges[id1][('path_to', id2)]['unlocked_desc']
        self._node_to_edges[id2][('path_to', id1)]['is_locked'] = False
        self._node_to_edges[id2][('path_to', id1)]['examine_desc'] = \
            self._node_to_edges[id2][('path_to', id1)]['unlocked_desc']

    def path_is_locked(self, id1, id2):
        return self._node_to_edges[id1][('path_to', id2)]['is_locked']

    def get_path_locked_with(self, id1, id2):
        if id1 == id2:
            # TODO get the locked_with of a room when the path is to itself
            # as this function shouldn't be called like this
            return None
        return self._node_to_edges[id1][('path_to', id2)]['locked_with']

    def set_desc(self, id, desc):
        self._node_to_desc[id] = desc

    def node_exists(self, id):
        return id in self._node_contained_in

    # -- Prop accessors -- #

    def get_prop(self, id, prop, default=None):
        '''Get the given prop, return None if it doesn't exist'''
        if id in self._node_to_prop:
            if prop in self._node_to_prop[id]:
                return self._node_to_prop[id][prop]
        return default

    # TODO should be deprecated like the below
    def extract_classed_from_dict(self, prop_d, viewer=None, default=None):
        if type(prop_d) is not dict:
            if prop_d is None:
                return default
            return prop_d
        if viewer is not None:
            viewer_class = self.get_prop(viewer, 'class')
            if viewer_class in prop_d:
                return prop_d[viewer_class]
            for viewer_class in self.get_prop(viewer, 'classes'):
                if viewer_class in prop_d:
                    return prop_d[viewer_class]
        if 'default' not in prop_d:
            return default
        return prop_d['default']

    # TODO should be deprecated - we may replace this with a model that
    # operates on the observation end of an agent to alter what they see
    def get_classed_prop(self, id, prop, viewer, default=None):
        prop_d = self.get_prop(id, prop)
        val = self.extract_classed_from_dict(prop_d, viewer, default)
        if type(val) is dict and 'iter' in val:
            i = val['iter']
            val['iter'] = (i + 1) % len(val['data'])
            return val['data'][i]
        return val

    def get_props_from_either(self, id1, id2, prop):
        '''Try to get ones own prop, fallback to other's prop. Do this for
        both provided ids symmetrically'''
        resp1 = self.get_prop(id1, prop, self.get_prop(id2, prop))
        resp2 = self.get_prop(id2, prop, self.get_prop(id1, prop))
        return resp1, resp2

    def set_prop(self, id, prop, val=True):
        '''Set a prop to a given value, True otherwise'''
        if id in self._node_to_prop:
            self._node_to_prop[id][prop] = val

    def has_prop(self, id, prop):
        '''Return whether or not id has the given prop'''
        if self.get_prop(id, prop) is not None:
            return True
        return False

    def inc_prop(self, id, prop, val=1):
        '''Increment a given prop by the given value'''
        if id in self._node_to_prop:
            if prop not in self._node_to_prop[id]:
                self.set_prop(id, prop, 0)
            if type(self._node_to_prop[id][prop]) != int:
                self.set_prop(id, prop, 0)
            self._node_to_prop[id][prop] += val

    def delete_prop(self, id, prop):
        '''Remove a prop from the node_to_prop map'''
        if id in self._node_to_prop:
            if prop in self._node_to_prop[id]:
                del self._node_to_prop[id][prop]

    def add_class(self, object_id, class_name):
        curr_classes = self.get_prop(object_id, 'classes')
        curr_classes.append(class_name)

    def remove_class(self, object_id, class_name):
        curr_classes = self.get_prop(object_id, 'classes')
        curr_classes.remove(class_name)

    # -- Graph locators -- #

    def location(self, thing):
        '''Get whatever the immediate container of a node is'''
        if thing in self._node_contained_in:
            return self._node_contained_in[thing]
        else:
            return None

    def room(self, thing):
        '''Get the room that contains a given node'''
        if thing not in self._node_contained_in:
            return None
        id = self._node_contained_in[thing]
        while not self.get_prop(id, 'room'):
            id = self._node_contained_in[id]
        return id

    def get_available_actions_fast(self, agent_id):
        '''Get available actions quickly, some of these may not be possible.
        NOTE: Jack can clean up later, but this seems to do everything need for NPCs
        right now. Essentially I think such a function shouldn't be using strings
        at all during reasoning, only ids all the way down until the last conversion
        to action strings, which the existing code didn't seem to do..?
        NOTE2: I've only included here actions actually in the LIGHT Turked dataset.
        Easy to add more of course, such as wield.
        This code is fairly fast (i measured like 10,000 calls in 0.8 secs).
        '''
        acts = []
        room_id = self.room(agent_id)
        nearby_ids = self.node_contains(room_id)
        carrying_ids = self.node_contains(agent_id)
        container_ids = []

        for id in nearby_ids:
            if id == agent_id:
                continue
            id_txt = self.node_to_desc(id).lower()
            if self.has_prop(id, 'agent'):
                acts.append('hit ' + id_txt)
                acts.append('hug ' + id_txt)
                acts.append('examine ' + id_txt)
                for id2 in carrying_ids:
                    id2_txt = self.node_to_desc(id2).lower()
                    acts.append('give ' + id2_txt + ' to ' + id_txt)
                neighbor_carrying_ids = self.node_contains(id)
                for id2 in neighbor_carrying_ids:
                    id2_txt = self.node_to_desc(id2).lower()
                    acts.append('steal ' + id2_txt + ' from ' + id_txt)
            if self.has_prop(id, 'object'):
                if not self.has_prop(id, 'not_gettable'):
                    acts.append('get ' + id_txt)
                if not self.has_prop(id, 'not_gettable') or self.has_prop(id, 'human'):
                    # objects are examinable,
                    # except for non-gettable by NPCs, as it's boring.
                    acts.append('examine ' + id_txt)
            if self.has_prop(id, 'container'):
                container_ids.append(id)

        for id in carrying_ids:
            if self.has_prop(id, 'container'):
                container_ids.append(id)

        for id in carrying_ids:
            id_txt = self.node_to_desc(id).lower()
            acts.append('examine ' + id_txt)
            acts.append('drop ' + id_txt)
            if self.has_prop(id, 'equipped'):
                acts.append('remove ' + id_txt)
            elif self.has_prop(id, 'wearable'):
                acts.append('wear ' + id_txt)
            if self.has_prop(id, 'food'):
                acts.append('eat ' + id_txt)
            if self.has_prop(id, 'drink'):
                acts.append('drink ' + id_txt)
            for id2 in container_ids:
                id2_txt = self.node_to_desc(id2).lower()
                acts.append('put ' + id_txt + ' in ' + id2_txt)

        for id in container_ids:
            id_txt = self.node_to_desc(id).lower()
            inside_ids = self.node_contains(id)
            for id2 in inside_ids:
                id2_txt = self.node_to_desc(id2).lower()
                acts.append('get ' + id_txt + ' from ' + id2_txt)

        return acts

    def desc_to_nodes(self, desc, nearbyid=None, nearbytype=None):
        '''Get nodes nearby to a given node from that node's perspective'''
        from_id = self.location(nearbyid)
        if nearbyid is not None:
            o = set()
            if 'all' in nearbytype and 'here' in nearbytype:
                o = self.get_local_ids(nearbyid)
            else:
                if 'path' in nearbytype:
                    o1 = self.node_path_to(from_id)
                    o = set(o).union(o1).union([from_id])
                if 'carrying' in nearbytype:
                    o = set(o).union(set(self.node_contains(nearbyid)))
                if 'sameloc' in nearbytype:
                    o1 = set(self.node_contains(from_id))
                    o = o.union(o1)
                if 'all' in nearbytype:
                    o1 = self.node_contains(nearbyid)
                    o2 = self.node_contains(from_id)
                    o3 = self.node_path_to(from_id)
                    o = o.union(o1).union(o2).union(o3)
                if 'contains' in nearbytype:
                    o = o.union({self.location(nearbyid)})
                if 'others' in nearbytype:
                    for item in o:
                        if self.get_prop(item, 'agent') \
                                or self.get_prop(item, 'container'):
                            o = o.union(self.node_contains(item))
                # if len(o) == 0:
                #     o1 = self.node_contains(nearbyid)
                #     o2 = self.node_contains(self.location(nearbyid))
                #     o = o1.union(o2)
        else:
            o = set(self._node_to_desc.keys())
        # Go through official in-game names
        if nearbyid is not None and self.room(nearbyid) in o and \
                desc == 'room':
            return [self.room(nearbyid)]
        found_pairs = [(id, self.node_to_desc(id, from_id=from_id).lower())
                       for id in o]
        valid_ids_1 = [(id, name) for (id, name) in found_pairs
                       if desc.lower() in name+'s']

        # Check the parent name trees for names that also could match in the
        # case that nothing could be found
        all_subnames = [(id, self.get_prop(id, 'names')) for id in o]
        all_pairs = [(id, name)
                     for (id, name_list) in all_subnames
                     for name in name_list]
        valid_ids_2 = [(id, name) for (id, name) in all_pairs
                       if desc.lower() in name+'s']

        valid_ids_1.sort(key=lambda x: len(x[0]))
        valid_ids_2.sort(key=lambda x: len(x[1]))
        valid_ids = valid_ids_1 + valid_ids_2
        valid_ids = [id for (id, _name) in valid_ids]
        return valid_ids

    def get_all_by_prop(self, prop):
        objects = self.all_node_ids()
        return [id for id in objects if self.get_prop(id, prop)]

    def node_path_to(self, id):
        if id is None:
            return []
        rooms = self._node_to_edges[id]
        rooms = [r[1] for r in rooms if r[0] == 'path_to']
        return rooms

    def get_actionable_ids(self, actor_id):
        o = self.get_local_ids(actor_id)
        new_o = set(o)
        for obj in o:
            if self.get_prop(obj, 'container') or self.get_prop(obj, 'agent'):
                new_o = new_o.union(self.node_contains(obj))
        return new_o

    def get_local_ids(self, actor_id):
        '''Return all accessible ids for an actor given the current area'''
        loc = self.location(actor_id)
        o1 = self.node_contains(actor_id)
        o2 = self.node_contains(loc)
        o3 = self.node_path_to(loc)
        o4 = [loc]
        local_ids = o1.union(o2).union(o3).union(o4)
        check_local_ids = list(local_ids)
        for pos_id in check_local_ids:
            if self.get_prop(pos_id, 'examined'):
                local_ids = local_ids.union(self.node_contains(pos_id))
        return local_ids

    # -- Text creators -- #

    def get_inventory_text_for(self, id, give_empty=True):
        '''Get a description of what id is carrying or equipped with'''
        s = ''
        carry_ids = []
        wear_ids = []
        wield_ids = []
        for o in self.node_contains(id):
            if self.get_prop(o, 'equipped'):
                if 'wearable' in self.get_prop(o, 'classes'):
                    wear_ids.append(o)
                elif 'weapon' in self.get_prop(o, 'classes'):
                    wield_ids.append(o)
            else:
                carry_ids.append(o)
        if len(carry_ids) + len(wield_ids) + len(wear_ids) == 0:
            if not give_empty:
                return ''

        if len(carry_ids) == 0:
            s += 'carrying nothing'
        else:
            s += 'carrying ' + self.display_node_list(carry_ids)
        if len(wear_ids) > 0:
            s += ',\n'
            if len(wield_ids) == 0:
                s += 'and '
            s += 'wearing ' + self.display_node_list(wear_ids)
        if len(wield_ids) > 0:
            s += ',\nand wielding ' + self.display_node_list(wield_ids)
        return s + '.'

    def health(self, id):
        '''Return the text description of someone's numeric health'''
        health = self.get_prop(id, 'health')
        if health is None or health is False:
            health = 1
        if health > 8:
            health = 8
        f = ['dead', 'on the verge of death',
             'very weak', 'weak', 'ok',
             'good', 'strong', 'very strong',
             'nigh on invincible']
        return f[int(health)]

    # -- Text accessors -- #

    def get_action_history(self, agent_id):
        observations = []
        while len(self._node_to_observations[agent_id]) > 0:
            observations.append(self._node_to_observations[agent_id].pop(0))
        return observations

    def node_to_desc(self, id, from_id=False, use_the=False, drop_prefix=False):
        if from_id:
            # A description of something (right now, a location)
            # from another location.
            # This gets the description from the path edge.
            path_desc = self.path_to_desc(id, from_id)
            if path_desc is not False:
                if path_desc.startswith('the') or path_desc.startswith('a'):
                    return path_desc
                return 'the ' + path_desc

        if id in self._node_to_desc:
            ent = self._node_to_desc[id]
            if self.get_prop(id, 'capitalize', False) is True:
                ent = ent.capitalize()
            if self.has_prop(id, 'dead'):
                ent = 'dead ' + ent
            if self.has_prop(id, 'player_name'):
                ent = self.get_prop(id, 'player_name')
            elif self.has_prop(id, 'agent') or self.has_prop(id, 'object'):
                prefix = self.name_prefix(id, ent, use_the)
                if prefix is not '' and not drop_prefix:
                    # -- clean up data, TODO: shouldn't need this?
                    if ent.lower().startswith('a '):
                        ent = ent[2:]
                    if ent.lower().startswith('an '):
                        ent = ent[3:]
                    if ent.lower().startswith('the '):
                        ent = ent[4:]
                    # ---- end clean up --------------
                    ent = prefix + ' ' + ent
            elif self.has_prop(id, 'room'):
                prefix = self.name_prefix(id, ent, use_the)
                if prefix is not '':
                    ent = prefix + ' ' + ent
                else:
                    ent = 'the ' + ent
            return ent
        else:
            return id

    def get_path_ex_desc(self, id1, id2, looker_id=None):
        '''Return a path description. If both ids are the same return the
        room description instead.
        '''
        if id1 == id2:
            if looker_id is not None:
                desc = self.get_classed_prop(id1, 'desc', looker_id)
                extra_desc = \
                    self.get_classed_prop(id1, 'extra_desc', looker_id)
                return extra_desc if extra_desc is not None else desc
            desc = self.get_prop(id1, 'desc')
            return self.get_prop(id1, 'extra_desc', desc)
        desc_set = self._node_to_edges[id1][('path_to', id2)]['examine_desc']
        val = self.extract_classed_from_dict(desc_set, looker_id)
        if type(val) is dict and 'iter' in val:
            i = val['iter']
            val['iter'] = (i + 1) % len(val['data'])
            return val['data'][i]
        return val

    def path_to_desc(self, id1, id2):
        '''get the description for a path from the perspective of id2'''
        rooms = self._node_to_edges[id2]
        for r in rooms:
            if r[0] == 'path_to' and r[1] == id1:
                if 'label' in rooms[r] and rooms[r]['label'] is not None:
                    if rooms[r]['full_label']:
                        return rooms[r]['label']
                    else:
                        return 'a path to the ' + rooms[r]['label']
        return False

    def node_to_desc_raw(self, id, from_id=False):
        if from_id:
            path_desc = self.path_to_desc(id, from_id)
            if path_desc is not False:
                return path_desc
        return self._node_to_desc[id]

    def name_prefix(self, id, txt, use_the):
        '''Get the prefix to prepend an object with in text form'''
        # Get the preferred prefix type.
        pre = self.get_prop(id, 'name_prefix')
        if pre == '':
            return pre

        if use_the is True:
            return 'the'

        if pre is False or pre is None or pre == 'auto':
            txt = 'an' if txt[0] in ['a', 'e', 'i', 'o', 'u'] else 'a'
            return txt
        return pre

    # -- Messaging commands -- #

    def send_action(self, agent_id, action):
        '''Parse the action and send it to the agent with send_msg'''
        if action['caller'] is None:
            val = \
                self.extract_classed_from_dict(action['txt'], agent_id, '')
            if type(val) is dict and 'iter' in val:
                i = val['iter']
                val['iter'] = (i + 1) % len(val['data'])
                extracted_text = val['data'][i]
            else:
                extracted_text = val
            self.send_msg(agent_id, extracted_text, action)
            return
        try:
            func_wrap = GRAPH_FUNCTIONS[action['caller']]
        except BaseException:
            func_wrap = CONSTRAINTS[action['caller']]
        try:
            t = func_wrap.format_observation(self, agent_id, action).rstrip()
        except Exception:
            # self.send_msg(agent_id, "You can't do that.")
            return  # the agent doesn't accept observations
        t += ' '
        self.send_msg(agent_id, t, action)

    def extract_action(self, agent_id, action):
        """
        Parse the given action and provide a graph-independent version
        of that action for consumption by other apis
        """
        new_action = action.copy()
        if action['caller'] is None:
            val = \
                self.extract_classed_from_dict(action['txt'], agent_id, '')
            if type(val) is dict and 'iter' in val:
                i = val['iter']
                val['iter'] = (i + 1) % len(val['data'])
                extracted_text = val['data'][i]
            else:
                extracted_text = val
            new_action['text'] = extracted_text
        else:
            try:
                func_wrap = GRAPH_FUNCTIONS[action['caller']]
            except BaseException:
                func_wrap = CONSTRAINTS[action['caller']]
            try:
                t = func_wrap.format_observation(self, agent_id, action).rstrip()
            except Exception:
                return  # the agent doesn't accept observations
            t += ' '
            new_action['text'] = t
        for field_name in new_action.keys():
            if type(new_action[field_name]) is set:
                new_action[field_name] = list(new_action[field_name])
        new_action['text_actors'] = [
            self.node_to_desc(a) for a in new_action.get('actors', [])
        ]

        return new_action

    def send_msg(self, agent_id, txt, action=None):
        '''Send an agent an action and a message'''
        if agent_id in self._node_to_text_buffer:
            if action is None:
                action = {
                    'caller': None,
                    'room_id': self.location(agent_id),
                    'txt': txt,
                }

            if not hasattr(self, '_node_to_observations'):
                # TODO remove when all the samples are converted
                self._node_to_observations = {}
            if agent_id not in self._node_to_observations:
                self._node_to_observations[agent_id] = []
            self._node_to_observations[agent_id].append(action)
            self._node_to_text_buffer[agent_id] += txt
        pos_playerid = self.agentid_to_playerid(agent_id)
        if pos_playerid in self.__message_callbacks:
            self.__message_callbacks[pos_playerid](self, action)

    def broadcast_to_room(self, action, exclude_agents=None, told_by=None):
        '''send a message to everyone in a room'''
        if exclude_agents is None:
            exclude_agents = []
        else:
            exclude_agents = list(exclude_agents)

        agents_list, _descs = self.get_room_agents(action['room_id'])
        agents = set(agents_list)
        if 'actors' in action:
            # send message to the actor first
            actor = action['actors'][0]
            if actor in agents and actor not in exclude_agents:
                self.send_action(actor, action)
                exclude_agents.append(actor)

        action['present_agent_ids'] = agents

        self._room_convo_buffers[action['room_id']].observe_turn(action)

        for a in agents:
            if a in exclude_agents:
                continue
            self.send_action(a, action)

    def broadcast_to_all_agents(self, action, exclude_agents=None, told_by=None):
        '''send a message to everyone '''
        if exclude_agents is None:
            exclude_agents = []
        else:
            exclude_agents = list(exclude_agents)
        agents_list, _descs = self.get_all_agents(action['room_id'])
        agents = set(agents_list)
        if 'actors' in action:
            # send message to the actor first
            actor = action['actors'][0]
            if actor in agents and actor not in exclude_agents:
                self.send_action(actor, action)
                exclude_agents.append(actor)
        action['present_agent_ids'] = agents
        for a in agents:
            if a in exclude_agents:
                continue
            self.send_action(a, action)

    # ----------------------------------------------------------------
    # TODO: Ideally, all functions below do not use the graph structure
    # directly but only the accessor functions (should not use self._node_* ).

    # -- Helpers -- #

    # TODO replace with assert_props which is just about validating world
    # constraints. Useful for testing
    def clean_props(self, object_id):
        '''ensures all necessary props are set on items that might not have
        been on earlier versions of graphworld
        '''
        # TODO remove when all samples are converted
        size = self.get_prop(object_id, 'size')
        if size is None or type(size) == bool:
            self.set_prop(object_id, 'size', 1)
        contain_size = self.get_prop(object_id, 'contain_size')
        if contain_size is None or type(contain_size) == bool:
            self.set_prop(object_id, 'contain_size', 3)
        classes = self.get_prop(object_id, 'classes')
        if type(classes) == str:
            self.set_prop(object_id, 'classes', [classes])
        elif type(classes) != list:
            self.set_prop(object_id, 'classes', [])

    # -- Commands -- #

    # Will be refactored at some point to actually work
    def create(self, agent_id, params):
        # -- create commands: --
        # *create room kitchen  -> creates room with path from this room
        # *create path kitchen  -> create path to that room from this one
        # *create agent orc
        # *create object ring
        # *create key golden key
        # create lockable tower with golden key
        # create container box
        # create [un]freeze
        # create reset/load/save [fname]
        # create rename <node> <value>    <-- **crashes*
        # create delete <node>
        # create set_prop orc to health=5
        from parlai_internal.tasks.graph_world3.class_nodes import \
            create_thing, CLASS_NAMES
        if not self.has_prop(agent_id, 'agent'):
            return False, 'create'
        if params is None:
            return False, 'create'
        room_id = self.room(agent_id)
        all_params = ' '.join(params)
        txt = ' '.join(params[1:])
        resp = 'create ' + ' '.join(params)
        if not (all_params in ['save', 'load', 'freeze', 'unfreeze']):
            if txt == '':
                return False, resp
        if params[0] == 'print':
            ids = self.desc_to_nodes(txt, nearbyid=agent_id, nearbytype='all')
            if len(ids) == 0:
                self.send_msg(agent_id, "Not found.\n ")
                return False, resp
            id = ids[0]
            self.send_msg(agent_id,
                          id + " has:\n{}".format(self._node_to_prop[id]))
            return True, resp
        if params[0] == 'save':
            self.save_graph(txt)
            self.send_msg(agent_id, "[ saved: " + self._save_fname + ' ]\n')
            return True, resp
        if params[0] == 'load' or params[0] == 'reset':
            self.load_graph(txt)
            self.send_msg(agent_id, "[ loaded: " + self._save_fname + ' ]\n')
            return True, resp
        if params[0] == 'freeze':
            self.freeze(True)
            self.send_msg(agent_id, "Frozen.\n")
            return True, resp
        if params[0] == 'unfreeze':
            self.freeze(False)
            self.send_msg(agent_id, "Unfrozen.\n")
            return True, resp
        if params[0] in ['delete', 'del', 'rm']:
            ids = self.desc_to_nodes(txt, nearbyid=agent_id, nearbytype='all')
            if len(ids) == 0:
                self.send_msg("Not found.\n ")
                return False, resp
            id = ids[0]
            self.delete_node(id)
            self.send_msg(agent_id, "Deleted.\n")
            return True, resp
        if params[0] == 'rename':
            params = self.split_params(params[1:], 'to')
            to_ids = self.desc_to_nodes(params[0], nearbyid=agent_id,
                                        nearbytype='all')
            if len(to_ids) == 0:
                self.send_msg(agent_id, "Not found.\n ")
                return False, resp
            to_id = to_ids[0]
            self.set_desc(to_id, params[1])
            self.send_msg(agent_id, "Done.\n")
            return True, resp
        if params[0] == 'agent':
            create_thing(self, room_id, params[0], force=True, use_name=txt)
            self.send_msg(agent_id, "Done.\n")
            return True, resp
        if params[0] == 'room':
            new_id = self.add_node(txt, params[0])
            self.add_path_to(new_id, room_id)
            self.set_prop(new_id, 'contain_size', 2000)
            self.send_msg(agent_id, "Done.\n")
            return True, resp
        if params[0] == 'set_prop':
            params = self.split_params(params[1:], 'to')
            to_ids = self.desc_to_nodes(params[0], nearbyid=agent_id,
                                        nearbytype='all')
            if len(to_ids) == 0:
                self.send_msg(agent_id, "Not found.\n ")
                return False, resp
            to_id = to_ids[0]
            key = params[1]
            value = True
            if '=' in key:
                sp = key.split('=')
                if len(sp) != 2:
                    return False, resp
                key = sp[0]
                value = sp[1]
                if value == 'True':
                    value = True
                try:
                    value = int(value)
                except ValueError:
                    pass
            self.set_prop(to_id, key, value)
            self.send_msg(agent_id, "Done.\n")
            return True, resp
        if (params[0] in CLASS_NAMES):
            if params[0] == 'key' and txt.find('key') == -1:
                self.send_msg(agent_id, "Keys must be called keys!\n")
                return False, resp
            create_thing(self, room_id, params[0], force=True, use_name=txt)
            self.send_msg(agent_id, "Done.\n")
            return True, resp
        if params[0] == 'lockable':
            ps = self.split_params(params[1:], 'with')
            if len(ps) != 2:
                return False, resp
            to_ids = self.desc_to_nodes(ps[0], nearbyid=agent_id,
                                        nearbytype='all')
            with_ids = self.desc_to_nodes(ps[1], nearbyid=agent_id,
                                          nearbytype='all')
            if len(to_ids) == 0 or len(with_ids) == 0:
                self.send_msg(agent_id, "Something was not found.\n ")
                return False, resp
            to_id = to_ids[0]
            with_id = with_ids[0]
            if not self.get_prop(with_id, 'key'):
                self.send_msg(agent_id, "You need to use a key!\n")
                return False, resp
            self.set_prop(to_id, 'locked_with', with_id)
            self.set_prop(to_id, 'locked', True)
            self.send_msg(agent_id, "Done.\n")
            return True, resp
        if params[0] == 'path':
            to_id = self.desc_to_nodes(txt)
            if to_id is False:
                return False, resp
            self.add_path_to(to_id, room_id)
            self.send_msg(agent_id, "Done.\n")
            return True, resp
        self.send_msg(agent_id, 'Create is not supported for: ' + resp)
        return False, resp

    # -- Create helpers -- #

    def split_params(self, params, word):
        '''
        Split an incoming param phrase by a splitword or list of splitwords
        '''
        if type(word) is str:
            word = {word}
        for w in word:
            search = ' {} '.format(w)
            phrase = ' '.join(params)
            if phrase.find(w) != -1:
                return phrase.split(search)
        return None

    # -- GraphFunction Helpers -- #

    def obj_fits(self, object_id, container_id):
        '''Return if one object will fit into another'''
        size = self.get_prop(object_id, 'size')
        max_size = self.get_prop(container_id, 'contain_size')
        if size is None or max_size is None:
            # TODO log these kinds of things
            print('None compare between {} and {}'.format(
                object_id, container_id), self._node_to_prop)
            return False
        return size <= max_size

    def move_object(self, object_id, container_id):
        '''Move an object from wherever it is into somewhere else'''
        size = self.get_prop(object_id, 'size')
        # Remove from the old container
        old_id = self.node_contained_in(object_id)
        if old_id is not None:
            contain_size = self.get_prop(old_id, 'contain_size')
            contain_size += size
            self.set_prop(old_id, 'contain_size', contain_size)
        # Put in the new container
        contain_size = self.get_prop(container_id, 'contain_size')
        contain_size -= size
        self.set_prop(container_id, 'contain_size', contain_size)
        self.add_contained_in(object_id, container_id)

    # TODO update to duplicate the agent as an object and remove agent instead
    def die(self, id):
        '''Update an agent into a dead state'''
        if not self.has_prop(id, 'agent'):
            return False
        if self.has_prop(id, 'human'):
            self.set_follow(id, None)
            room = self.location(id)
            add_text = ''
            contents = self.node_contains(id)
            skull_msg = emoji.emojize(':skull:')*31
            self.send_msg(id,
                          "\n" + skull_msg + "\n" +
                          "                      YOU ARE DEAD !!!       \n" +
                          skull_msg + "\n")

        agent_desc = self.node_to_desc(id, use_the=True).capitalize()
        descs = ['They look pretty dead.', 'They are very dead.', 'Their corpse is inanimate.' ]
        self.set_prop(id, 'desc', random.choice(descs))
        self.set_follow(id, None)
        self.set_prop(id, 'dead', True)
        self.delete_prop(id, 'agent')
        self.remove_class(id, 'agent')
        self.add_class(id, 'container')
        self.add_class(id, 'object')
        #removed for now until we fix delete bug:
        #self.add_class(id, 'food')
        self.set_prop(id, 'container')
        self.set_prop(id, 'object')
        #self.set_prop(id, 'food')
        self.set_prop(id, 'examined', True)
        self.broadcast_to_room({
            'caller': None,
            'name': 'died',
            'actors': [id],
            'room_id': self.location(id),
            'txt': agent_desc + ' died!\n',
            'room_agents': self.get_room_agents(self.location(id), drop_prefix=True)
        }, [id])
        return True

    def get_room_edge_text(self, room_descs, past=False):
        '''Get text for all the edges outside of a room'''
        if len(room_descs) == 1:
            if past:
                return 'There was ' + room_descs[0] + '.\n'
            else:
                return 'There\'s ' + room_descs[0] + '.\n'
        default_paths = [path[10:] for path in room_descs
                         if path.startswith('a path to')]
        non_default_paths = [path for path in room_descs
                             if not path.startswith('a path to')]
        if len(default_paths) == 0:
            if past:
                s = 'There was '
            else:
                s = 'There\'s '
            s += self.display_desc_list(non_default_paths)
            s += '.\n'
        elif len(non_default_paths) == 0:
            if past:
                s = 'There were paths to '
            else:
                s = 'There are paths to '

            s += self.display_desc_list(default_paths)
            s += '.\n'
        else:
            if past:
                s = 'There was '
            else:
                s = 'There\'s '
            s += ", ".join(non_default_paths)
            if len(default_paths) == 1:
                s += ', and a path to '
            else:
                s += ', and paths to '
            s += self.display_desc_list(default_paths)
            s += '.\n'
        return s

    def get_room_object_text(self, object_descs, ents, past=False,
                             give_empty=True):
        '''Get text for all the objects in a room'''
        s = ''
        tensed_is = 'was' if past else 'is'
        tensed_are = 'were' if past else 'are'
        loc = 'there' if past else 'here'
        if len(object_descs) == 0:
            if not give_empty:
                return ''
            s += 'It ' + tensed_is + ' empty.\n'
        elif len(object_descs) > 20:
            s += 'There ' + tensed_are + ' a lot of things here.\n'
        else:
            s += 'There\'s '
            s += self.display_desc_list(object_descs, ents)
            s += ' {}.\n'.format(loc)
        return s

    def get_room_agent_text(self, agent_descs, past=False):
        '''Get text for all the agents in a room'''
        loc = 'there' if past else 'here'
        you_are = 'You were ' if past else 'You are '
        is_tensed = ' was ' if past else ' is '
        are_tensed = ' were ' if past else ' are '
        count = len(agent_descs)
        if count == 0:
            return ''
        elif count == 1:
            if agent_descs[0] == 'you':
                return you_are + loc + '.\n'
            else:
                return agent_descs[0].capitalize() + is_tensed + loc + '.\n'
        elif count == 2:
            all_descs = ' and '.join(agent_descs).capitalize()
            return all_descs + are_tensed + loc + '.\n'
        else:
            before_and = ', '.join(agent_descs[:-1]).capitalize()
            all_descs = before_and + ', and ' + agent_descs[-1]
            return all_descs + are_tensed + loc + '.\n'

    def get_room_edges(self, room_id):
        '''Return a list of edges from a room and their current descriptions'''
        rooms = self._node_to_edges[room_id]
        rooms = [r[1] for r in rooms if r[0] == 'path_to']
        room_descs = [self.node_to_desc(ent, room_id) for ent in rooms]
        return rooms, room_descs

    def get_nondescribed_room_objects(self, room_id):
        '''Return a list of objects in a room and their current descriptions'''
        objects = self.node_contains(room_id)
        objects = [o for o in objects if self.get_prop(o, 'object')]
        objects = [o for o in objects
                   if 'described' not in self.get_prop(o, 'classes')]
        object_descs = [self.node_to_desc(o) for o in objects]
        return objects, object_descs

    def get_room_objects(self, room_id):
        '''Return a list of objects in a room and their current descriptions'''
        objects = self.node_contains(room_id)
        objects = [o for o in objects if self.get_prop(o, 'object')]
        object_descs = [self.node_to_desc(o) for o in objects]
        return objects, object_descs

    def get_nondescribed_room_agents(self, room):
        '''Return a list of agents in a room and their current descriptions
        if those agents aren't described in the room text'''
        agents = self.node_contains(room)
        agents = [a for a in agents if self.get_prop(a, 'agent')]
        agents = [a for a in agents
                  if 'described' not in self.get_prop(a, 'classes')]
        agent_descs = [self.node_to_desc(a) for a in agents]
        return agents, agent_descs

    def get_room_agents(self, room, drop_prefix=False):
        '''Return a list of agents in a room and their current descriptions'''
        agents = self.node_contains(room)
        agents = [a for a in agents if self.get_prop(a, 'agent')]
        agent_descs = [self.node_to_desc(a, drop_prefix=drop_prefix) for a in agents]
        return agents, agent_descs

    # TODO remove room argument? why is this here
    def get_all_agents(self, room, have_prop = 'human'):
        '''Return a list of all agents and their current descriptions'''
        agents = []
        for a in self._node_npcs:
            if self.get_prop(a, have_prop) and self.get_prop(a, 'agent'):
                agents.append(a)
        agents = [a for a in agents if self.get_prop(a, 'agent')]
        agent_descs = [self.node_to_desc(a) for a in agents]
        return agents, agent_descs

    # TODO replace with agents managing their own text rather than
    # keeping a local text buffer
    def get_text(self, agent, clear_actions=True):
        '''Get text from the text buffer for an agent, clear that buffer'''
        txt = ''
        if agent in self._node_to_text_buffer:
            txt = self._node_to_text_buffer[agent]
        self._node_to_text_buffer[agent] = ''  # clear buffer
        if clear_actions:
            self._node_to_observations[agent] = []  # clear buffer
        return txt

    def cnt_obj(self, obj, c, ents=None):
        '''Return a text form of the count of an object'''
        cnt = c[obj]
        if cnt == 1:
            return obj
        else:
            if ents is not None:
                if self.get_prop(ents[obj], 'plural') is not None:
                    words = self.get_prop(ents[obj], 'plural').split(' ')
                else:
                    if obj[-1] != 's':
                        words = (obj + 's').split(' ')
                    else:
                        words = (obj).split(' ')
            f = ['two', 'three', 'four', 'five', 'six', 'seven', 'eight',
                 'nine', 'a lot of']
            cnt = cnt - 2
            if cnt > 8:
                cnt = 8
            cnt = f[cnt]
            if words[0] == 'some':
                return ' '.join(words)
            else:
                return cnt + ' ' + ' '.join(words[1:])

    def display_desc_list(self, descs, ents=None):
        if len(descs) == 0:
            return 'nothing'
        if len(descs) == 1:
            return descs[0]
        c = Counter(descs)
        unique_items = set(descs)
        s = ''
        cnt = 0
        for obj in unique_items:
            s += self.cnt_obj(obj, c, ents)
            if len(unique_items) > 2 and cnt < len(unique_items) - 1:
                s += ','
            s += ' '
            cnt = cnt + 1
            if cnt == len(unique_items) - 1:
                s += 'and '
        return s.rstrip(' ')

    def display_node_list(self, l, from_id=False):
        desc_to_ent = {self.node_to_desc(ent, from_id): ent for ent in l}
        descs = [self.node_to_desc(ent, from_id) for ent in l]
        return self.display_desc_list(descs, desc_to_ent)

    def display_node(self, id):
        if self.get_prop(id, 'surface_type') == 'on':
            contents = self.node_contains(id)
            content_desc = self.display_node_list(contents)
            obj_desc = self.node_to_desc(id, use_the=True)
            return "There's {} on {}".format(content_desc, obj_desc)
        else:
            s = self.node_to_desc(id, use_the=True).capitalize() + ' contains '
            contents = self.node_contains(id)
            return s + self.display_node_list(contents) + '.\n'

    def help(self):
        #scroll_line = "="*40 + '\n'
        scroll_line = ((emoji.emojize(':scroll:', use_aliases=True) + ' ')*20) + '\n'
        txt = (
            ('You pull some scribbled notes on a torn manuscript out of your pocket.\n' +
             'It reads:\n')  +
            scroll_line +
            ('Thine Commands:\n') +
            scroll_line +
            ('say/shout "<thing you want to say>; or use quotes only for short "\n'
             'tell/whisper <agent> "<something>"\n'
             'look (l, for short)\n'
             'go <direction>, e.g. "go north", or "go n" or just "n" for short\n'
             'inventory (i or inv, for short)\n'
             'status/health\n'
             'examine <thing> (ex, for short)\n'
             'get/drop <object>\n'
             'eat/drink <object>\n'
             'wear/remove <object>\n'
             'wield/unwield <object>\n'
             'lock/unlock <object> with <object>\n'
             'follow <agent>\n'
             'hit <agent>\n'
             'put <object> in <container>\n'
             'get <object> from <container>\n'
             'give <object> to <agent>\n'
             'steal <object> from <agent>\n'
             'emotes: laugh,cry,smile,ponder,blush,shrug,sigh,\n'
             '        wink,yawn,wave,stare,scream,pout,nudge,nod,\n'
             '        growl,groan,grin,gasp,frown,dance,applaud\n') +
            scroll_line
        )
        #((emoji.emojize(':scroll:', use_aliases=True) + ' ')*20) + '\n')
        return txt

    def print_graph(self, start_node, agentid, visited=False):

        return self._graph_printer.print(self, start_node, agentid, visited)

    def args_to_descs(self, args):
        loc = self.location(args[0])
        return [self.node_to_desc_raw(i, from_id=loc) for i in args]

    # TODO replace someday with something that isn't n^3
    def get_possible_actions(self, my_agent_id='dragon', use_actions=None):
        if self.get_prop(my_agent_id, 'dead'):
            return []
        o = self.get_actionable_ids(my_agent_id)
        final_o = o
        for item in o:
            if self.get_prop(item, 'agent') \
                    or self.get_prop(item, 'container'):
                final_o = final_o.union(self.node_contains(item))
        actions = []
        use_functions = CANNONICAL_GRAPH_FUNCTIONS.items()
        if use_actions is not None:
            use_functions = [
                (fn, func) for (fn, func) in use_functions
                if fn in use_actions]
        for func_name, func in use_functions:
            if func_name in FUNC_IGNORE_LIST:
                continue  # Ignore functions we don't want to expose directly
            args = [my_agent_id]
            if func.valid_args(self, args):
                canon = func.get_canonical_form(self, args)
                actions.append(canon)
            for id1 in final_o:
                if id1 == my_agent_id:
                    continue
                args = [my_agent_id, id1]
                if func.valid_args(self, args):
                    canon = func.get_canonical_form(self, args)
                    actions.append(canon)
                for id2 in final_o:
                    if id2 == my_agent_id:
                        continue
                    args = [my_agent_id, id1, id2]
                    if func.valid_args(self, args):
                        canon = func.get_canonical_form(self, args)
                        actions.append(canon)
        return list(set(actions))

    @staticmethod
    def parse_static(inst):
        inst = inst.strip().split()
        symb_points = [0]
        return inst, symb_points

    @staticmethod
    def filter_actions(inst):
        ret_actions = []
        inst, symb_points = Graph.parse_static(inst)
        for i in range(len(symb_points) - 1):
            j, k = symb_points[i], symb_points[i + 1]
            if inst[j].lower() in GRAPH_FUNCTIONS.keys():
                ret_actions.append(' '.join(inst[j: k]))
        return ' '.join(ret_actions), ret_actions

    def parse(self, inst):
        return Graph.parse_static(inst)

    def canonical_action(self, agentid, inst):
        words = inst.split(' ')
        if (words[0].lower() in GRAPH_FUNCTIONS.keys()):
            func_wrap = GRAPH_FUNCTIONS[words[0].lower()]
            valid, args, _canon_args = \
                func_wrap.parse_text_to_args(self, agentid, words[1:])
            if not valid:
                return False, inst
            return True, func_wrap.get_canonical_form(self, args)
        return False, inst

    def help_message(self):
        h = [
            '',
            ' Have you tried typing help?',
        ]
        return random.choice(h)

    def valid_exec(self, agentid, inst=None):
        if inst is None:
            inst = agentid
            agentid = 'dragon'

        if self.get_prop(agentid, 'dead'):
            return False

        inst, symb_points = self.parse(inst)
        inst[0] = inst[0].lower()

        if len(inst) == 1 and (inst[0] == 'help'):
            return True

        if inst[0] not in GRAPH_FUNCTIONS.keys():
            return False

        for i in range(len(symb_points) - 1):
            j, k = symb_points[i], symb_points[i + 1]
            params = inst[j + 1: k]
            if (inst[j].lower() in GRAPH_FUNCTIONS.keys()):
                func_wrap = GRAPH_FUNCTIONS[inst[j].lower()]
                valid, args, _canon_args = \
                    func_wrap.parse_text_to_args(self, agentid, params)
                if not valid:
                    return False
            else:
                return False
        return True

    def parse_exec(self, agentid, inst=None):
        try:
            return self.parse_exec_internal(agentid, inst)
        except Exception:
            self.send_msg(agentid, "Strange magic is afoot. This failed for some reason...")
            return False, "FailedParseExec"

    def parse_exec_internal(self, agentid, inst=None):
        """ATTENTION: even if one of the actions is invalid, all actions
        before that will still be executed (the world state will be changed)!
        """
        # basic replacements
        inst = inst.rstrip('\n').rstrip('\r')
        parse_shortcuts = {
            'e':'go east', 'w':'go west', 'n':'go north', 's':'go south',
            'ex self':'inv', 'examine self':'inv'
        }
        if inst in parse_shortcuts:
            inst = parse_shortcuts[inst]
        if inst.startswith('"'):
            inst = 'say ' + inst
        if inst.startswith('look '):
            inst = 'look'

        inst, symb_points = self.parse(inst)

        if (len(inst) == 1 and ((inst[0] == "respawn") or (inst[0] == "*respawn*"))
            and self.get_prop(agentid, 'human') and
        self.get_prop(agentid, 'dead')):
            self.respawn_player(agentid)
            return True, "Respawn"
        if self.get_prop(agentid, 'dead'):
            self.send_msg(agentid,
                          "You are dead, you can't do anything, sorry.\nType *respawn* to try at life again.\n")
            return False, 'dead'

        if inst == []:
            errs = ['Huh?', 'What?', 'Are you going to type anything?', 'Maybe try help...?', 'Sigh.']
            self.send_msg(agentid, random.choice(errs))
            return False

        inst[0] = inst[0].lower()

        # for i in self.all_node_ids():
        #     self.clean_props(i)

        hint_calls = ['a', 'actions', 'hints']
        if len(inst) == 1 and (inst[0] in hint_calls):
            # TODO remove the list of valid instructions from the main game,
            # Perhaps behind an admin gatekeeper of sorts
            self.send_msg(agentid, '\n'.join(
                sorted(self.get_possible_actions(agentid))) + '\n')
            return True, 'actions'
        if len(inst) == 1 and (inst[0] == 'help'):
            self.send_msg(agentid, self.help())
            return True, 'help'
        if len(inst) == 1 and (inst[0] == "map"):
            self.send_msg(agentid, self.print_graph(self.room(agentid), agentid, visited=False))
            return True, "Print graph"
        if len(inst) == 1 and (inst[0] == "fogmap"):
            self.send_msg(agentid, self.print_graph(self.room(agentid), agentid, visited=True))
            return True, "Print graph"
        if len(inst) == 2 and (inst[0] == "commit") and (inst[1] == "suicide"):
            self.send_msg(agentid, "You commit suicide!")
            self.die(agentid)
            return True, "Suicide"

        # if inst[0] == 'create':
        #     return self.create(agentid, inst[1:])
        if inst[0] not in GRAPH_FUNCTIONS.keys():
            if Callbacks.handle_failed_parse_callbacks(
                    inst[0].lower(), self, inst[1:], agentid):
                return False, inst[0]
            self.send_msg(agentid, "You can't {}.{}".format(inst[0], self.help_message()))
            return False, inst[0]
        acts = []
        j = 0
        k = len(inst)
        params = inst[j + 1: k]
        if (inst[j].lower() in GRAPH_FUNCTIONS.keys()):
            func_wrap = GRAPH_FUNCTIONS[inst[j].lower()]
            valid, args, _canon_args = \
                func_wrap.parse_text_to_args(self, agentid, params)
            if not valid:
                if Callbacks.handle_failed_parse_callbacks(
                        func_wrap.get_name(), self, params, agentid):
                    return False, ' '.join(acts)
                if type(args) is str:
                    self.send_msg(agentid, args)
                else:
                    #self.send_msg(agentid, "You can't do that.")
                    self.send_action(agentid, args)
                return False, ' '.join(acts)
            new_act = func_wrap.get_canonical_form(self, args)
            try:
                success = func_wrap.handle(self, args)
            except Exception:
                success = False
            acts.append(new_act)
            if not success:
                return False, ' '.join(acts)
        elif Callbacks.handle_failed_parse_callbacks(
                inst[j].lower(), self, params, agentid):
            return False, ' '.join(acts)
        else:
            return False, ' '.join(acts)
        return True, ' '.join(acts)

    def spawn_player(self, existing_player_id = -1):
        # choose an agent to spawn into
        a_id = -1
        for agent_id in self._node_npcs:
            if (not self.get_prop(agent_id, 'human') and
                not self.get_prop(agent_id,  'dead') and
                self.get_prop(agent_id,  'agent') and
                self.get_prop(agent_id, 'speed') > 0):
                a_id = agent_id
                break
        if a_id != -1:
            self.set_prop(a_id, 'human')
            # self.parse_exec(a_id, "examine " + str(a_id))
            self.get_text(a_id).rstrip('\n') # clear buffer
            msg_txt = ''
            if existing_player_id != -1:
                msg_txt += "Your lost soul attempts to join the living...\n"
            sun_txt = emoji.emojize(':star2:', use_aliases=True)*31
            msg_txt += sun_txt + "\n"
            msg_txt += "You are spawned into this world as " + self.node_to_desc(a_id) + ".\n"
            msg_txt += "Your character:\n"
            msg_txt += self.get_prop(a_id, 'persona') + "\n"
            # msg_txt += self.get_prop(a_id, 'desc') + "\n"
            msg_txt += sun_txt + "\n"
            action = {
                'caller': None,
                'name': 'persona',
                'room_id': self.location(a_id),
                'txt': msg_txt,
                'actors': [a_id],
                'character': self.node_to_desc(a_id),
                'persona': self.get_prop(a_id, 'persona'),
            }
            self.send_action(a_id, action)
        else:
            if existing_player_id != -1:
                # send message that we can't respawn
                aid = self.playerid_to_agentid(existing_player_id)
                self.send_msg(aid,
                              "Your lost soul attempts to join the living...but the path is blocked.\n")
            return -1
        if existing_player_id == -1:
            self._player_cnt += 1
            p_id = "_player_" + str(self._player_cnt)
        else:
            p_id = existing_player_id
        self.set_prop(a_id, 'player_id', p_id)
        self._playerid_to_agentid[p_id] = a_id
        self._agentid_to_playerid[a_id] = p_id
        self._last_rooms[a_id] = None
        self._room_convo_buffers[self.room(a_id)].enter_human()
        return p_id

    def playerid_to_agentid(self, pid):
        return self._playerid_to_agentid[pid]

    def agentid_to_playerid(self, aid):
        return self._agentid_to_playerid.get(aid)

    def respawn_player(self, a_id):
        p_id = self.get_prop(a_id, 'player_id')
        if p_id != -1:
            self.set_prop(a_id, 'player_id', -1)
            p_id2 = self.spawn_player(existing_player_id = p_id)
            new_a_id = self.playerid_to_agentid(p_id2)
            self.parse_exec(new_a_id, 'look')

    def possibly_clean_corpse(self, id):
        ticks = self.get_prop(id, 'death_ticks', 0)
        self.set_prop(id, 'death_ticks', ticks + 1)
        # After N ticks, we clean up the corpse.
        if ticks < 20:
            return
        self._npc_names.remove(self._node_to_desc[id])
        agent_desc = self.node_to_desc(id, use_the=True).capitalize()
        self.broadcast_to_room({
            'caller': None,
            'room_id': self.location(id),
            'txt': agent_desc + ' corpse disintegrates in a puff of magic.\n',
        }, [id])
        # Possibly spawn in a new agent
        self.world.add_random_new_agent_to_graph(self)
        self.delete_node(id)

    def update_world(self):
        # move all the agents and junk, unless world frozen
        if self.freeze():
            return
        live_npcs = 0
        for agent_id in self._node_npcs.copy():
            if self.get_prop(agent_id, 'human'):
                continue
            if self.get_prop(agent_id, 'dead'):
                self.possibly_clean_corpse(agent_id)
                continue
            if not self.get_prop(agent_id, 'agent'):
                continue
            live_npcs += 1
            self.npc_models.npc_act(agent_id)

        # Delete any nodes left in the queue to be deleted.
        # It's better to do this here outside the loop above where the nodes might be used.
        self.delete_nodes()
        if live_npcs < self._initial_num_npcs:
            # add a new NPC as we don't have enough left alive!
            # print("adding new npc as total is: " + str(live_npcs))
            self.world.add_random_new_agent_to_graph(self)
