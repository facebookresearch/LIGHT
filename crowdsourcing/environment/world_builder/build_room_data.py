from collections import defaultdict
from copy import deepcopy
import pickle
import jsonlines
import os
import shutil
from tqdm import tqdm
import parlai.core.build_data as build_data
from parlai.utils.data import DatatypeHelper
import parlai.utils.logging as logging
import parlai_internal.tasks.light_common_sense.constants as consts

import random
from config import LIGHT_DB_PATH

random.seed(8)


try:
    from light.graph.builders.base import DBGraphBuilder
    from light.graph.structured_graph import OOGraph
    from light.world.world import World
    from light.data_model.light_database import (
        LIGHTDatabase,
    )

except ModuleNotFoundError:
    raise ModuleNotFoundError(consts.INST_LIGHT_MSG)

class RoomCommonSenseGraphBuilder(DBGraphBuilder):
    def __init__(self, db_path, allow_blocked=False):
        logging.info(f'Opening the LIGHT DB at "{db_path}"')
        ldb = LIGHTDatabase(db_path, True)
        logging.info('DB opened successfully.')
        super().__init__(ldb, allow_blocked)

def _get_element_attributes(db_element, attributes_list):
    data = dict()
    for att in attributes_list:
        data[att] = db_element.__dict__.get(att)
    return data


def get_room_data(db_room):
    """
    Outputs a dict containing relevant data from a DBRoom object.
    """
    data = _get_element_attributes(db_room, consts.ROOM_ATTRIBUTES)
    if data['data_split'] == 'val':
        data['data_split'] = 'valid'
    # The following lists are place-holder. They will be populated later.
    data.update({'objects': [], 'characters': []})
    data['element_type'] = 'room'
    return data

def get_object_data(db_object):
    """
    Outputs a dict containing relevant data from a DBObject object.
    """
    object_data = _get_element_attributes(db_object, consts.ROOM_OBJECT_ATTRIBUTES)
    # For some reason I don't know I can't get lists with the above function.
    object_data['containing_objects'] = db_object.containing_objs
    object_data['contained_by'] = db_object.contained_by
    object_data['element_type'] = 'objects'
    return object_data

def get_character_data(db_character, graph_builder):
    """
    Outputs a dict containing relevant data from a DBCharacter object.
    """

    def get_related_objects(related_objects_ids):
        related_objects = []
        for ro_id in related_objects_ids:
            ro = graph_builder.get_obj_from_id(ro_id)
            related_objects.append(
                _get_element_attributes(ro, consts.ROOM_OBJECT_ATTRIBUTES)
            )
        return related_objects

    character_data = _get_element_attributes(
        db_character, consts.ROOM_CHARACTER_ATTRIBUTES
    )
    # For some reason I don't know I can't get lists with the above function.
    character_data['carrying_objects'] = get_related_objects(
        db_character.carrying_objects['db']
    )
    character_data['wearing_objects'] = get_related_objects(
        db_character.wearing_objects['db']
    )
    character_data['wielding_objects'] = get_related_objects(
        db_character.wielding_objects['db']
    )
    character_data['element_type'] = 'characters'
    return character_data



room_cs_graph_builder = RoomCommonSenseGraphBuilder(LIGHT_DB_PATH, True)

usable_rooms = room_cs_graph_builder.get_usable_rooms()

all_room_data = []
for room_id in tqdm(usable_rooms):
    room = room_cs_graph_builder.get_room_from_id(room_id)
    room_data = get_room_data(room)
    
    in_room_object_ids = room.in_objects['db']
    ex_room_object_ids = room.ex_objects['db']
    for room_object_id in in_room_object_ids + ex_room_object_ids:
        room_object = room_cs_graph_builder.get_obj_from_id(room_object_id)
        if not room_object:
            continue
        room_object_data = get_object_data(room_object)
        room_object_data[consts.IS_IN_ROOM] = (
            room_object_id in in_room_object_ids
        )
        if room_object_data[consts.IS_IN_ROOM]:
            room_data['objects'].append(room_object_data)

    # Getting the list of characters in the room
    in_room_character_ids = room.in_characters['db']
    ex_room_character_ids = room.ex_characters['db']
    for room_character_id in in_room_character_ids + ex_room_character_ids:
        room_characetr = room_cs_graph_builder.get_char_from_id(room_character_id)
        if not room_characetr:
            continue
        room_characetr_data = get_character_data(room_characetr, room_cs_graph_builder)
        room_characetr_data[consts.IS_IN_ROOM] = (
            room_character_id in in_room_character_ids
        )
        if room_characetr_data[consts.IS_IN_ROOM]:
            room_data['characters'].append(room_characetr_data)
        
    all_room_data.append(room_data)

rd = all_room_data[0]

room_to_items = {}

for rd in all_room_data:
    db_id = rd['db_id']
    room_to_items[db_id] = {'characters': [], 'objects': []}
    for db_c in rd['characters']:
        character_node = {
                "agent": True,
                "aggression": 0,
                "pacifist": False,
                "char_type": "creature",
                "classes": ["agent"],
                "contain_size": 20,
                "contained_nodes": {},
                "container_node": {
                    "target_id": None
                },
                "damage": 1,
                "db_id": None,
                "defense": 0,
                "desc": db_c.get('desc', ''),
                "followed_by": {},
                "following": None,
                "food_energy": 1,
                "health": 5,
                "is_player": False,
                "name": db_c['name'],
                "name_prefix": "a",
                "names": [db_c['name']],
                "tags": [],
                "node_id": db_c['name'].replace(" ", "_"),
                "object": False,
                "on_events": None,
                "persona": db_c.get('persona', ''),
                "room": False,
                "size": 20,
                "speed": 20
            }
        room_to_items[db_id]['characters'].append(character_node)
    for db_o in rd['objects']:
        object_node = {
            "agent": False,
            "classes": ["object"],
            "contain_size": 20,
            "contained_nodes": {},
            "container": True,
            "container_node": {
                "target_id": None
            },
            "db_id": None,
            "dead": False,
            "desc": db_o.get('description'),
            "drink": False,
            "equipped": None,
            "food": False,
            "food_energy": 0,
            "gettable": False,
            "locked_edge": None,
            "name": db_o['name'],
            "name_prefix": "a",
            "names": [db_o['name']],
            "node_id": db_o['name'].replace(" ", "_"),
            "object": True,
            "on_use": None,
            "room": False,
            "size": 1,
            "stats": {
            "damage": 0,
            "defense": 0
            },
            "surface_type": "in",
            "value": 1,
            "wearable": False,
            "wieldable": False
        }
        room_to_items[db_id]['objects'].append(object_node)

ROOM_ID_TO_ITEMS = room_to_items