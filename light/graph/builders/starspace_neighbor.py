# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3
# Builds a LIGHT map using a StarSpace model to connect locations.
# Is not currently connected to the LIGHT text adventure game API
#  (but should be straight-forward).

# TODO (wish) restore this to work with the new data model
# to include as reproducible research

from parlai.core.params import ParlaiParser
from parlai.core.agents import create_agent
from light.graph.viz.html_map import generate_html_map
from light.graph.viz.graph_printer import GraphPrinter
from light.data_model.filler_rooms import build_filler_rooms
from light.graph.structured_graph import OOGraph
from light.graph.builders.base import GraphBuilder

import pickle
import random
import copy
import numpy as np
import asyncio

random.seed(6)
np.random.seed(6)


# TODO deprecate?
class StarspaceNeighborBuilder(GraphBuilder):
    """Old builder that used starspace to connect rooms and db entries to fill them"""

    def __init__(self, debug=True, build_args=None):
        parser = ParlaiParser(True, True, "blah")
        parser.add_argument(
            "--light-model-root",
            type=str,
            default="/Users/jju/Desktop/LIGHT/LIGHT_models/",
            help="models path. For local setup, use: /checkpoint/jase/projects/light/dialog/",
        )
        parser.add_argument(
            "--light-db-file",
            type=str,
            default="",
            help="specific path for db pickle to override the path",
        )
        parser.add_argument(
            "--dump-dialogues",
            type=bool,
            default=False,
            help="option to dump all human dialogues to file",
        )
        self.opt, _unknown = parser.parse_and_process_known_args(args=build_args)
        self.dpath = self.opt["datapath"] + "/light_maps"

        if self.opt.get("light_db_file", "") != "":
            env_file = self.opt.get("light_db_file")
            print("loading specified db: " + env_file)
            with open(env_file, "rb") as picklefile:
                self.db = pickle.load(picklefile)
        else:
            raise AssertionError(
                "Loading a legacy builder without the pickle is unsupported"
            )

        self.debug = debug
        self.filler_rooms, self.filler_room_names = build_filler_rooms(self.db)
        self.filler_probability = 0.3
        self._no_npc_models = False
        self.load_models()

    def props_from_obj(self, obj):
        use_classes = ["object"]
        props = {
            "object": True,
            "size": 1,
            "food_energy": 0,
            "value": 1,
            "desc": obj["description"],
        }
        if obj["is_surface"] > 0.5:
            props["container"] = True
            props["contain_size"] = 3
            props["surface_type"] = "on"
            use_classes.append("container")
        if obj["is_container"] > 0.5:
            props["container"] = True
            props["contain_size"] = 3
            props["surface_type"] = "on"
            use_classes.append("container")
        if obj["is_drink"] > 0.5:
            props["drink"] = True
            use_classes.append("drink")
        if obj["is_food"] > 0.5:
            props["food"] = True
            use_classes.append("food")
        if obj["is_gettable"] < 0.33:
            use_classes.append("not_gettable")
        if obj["is_wearable"] > 0.5:
            props["wearable"] = True
            props["stats"] = {"attack": 1}
            use_classes.append("wearable")
        if obj["is_weapon"] > 0.5:
            props["wieldable"] = True
            props["stats"] = {"attack": 1}
            use_classes.append("wieldable")

        props["classes"] = use_classes
        if obj.get("is_plural", 0) == 1:
            props["is_plural"] = True
        else:
            props["is_plural"] = False

        return props

    def props_from_char(self, char):
        use_classes = ["agent"]
        props = {
            "agent": True,
            "size": 20,
            "contain_size": 20,
            "health": 2,
            "food_energy": 1,
            "aggression": 0,
            "speed": 5,
            "char_type": char["char_type"],
            "desc": char["desc"],
            "persona": random.choice(char["personas"]),
        }
        props["classes"] = use_classes
        props["name_prefix"] = char["name_prefix"]
        if char.get("is_plural", 0) == 1:
            props["is_plural"] = True
        else:
            props["is_plural"] = False
        return props

    def add_room(self, g, room_id):
        g._node_rooms.add(room_id)

    def add_agent(self, g, agent_id):
        g._node_npcs.add(agent_id)

    def heuristic_name_cleaning(self, use_desc):
        if use_desc.lower().startswith("a "):
            use_desc = use_desc[2:]
        if use_desc.lower().startswith("an "):
            use_desc = use_desc[3:]
        if use_desc.lower().startswith("the "):
            use_desc = use_desc[4:]
        return use_desc

    def add_object_to_graph(self, g, obj, container_id, extra_props={}):
        if type(obj) == str:
            # TODO: find matching objects using string -> object model
            return None
        if type(obj) == int:
            obj = self.db["objects"][obj]  # find actual object from id
        obj["description"] = random.choice(obj["descriptions"]).capitalize()
        if obj["is_plural"] == 1:
            if extra_props.get("not_gettable", False) != True:
                return None  # skip this. TODO: find nearest object that is singular.
            else:
                # modify object description to make plural work. TODO: fix in data
                desc = obj["description"]
                desc = "You peer closer at one of them. " + desc
                obj["description"] = desc

        use_desc = obj["name"]
        props = self.props_from_obj(obj)
        for k, v in extra_props.items():
            props[k] = v
        props["name_prefix"] = obj["name_prefix"]
        obj_id = g.add_node(use_desc, props)
        g.move_object(obj_id, container_id)
        return obj_id

    def add_new_agent_to_graph(self, g, char, room_id):
        if "is_banned" in char:
            print("skipping BANNED character! " + char["name"])
            return
        if char["is_plural"] > 0:
            print("skipping PLURAL character! " + char["name"])
            return
        use_desc = (
            char["name"] if char["is_plural"] == 0 else random.choice(char["base_form"])
        )
        use_desc = self.heuristic_name_cleaning(use_desc)
        # TODO check for duplicates again
        # if use_desc in g._npc_names:
        #     # Don't create the same agent twice.
        #     return

        agent = g.oo_graph.add_agent(use_desc, self.props_from_char(char))
        agent_id = agent.node_id

        g.move_object(agent_id, room_id)
        objs = {}
        for obj in char["carrying_objects"]:
            objs[obj] = "carrying"
        for obj in char["wearing_objects"]:
            objs[obj] = "equipped"
        for obj in char["wielding_objects"]:
            objs[obj] = "equipped"
        for obj in objs:
            obj_id = self.add_object_to_graph(g, obj, agent_id)
            if obj_id is not None:
                if objs[obj] == "equipped":
                    g.set_prop(obj_id, "equipped")
        return agent_id

    async def add_random_new_agent_to_graph(self, g):
        # pick a random room
        while True:
            id = random.choice(list(g.oo_graph.rooms.keys()))
            if id in self.roomid_to_db:
                pos_room = self.roomid_to_db[id]
                break
        if pos_room["setting"] == "EMPTY":
            return
        chars = pos_room["ex_characters"]
        if len(chars) == 0:
            return
        char_id = random.choice(chars)
        char = self.db["characters"][char_id]

        agent_id = self.add_new_agent_to_graph(g, char, pos_room["g_id"])
        if agent_id is None:
            return
        # Send message notifying people in room this agent arrived.
        agent_desc = g.node_to_desc(agent_id, use_the=True).capitalize()
        g.broadcast_to_room(
            {
                "caller": None,
                "name": "arrived",
                "actors": [agent_id],
                "room_id": g.location(agent_id),
                "txt": agent_desc + " enters the room.\n",
                "room_agents": g.get_room_agents(
                    g.location(agent_id), drop_prefix=True
                ),
            },
            [agent_id],
        )

    def load_models(self):
        # load model
        # TODO load from zoo
        opt = copy.deepcopy(self.opt)
        LIGHT_MODEL_ROOT = opt["light_model_root"].replace(":no_npc_models", "")
        if ":no_npc_models" in opt["light_model_root"]:
            self._no_npc_models = True
        mf = LIGHT_MODEL_ROOT + "light_maps1/model"
        opt["model_file"] = mf
        self.agents = {}
        opt["fixed_candidates_file"] = self.dpath + "/room_full_cands.txt"
        opt["override"] = {
            "fixed_candidates_file": opt["fixed_candidates_file"],
            #'dict_file': '/Users/jju/Desktop/LIGHT_maps/model.dict',
        }
        self.agents["room"] = create_agent(opt, requireModelExists=True)
        self.agent = self.agents["room"]

    def get_random_room(self):
        ind = random.choice(list(self.db["id_to_roomfeats"].keys()))
        return copy.deepcopy(self.db["rooms"][ind])

    def build_world(self, html_visualization_filename="/tmp/gridtmp.html"):
        self.grid = {}
        r = self.get_random_room()
        loc = (3, 3, 0)
        r["loc"] = loc
        self.grid[loc] = r
        self.map_size = 6
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
            self.grid[randloc] = {"setting": "EMPTY"}
        self.banned_rooms = set()
        self.banned_rooms.add(r["ind"])
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
                l2 = (loc[0] - 1, loc[1], loc[2])
                src_dir = "west"
            if direction == 1:
                l2 = (loc[0] + 1, loc[1], loc[2])
                src_dir = "east"
            if direction == 2:
                l2 = (loc[0], loc[1] - 1, loc[2])
                src_dir = "north"
            if direction == 3:
                l2 = (loc[0], loc[1] + 1, loc[2])
                src_dir = "south"
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
        self.agents["room"].reset()
        txt_feats = self.db["id_to_roomfeats"][self.grid[loc1]["ind"]]
        sim_feats = self.db["id_to_roomfeats"][self.grid[loc2]["ind"]]
        msg = {"text": txt_feats, "episode_done": True}
        self.agents["room"].observe(msg)
        response = self.agents["room"].act()
        score = 100000
        for i, k in enumerate(response["text_candidates"]):
            if k == sim_feats:
                score = i
                break
        return score

    def possibly_connect_to_neighbor(self, loc1, loc2, src_dir):
        if (
            loc2 not in self.grid
            or self.grid[loc2]["setting"] == "EMPTY"
            or src_dir in self.grid[loc1]
        ):
            # nothing there or it is already connected
            return
        else:
            # compute similarity of rooms:
            sim = self.room_similarity(loc1, loc2)
            if sim > 100:
                # if not in the top 40 most similar rooms, no connection.
                return
            # make connection
            inv_dir = {
                "east": "west",
                "west": "east",
                "north": "south",
                "south": "north",
            }
            self.grid[loc2][inv_dir[src_dir] + "*"] = True
            self.grid[loc1][src_dir + "*"] = True

    def possibly_connect_to_neighbors(self, loc):
        self.possibly_connect_to_neighbor(loc, (loc[0] - 1, loc[1], loc[2]), "west")
        self.possibly_connect_to_neighbor(loc, (loc[0] + 1, loc[1], loc[2]), "east")
        self.possibly_connect_to_neighbor(loc, (loc[0], loc[1] - 1, loc[2]), "north")
        self.possibly_connect_to_neighbor(loc, (loc[0], loc[1] + 1, loc[2]), "south")

    def add_room(self, room, loc, src_loc, src_dir):
        self.grid[loc] = room
        room["loc"] = loc
        inv_dir = {"east": "west", "west": "east", "north": "south", "south": "north"}
        self.grid[loc][inv_dir[src_dir]] = True
        self.grid[src_loc][src_dir] = True
        self.banned_rooms.add(room["ind"])
        self.possibly_connect_to_neighbors(loc)
        self.stack.append(room)

    def add_exits(self, r):
        for e in r["neighbors"]:
            l1, src_dir = self.new_grid_position(r["loc"])
            if l1 is not None:
                exit_desc = self.db["neighbors"][e]
                exit_text = exit_desc["destination"] + " " + r["category"]
                r1 = self.get_similar_room(exit_text)
                if r1 is not None:
                    if self.debug:
                        print(
                            str(r["loc"])
                            + " "
                            + r["setting"]
                            + " -> "
                            + exit_text
                            + " REPLACED-WITH: "
                            + r1["setting"]
                            + " "
                            + str(l1)
                        )
                    p = np.random.uniform(0, 1, 1)
                    if (
                        p[0] < self.filler_probability
                        and r1["category"] in self.filler_rooms
                    ):
                        # choose random room in this category as filler
                        category_filler_rooms = self.filler_rooms[r1["category"]]
                        # need to copy exits, or will create small closed loops in the game
                        filler_room = random.choice(category_filler_rooms)
                        filler_room["neighbors"] = r1["neighbors"]
                        self.add_room(filler_room, l1, r["loc"], src_dir)
                    else:
                        self.add_room(r1, l1, r["loc"], src_dir)

    def get_similar_room(self, txt_feats):
        # Get prediction from StarSpace model.
        self.agents["room"].reset()
        msg = {"text": txt_feats, "episode_done": True}
        self.agents["room"].observe(msg)
        response = self.agents["room"].act()
        ind = 0
        while True:
            key = response["text_candidates"][ind]
            if key in self.db["roomfeats_to_id"]:
                rind = self.db["roomfeats_to_id"][key]
                if rind not in self.banned_rooms:
                    return self.db["rooms"][rind]
            ind = ind + 1
            if len(response["text_candidates"]) <= ind:
                return None

    async def get_graph(self):
        g = OOGraph(self.opt)
        g.npc_models._no_npc_models = self._no_npc_models
        g.db = self.db
        g.world = self
        self.g = g
        room_ids = []

        # Create base rooms
        self.roomid_to_db = {}
        for pos_room in self.grid.values():
            if pos_room["setting"] == "EMPTY":
                continue
            pos_room["g_id"] = g.add_node(
                pos_room["setting"],
                # props:
                {
                    "room": True,
                    "desc": pos_room["description"],
                    "extra_desc": pos_room["background"],
                    "room": True,
                    "size": 2000,  # TODO turk room sizes
                    "contain_size": 2000,  # TODO turk room sizes
                    "name_prefix": "the",
                    "surface_type": "in",
                    "classes": {"room"},
                },
                is_room=True,
            )
            room_ids.append(pos_room["g_id"])
            # store link between graph and underlying db so we can create more characters, etc.
            self.roomid_to_db[pos_room["g_id"]] = pos_room

        # attach rooms to neighbors
        for (i, j, k), pos_room in self.grid.items():
            if pos_room["setting"] == "EMPTY":
                continue
            if pos_room.get("north"):
                other_room = self.grid[(i, j - 1, k)]
                if other_room["setting"] == "EMPTY":
                    continue
                g.add_one_path_to(pos_room["g_id"], other_room["g_id"], "north")
            if pos_room.get("south"):
                other_room = self.grid[(i, j + 1, k)]
                if other_room["setting"] == "EMPTY":
                    continue
                g.add_one_path_to(pos_room["g_id"], other_room["g_id"], "south")
            if pos_room.get("east"):
                other_room = self.grid[(i + 1, j, k)]
                if other_room["setting"] == "EMPTY":
                    continue
                g.add_one_path_to(pos_room["g_id"], other_room["g_id"], "east")
            if pos_room.get("west"):
                other_room = self.grid[(i - 1, j, k)]
                if other_room["setting"] == "EMPTY":
                    continue
                g.add_one_path_to(pos_room["g_id"], other_room["g_id"], "west")

        if False:
            # add player to a random room
            player_id = g.add_node(
                "player",
                {
                    "agent": True,
                    "size": 20,
                    "contain_size": 20,
                    "health": 1,
                    "food_energy": 1,
                    "aggression": 0,
                    "speed": 25,
                    "classes": {"agent"},
                },
                is_player=True,
                uid="player",
            )
            # don't add player to a boring room at the start
            non_filler_room_ids = list(
                filter(
                    lambda x: x.split("_")[0] not in self.filler_room_names, room_ids
                )
            )
            g.move_object(player_id, random.choice(non_filler_room_ids))

        # add objects and characters to rooms
        for pos_room in self.grid.values():
            if pos_room["setting"] == "EMPTY":
                continue
            for item_id in pos_room["ex_objects"]:
                if random.random() > 0.5:
                    continue
                obj = self.db["objects"][item_id]
                objid = self.add_object_to_graph(g, obj, pos_room["g_id"])

            for item_id in pos_room["in_objects"]:
                obj = self.db["objects"][item_id]
                props = {}
                props["not_gettable"] = True
                objid = self.add_object_to_graph(g, obj, pos_room["g_id"], props)
                g._node_to_prop[objid]["classes"].append("described")

                if False:
                    # Asterisks marking interactable in the description.
                    # SKIP THIS FOR NOW... but we may go back to it
                    old_desc = g._node_to_prop[pos_room["g_id"]]["desc"]
                    new_desc = old_desc.replace(obj["name"], "*{}*".format(obj["name"]))
                    new_desc = new_desc.replace("**", "*")
                    new_desc = new_desc.replace("*", "")  # remove completely
                    g._node_to_prop[pos_room["g_id"]]["desc"] = new_desc
            cnt = 0
            for char_id in pos_room["ex_characters"]:
                if random.random() > 0.5 or cnt > 2:
                    continue
                char = self.db["characters"][char_id]
                room = pos_room["g_id"]
                self.add_new_agent_to_graph(g, char, room)
                cnt += 1
                # print("creating:" + )
            for char_id in pos_room["in_characters"]:
                continue  # ignore for now
                char = self.db["characters"][char_id]
                use_desc = (
                    char["name"]
                    if char["is_plural"] == 0
                    else random.choice(char["base_form"])
                )
                props = self.props_from_char(char)
                props["classes"].append("described")
                props["speed"] = 0
                g_id = g.add_node(use_desc, props)
                g.move_object(g_id, pos_room["g_id"])
                if False:
                    # Asterisks marking interactable in the description.
                    # SKIP THIS FOR NOW... but we may go back to it
                    old_desc = g._node_to_prop[pos_room["g_id"]]["desc"]
                    new_desc = old_desc.replace(
                        char["name"], "*{}*".format(char["name"])
                    )
                    # dedupe stars
                    new_desc = new_desc.replace("**", "*")
                    new_desc = new_desc.replace("*", "")  # remove completely
                    g._node_to_prop[pos_room["g_id"]]["desc"] = new_desc
                    g._node_to_prop[pos_room["g_id"]]["persona"] = new_desc

        g._initial_num_npcs = len(g._node_npcs)
        return g
