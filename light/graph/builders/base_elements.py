#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import copy, itertools
from parlai_internal.projects.light.v1.graph_builders.db_utils import id_is_usable
from parlai_internal.projects.light.v1.data_model.light_database import (
    LIGHTDatabase,
    DB_TYPE_ROOM,
    DB_TYPE_CHAR,
    DB_TYPE_OBJ,
    DB_STATUS_REJECTED,
    DB_EDGE_IN_CONTAINED,
    DB_EDGE_EX_CONTAINED,
    DB_EDGE_CONTAINED_IN,
    DB_EDGE_WORN,
    DB_EDGE_WIELDED,
    DB_EDGE_NEIGHBOR,
)


class DBElement(object):
    '''Abstract class that defines a method for building database elements 
    that are used to populate graphs. All database elements will adhere to 
    a standard interface'''

    def __init__(self, db_path, id, cache=None):
        '''Intialize databse for later queries '''
        self.db_path = db_path
        self.id = id
        self.__data_split = None
        self.text_edge_cache = None
        self.db_edge_cache = None
        self.use_cache = False
        if cache is not None:
            self.cache = cache
            self.use_cache = True
            self.text_edge_cache = self.cache['text_edges']
            self.db_edge_cache = self.cache['db_edges']
            # self.__data_split = cache['id'][self.id]['split']

    def get_text_edges(self, type=None):
        '''Return a list of text edges (child_text) given the id 
        of  parent node and type of connection'''
        if self.use_cache:
            text_edges_list = []
            if self.id in self.text_edge_cache:
                filtered = self.text_edge_cache[self.id]
                if type is not None:
                    filtered = [f for f in filtered if f['edge_type'] == type]
                text_edges_list = [edge['child_text'] for edge in filtered]
            return text_edges_list
        with LIGHTDatabase(self.db_path) as ldb:
            text_edges_list = [
                edge['child_text']
                for edge in ldb.get_text_edge(parent_id=self.id, edge_type=type)
                if id_is_usable(ldb, edge['id'])
            ]
        return text_edges_list

    def get_db_edges(self, type=None, return_child=True, parent_type=None):
        '''Return a list of database edges (child_id is return_child is True else parent_id)
        given the id of  parent node and type of connection'''
        if return_child:
            return_id = 'child_id'
        else:
            return_id = 'parent_id'
        if self.db_edge_cache is not None:
            filtered = []
            if return_child and self.id in self.db_edge_cache:
                filtered = [
                    edge['child_id']
                    for edge in self.db_edge_cache[self.id]
                    if edge['edge_type'] == type
                ]
            else:
                if parent_type is not None:
                    filtered = list(
                        itertools.chain.from_iterable(
                            [rows for rows in self.db_edge_cache.values()]
                        )
                    )
                    filtered = [
                        row['parent_id']
                        for row in filtered
                        if row['type'] == type
                        and row['child_id'] == self.id
                        and self.cache['id'][row['parent_id']]['edge_type']
                        == parent_type
                    ]
            return filtered

        with LIGHTDatabase(self.db_path) as ldb:
            if parent_type is not None:
                db_edges_list = [
                    edge[return_id]
                    for edge in ldb.get_node_content(child_id=self.id, edge_type=type)
                    if id_is_usable(ldb, edge['id'])
                    and ldb.get_id(edge['parent_id'])[0]['type'] == parent_type
                ]
            else:
                db_edges_list = [
                    edge[return_id]
                    for edge in ldb.get_node_content(parent_id=self.id, edge_type=type)
                    if id_is_usable(ldb, edge['id'])
                ]
        return db_edges_list

    @property
    def data_split(self):
        if self.__data_split is None:
            with LIGHTDatabase(self.db_path) as ldb:
                self.__data_split = ldb.get_id(self.id)[0]['split']
        return self.__data_split


