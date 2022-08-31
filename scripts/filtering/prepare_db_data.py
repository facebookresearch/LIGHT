# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# Builds a LIGHT map using a StarSpace model to connect locations.
# Is not currently connected to the LIGHT text adventure game API
#  (but should be straight-forward).

from parlai.core.params import ParlaiParser
from parlai.core.agents import create_agent
from parlai_internal.projects.light.light_maps.html_map import generate_html_map
from parlai_internal.projects.light.light_maps.filler_rooms import build_filler_rooms
import parlai_internal.projects.light.v1.graph as graph
import pickle
import random
import copy
import numpy as np

random.seed(6)
np.random.seed(6)


from parlai_internal.projects.light.v1.data_model.light_database import (
    LIGHTDatabase,
    DB_STATUS_REJECTED,
    DB_TYPE_ROOM,
    DB_TYPE_CHAR,
)

db_path = "/Users/jju/ParlAI/data/LIGHT/environment/db/database3.db"


with LIGHTDatabase(db_path) as db:
    statuses = db.get_id(type=DB_TYPE_ROOM)
    good_ids = [s["id"] for s in statuses if s["status"] != DB_STATUS_REJECTED]
    LEFT_ROOMS = {id: dict(db.get_room(id=id)[0]) for id in good_ids}

with LIGHTDatabase(db_path) as db:
    statuses = db.get_id(type=DB_TYPE_CHAR)
    print(len(statuses))
    good_ids = [s["id"] for s in statuses if s["status"] != DB_STATUS_REJECTED]
    print(len(good_ids))
    LEFT_CHARACTERS = [dict(db.get_character(id=id)[0]) for id in good_ids]


def get_random_room():
    return random.choice(list(LEFT_ROOMS.values()))


def go():
    real_room = 0
    random_room = 0
    personas = []

    with LIGHTDatabase(db_path) as db:
        for c in LEFT_CHARACTERS:
            if c["is_plural"] == 0:
                name = c["name"]
                persona = c["persona"]
                room_id_searched = db.get_node_content(child_id=c["id"])
                if len(room_id_searched) == 0:
                    room_id_used = -1
                else:
                    room_id_used = room_id_searched[0]["parent_id"]
                if room_id_used in LEFT_ROOMS:
                    room = LEFT_ROOMS[room_id_used]
                    real_room += 1
                else:
                    room = get_random_room()
                    random_room += 1
                # print(room)
                setting = room["name"]
                desc = room["description"]
                personas.append([name, persona, setting + ", " + desc])

    # env_file = "/checkpoint/light/light_jfixed_environment.pkl"
    # print("loading specified db: " + env_file)
    # with open(env_file, 'rb') as picklefile:
    #     db = pickle.load(picklefile)
    # for ci in db['characters']:
    #     c = db['characters'][ci]
    #     if c['is_plural'] == 0:
    #         cnt = 0
    #         for p in c['personas']:
    #             persona = [p]
    #             persona.insert(0, c['name'])
    #             # get a room id.
    #             if 'in_room_ids' in c and len(c['in_room_ids']) > cnt:
    #                 rid = c['in_room_ids'][cnt]
    #                 r =  db['rooms'][rid]
    #             else:
    #                 r = get_random_room(db)
    #             setting = r['setting']
    #             desc = r['description']
    #             persona.append(setting + ". " + desc)
    #             personas.append(persona)

    print(len(personas), real_room, random_room)

    import json

    with open("personas.json", "w") as outfile:
        json.dump(personas, outfile)


if __name__ == "__main__":
    random.seed(6)
    go()