class DBRoom(DBElement):
    '''Instantiate a LightDB representation of a room'''

    def __init__(self, db_path, room_id, cache=None):
        '''Takes in the database path and a valid room_id 
        and initialize base fields of a room'''
        super(DBRoom, self).__init__(db_path, room_id, cache)
        if self.use_cache:
            room = cache['rooms'][room_id]
        else:
            with LIGHTDatabase(self.db_path) as ldb:
                room = ldb.get_room(id=room_id)[0]
        self.db_id = room_id
        self.setting = room['name']
        self.description = room['description']
        self.background = room['backstory']
        self.loc = None
        self.g_id = None
        self.possible_connections = {}
        self.base_id = room['base_id']
        self.__ex_objects = None
        self.__in_objects = None
        self.__ex_characters = None
        self.__in_characters = None
        self.__category = None
        if self.use_cache:
            self.__category = self.cache['base_rooms'][self.base_id]['name']
        self.__neighbors = None

    @property
    def ex_objects(self):
        if self.__ex_objects is None:
            all_ex_edges = self.get_db_edges(DB_EDGE_EX_CONTAINED)
            if self.use_cache:
                db_ex_objs = [
                    id
                    for id in all_ex_edges
                    if self.cache['id'][id]['type'] == DB_TYPE_OBJ
                ]
            else:
                with LIGHTDatabase(self.db_path) as ldb:
                    db_ex_objs = [
                        e
                        for e in all_ex_edges
                        if ldb.get_id(e)[0]['type'] == DB_TYPE_OBJ
                    ]
            all_ex_text_edges = self.get_text_edges(DB_EDGE_EX_CONTAINED)
            self.__ex_objects = {'db': db_ex_objs, 'text': all_ex_text_edges}
        return self.__ex_objects.copy()

    @property
    def in_objects(self):
        if self.__in_objects is None:
            all_in_edges = self.get_db_edges(DB_EDGE_IN_CONTAINED)
            if self.use_cache:
                db_in_objs = [
                    id
                    for id in all_in_edges
                    if self.cache['id'][id]['type'] == DB_TYPE_OBJ
                ]
            else:
                with LIGHTDatabase(self.db_path) as ldb:
                    db_in_objs = [
                        e
                        for e in all_in_edges
                        if ldb.get_id(e)[0]['type'] == DB_TYPE_OBJ
                    ]
            all_in_text_edges = self.get_text_edges(DB_EDGE_IN_CONTAINED)
            self.__in_objects = {'db': db_in_objs, 'text': all_in_text_edges}
        return self.__in_objects.copy()

    @property
    def ex_characters(self):
        if self.__ex_characters is None:
            all_ex_edges = self.get_db_edges(DB_EDGE_EX_CONTAINED)
            if self.use_cache:
                db_ex_chars = [
                    id
                    for id in all_ex_edges
                    if self.cache['id'][id]['type'] == DB_TYPE_CHAR
                ]
            else:
                with LIGHTDatabase(self.db_path) as ldb:
                    db_ex_chars = [
                        e
                        for e in all_ex_edges
                        if ldb.get_id(e)[0]['type'] == DB_TYPE_CHAR
                    ]
            self.__ex_characters = {'db': db_ex_chars}
        return self.__ex_characters.copy()

    @property
    def in_characters(self):
        if self.__in_characters is None:
            all_in_edges = self.get_db_edges(DB_EDGE_IN_CONTAINED)
            if self.use_cache:
                db_in_chars = [
                    id
                    for id in all_in_edges
                    if self.cache['id'][id]['type'] == DB_TYPE_CHAR
                ]
            else:
                with LIGHTDatabase(self.db_path) as ldb:
                    db_in_chars = [
                        e
                        for e in all_in_edges
                        if ldb.get_id(e)[0]['type'] == DB_TYPE_CHAR
                    ]
            self.__in_characters = {'db': db_in_chars}
        return self.__in_characters.copy()

    @property
    def category(self):
        if self.__category is None:
            with LIGHTDatabase(self.db_path) as ldb:
                self.__category = ldb.get_base_room(self.base_id)[0]['name']
        return self.__category

    @property
    def neighbors(self):
        if self.__neighbors is None:
            self.__neighbors = self.get_text_edges(type=DB_EDGE_NEIGHBOR)
        return self.__neighbors.copy()

    def room_features(self, globalFull, full=False):
        '''Get text feature for a DBRoom'''
        if globalFull:
            full = True
        str = ''
        str += self.setting
        if full:
            str += f'. {self.category}. {self.description} {self.background}'
        return str.rstrip()


class DBObject(DBElement):
    '''Instantiate a LightDB representation of an Object'''

    def __init__(self, db_path, object_id, cache=None):
        super(DBObject, self).__init__(db_path, object_id, cache)
        if self.use_cache:
            obj = cache['objects'][object_id]
        else:
            with LIGHTDatabase(self.db_path) as ldb:
                obj = ldb.get_object(id=object_id)[0]
        self.is_gettable = obj['is_gettable']
        self.is_wearable = obj['is_wearable']
        self.is_weapon = obj['is_weapon']
        self.is_food = obj['is_food']
        self.is_drink = obj['is_drink']
        self.is_container = obj['is_container']
        self.is_surface = obj['is_surface']
        self.description = obj['physical_description']
        self.name = obj['name']
        self.name_prefix = obj['name_prefix']
        self.is_plural = obj['is_plural']
        self.db_id = object_id
        self.base_id = obj['base_id']
        self.__in_room_ids = []
        self.__ex_room_ids = []
        self.__contained_by = []
        self.__containing_objs = []
        self.__base_form = None
        if self.use_cache:
            self.__base_form = self.cache['base_objs'][self.base_id]['name']

    @property
    def in_room_ids(self):
        if not self.__in_room_ids:
            self.__in_room_ids = self.get_db_edges(
                DB_EDGE_IN_CONTAINED, False, DB_TYPE_ROOM
            )
        return self.__in_room_ids.copy()

    @property
    def ex_room_ids(self):
        if not self.__ex_room_ids:
            self.__ex_room_ids = self.get_db_edges(
                DB_EDGE_EX_CONTAINED, False, DB_TYPE_ROOM
            )
        return self.__ex_room_ids.copy()

    @property
    def contained_by(self):
        if not self.__contained_by:
            self.__contained_by = self.get_text_edges(type=DB_EDGE_CONTAINED_IN)
        return self.__contained_by.copy()

    @property
    def base_form(self):
        if self.__base_form is None:
            with LIGHTDatabase(self.db_path) as ldb:
                self.__base_form = ldb.get_base_object(self.base_id)[0]['name']
        return self.__base_form

    @property
    def containing_objs(self):
        if not self.__containing_objs:
            self.__containing_objs = self.get_text_edges(type=DB_EDGE_IN_CONTAINED)
        return self.__containing_objs.copy()

    def object_features(self, globalFull, full=None):
        '''Get text feature for a dbobject'''
        if globalFull and full is None:
            full = True
        if full is None:
            full = False
        str = ''
        str += self.name
        if full:
            str += f'. {self.description} '
        return str.rstrip()


class DBCharacter(DBElement):
    '''Instantiate a LightDB representation of a Character'''

    def __init__(self, db_path, char_id, cache=None):
        '''Takes in the database path and a valid room_id 
        and initialize base fields of a character'''
        super(DBCharacter, self).__init__(db_path, char_id, cache)
        if self.use_cache:
            char = cache['characters'][char_id]
        else:
            with LIGHTDatabase(self.db_path) as ldb:
                char = ldb.get_character(id=char_id)[0]
        self.name = char['name']
        self.name_prefix = char['name_prefix']
        self.char_type = char['char_type']
        self.desc = char['physical_description']
        self.persona = char['persona']
        self.is_plural = char['is_plural']
        self.__carrying_objects = None
        self.__wearing_objects = None
        self.__wielding_objects = None
        self.base_id = char['base_id']
        self.__base_char = None
        if self.use_cache:
            self.__base_char = self.cache['base_chars'][self.base_id]['name']
        self.db_id = char_id
        self.__in_room_ids = None
        self.__ex_room_ids = None

    @property
    def carrying_objects(self):
        if self.__carrying_objects is None:
            db_carrying_objs = self.get_db_edges(type=DB_EDGE_IN_CONTAINED)
            text_carrying_objs = self.get_text_edges(type=DB_EDGE_IN_CONTAINED)
            self.__carrying_objects = {
                'db': db_carrying_objs,
                'text': text_carrying_objs,
            }
        return self.__carrying_objects.copy()

    @property
    def wearing_objects(self):
        if self.__wearing_objects is None:
            db_wearing_objs = self.get_db_edges(type=DB_EDGE_WORN)
            text_wearing_objs = self.get_text_edges(type=DB_EDGE_WORN)
            self.__wearing_objects = {'db': db_wearing_objs, 'text': text_wearing_objs}
        return self.__wearing_objects.copy()

    @property
    def wielding_objects(self):
        if self.__wielding_objects is None:
            db_wielding_objs = self.get_db_edges(type=DB_EDGE_WIELDED)
            text_wielding_objs = self.get_text_edges(type=DB_EDGE_WIELDED)
            self.__wielding_objects = {
                'db': db_wielding_objs,
                'text': text_wielding_objs,
            }
        return self.__wielding_objects.copy()

    @property
    def base_form(self):
        if self.__base_char is None:
            with LIGHTDatabase(self.db_path) as ldb:
                self.__base_char = ldb.get_base_character(self.base_id)[0]['name']
        return self.__base_char

    @property
    def in_room_ids(self):
        if self.__in_room_ids is None:
            self.__in_room_ids = self.get_db_edges(
                DB_EDGE_IN_CONTAINED, False, DB_TYPE_ROOM
            )
        return self.__in_room_ids.copy()

    @property
    def ex_room_ids(self):
        if self.__ex_room_ids is None:
            self.__ex_room_ids = self.get_db_edges(
                DB_EDGE_EX_CONTAINED, False, DB_TYPE_ROOM
            )
        return self.__ex_room_ids.copy()

    def character_features(self, globalFull, full=False):
        '''Get text feature for a db character'''
        if globalFull:
            full = True
        str = ''
        str += self.name
        if full:
            str += f'. {self.persona} '
        return str.rstrip()
