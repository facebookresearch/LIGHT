#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.registry.models.starspace_model import MapStarspaceModelConfig
from light.world.world import World, WorldConfig
from light.graph.structured_graph import OOGraph
from light.graph.builders.base import (
    DBGraphBuilder,
    SingleSuggestionGraphBuilder,
)
from light.data_model.light_database import (
    DB_EDGE_IN_CONTAINED,
    DB_EDGE_CONTAINED_IN,
    DB_EDGE_WORN,
    DB_EDGE_WIELDED,
    DB_EDGE_NEIGHBOR,
    DB_TYPE_ROOM,
    DB_TYPE_OBJ,
    DB_TYPE_CHAR,
    DB_TYPE_CHAR,
    DB_TYPE_OBJ,
    DB_TYPE_ROOM,
)
from light.graph.builders.base_elements import (
    DBRoom,
    DBObject,
    DBCharacter,
)

import os
import random
import copy
import time
import asyncio

from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from light.data_model.light_database import LIGHTDatabase
    from light.registry.model_pool import ModelPool

MAX_EXTRA_AGENTS_PER_ROOM = 2
INV_DIR = {"east": "west", "west": "east", "north": "south", "south": "north"}
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


@dataclass
class OneRoomChatBuilderConfig:  # BuilderConfig():
    # TODO create builder config parent
    model_loader_config: MapStarspaceModelConfig = MapStarspaceModelConfig()
    suggestion_type: str = field(
        default="model",
        metadata={
            "help": ("Input 'model', 'human', or 'hybrid', for the suggestion type")
        },
    )
    hybridity_prob: float = field(
        default=0.5,
        metadata={
            "help": ("Set probability how often ex-object or character is skipped")
        },
    )
    use_best_match_model: bool = field(
        default=False,
        metadata={
            "help": (
                "use human suggestions for predicting placement of objects, characters, and room"
            )
        },
    )
    # TODO move to elsewhere
    light_db_file: str = field(
        default="/checkpoint/light/data/database3.db",
        metadata={"help": ("specific path for light database")},
    )


class OneRoomChatBuilder(DBGraphBuilder, SingleSuggestionGraphBuilder):
    """Builds a one-room light Graph using a StarSpace model to connect everything."""

    def __init__(
        self,
        ldb: "LIGHTDatabase",  # LIGHT database, TODO replace with EnvDB
        model_pool: "ModelPool",  # Models this builder can use
        builder_config: "DictConfig",  # Configuration for this builder
        graph_opt=None,
    ):
        """Initializes required models and parameters for this graph builder"""
        self.graph_opt = {} if graph_opt is None else graph_opt

        # Setup correct path
        self.db_path = builder_config.get("light_db_file")
        self.dpath = os.path.expanduser("~/ParlAI/data/light_maps/")
        model_path = opt.get("model_path")
        if model_path is None:
            model_path = opt.get("light_model_root")
        self.model_path = model_path
        DBGraphBuilder.__init__(self, ldb)
        SingleSuggestionGraphBuilder.__init__(self, model_pool=model_pool)

        self.load_models()
        self.use_best_match = builder_config.use_best_match_model
        self.suggestion_type = builder_config.suggestion_type
        # Cache for retrieved room/ char/ obj dicts from the database
        self.roomid_to_feats = {}
        self.feats_to_roomid = {}
        self.objid_to_feats = {}
        self.feats_to_objid = {}
        self.charid_to_feats = {}
        self.feats_to_charid = {}
        # paramter to control the hybridity of the model
        self.prob_skip_ex_objects = builder_config.hybridity_prob
        self.prob_skip_ex_char = builder_config.hybridity_prob
        self.allowed_characters = None
        self.banned_rooms = []
        self.room = None
        self.neighbors = []

    def load_models(self) -> None:
        """Load starspace models for building the map"""
        # self.model_pool.register_model(self.config.model_loader_config, "map_starspace")
        self.agents["room"] = self.model_pool.get_model(
            "map_starspace", {"target_type": "room"}
        )
        self.agents["object"] = self.model_pool.get_model(
            "map_starspace", {"target_type": "object"}
        )
        self.agents["character"] = self.model_pool.get_model(
            "map_starspace", {"target_type": "character"}
        )

    def _props_from_obj(self, obj):
        """Given a DBObject representing an object in the world, extract the
        required props to create that object in the world
        """
        use_classes = ["object"]
        props = {
            "object": True,
            "size": 1,
            "food_energy": 0,
            "value": 1,
            "desc": obj.description,
        }
        if obj.is_surface > 0.5:
            props["container"] = True
            props["contain_size"] = 3
            props["surface_type"] = "on"
            use_classes.append("container")
        if obj.is_container > 0.5:
            props["container"] = True
            props["contain_size"] = 3
            props["surface_type"] = "on"
            use_classes.append("container")
        if obj.is_drink > 0.5:
            props["drink"] = True
            use_classes.append("drink")
        if obj.is_food > 0.5:
            props["food"] = True
            use_classes.append("food")
        if obj.is_gettable < 0.33:
            use_classes.append("not_gettable")
        if obj.is_wearable > 0.5:
            props["wearable"] = True
            props["stats"] = {"attack": 1}
            use_classes.append("wearable")
        if obj.is_weapon > 0.5:
            props["wieldable"] = True
            props["stats"] = {"attack": 1}
            use_classes.append("wieldable")

        props["classes"] = use_classes
        if obj.is_plural == 1:
            props["is_plural"] = True
        else:
            props["is_plural"] = False

        return props

    def _props_from_char(self, char):
        """Given a dict representing a character in the world, extract the
        required props to create that object in the world
        """
        use_classes = ["agent"]
        props = {
            "agent": True,
            "size": 20,
            "contain_size": 20,
            "health": 2,
            "food_energy": 1,
            "aggression": 0,
            "speed": 5,
            "char_type": char.char_type,
            "desc": char.desc,
            "persona": char.persona,
        }
        props["classes"] = use_classes
        props["name_prefix"] = char.name_prefix
        if char.is_plural == 1:
            props["is_plural"] = True
        else:
            props["is_plural"] = False
        return props

    def _heuristic_name_cleaning(self, use_desc):
        """Remove some artifacts of bad data collection."""
        # TODO deprecate after initial version of LIGHTDatabase is completed
        # with this stuff already cleaned up.
        if use_desc.lower().startswith("a "):
            use_desc = use_desc[2:]
        if use_desc.lower().startswith("an "):
            use_desc = use_desc[3:]
        if use_desc.lower().startswith("the "):
            use_desc = use_desc[4:]
        return use_desc

    async def add_object_to_graph(self, g, obj, container_node, extra_props=None):
        """Adds a particular DBObject to the given OOgraph, adding to the specific
        container node. Returns the newly created object node"""
        if obj is None:
            return None
        if extra_props is None:
            extra_props = {}
        obj.description = obj.description.capitalize()
        if obj.is_plural == 1:
            if extra_props.get("not_gettable", False) is not True:
                # TODO: figure out making plurals work better
                return None
            else:
                # modify object description to make plural work.
                # TODO: fix in data
                desc = obj.description
                desc = f"You peer closer at one of them. {desc}"
                obj.description = desc
        if self._name_not_in_graph(g, obj.name):
            obj_node = self._add_object_to_graph(g, obj, container_node)
            if obj_node.container and self.suggestion_type != "human":
                print(
                    "Adding CONTAINED objects to CONTAINER object to ",
                    obj.name,
                    obj.db_id,
                )
                contained_objs = await self.get_contained_items(
                    obj.db_id, DB_TYPE_OBJ, 3
                )[1:]
                for o in contained_objs:
                    if self._name_not_in_graph(g, o.name):
                        self._add_object_to_graph(g, o, obj_node)
                # TODO: Currently only adding one layer of contained object of an object
                # Check if we want to add more layers
            return obj_node

    def _name_not_in_graph(self, g, name):
        """check if a node with a certain name is contained in the graph"""
        return name not in [n.name for n in g.all_nodes.values()]

    def _add_object_to_graph(self, g, obj, container_node, extra_props=None):
        """Helper for add_object_to_graph to reduce redundancy"""
        if extra_props is None:
            extra_props = {}
        # construct props for this object
        use_desc = obj.name
        props = self._props_from_obj(obj)
        for k, v in extra_props.items():
            props[k] = v
        props["name_prefix"] = obj.name_prefix

        # Add the object to the graph
        obj_node = g.add_object(use_desc, props, db_id=obj.db_id)
        if obj_node.size <= container_node.contain_size:
            obj_node.move_to(container_node)
            return obj_node

    async def add_new_agent_to_graph(self, g, char, room_node):
        """Add the given DBcharacter  to the given room (room_node) in the
        given OOFraph. Return the new agent node on success, and None on failure"""
        if char is None:
            return None
        if "is_banned" in vars(char):
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
        agent_node = g.add_agent(
            use_desc, self._props_from_char(char), db_id=char.db_id
        )
        # added as a NPC
        agent_node.move_to(room_node)
        objs = {}
        if self.suggestion_type != "model":
            # For the case of only using human recs and hybrid
            for obj in char.carrying_objects["db"]:
                # Only use the database id objects, as add object to graph takes an obj_id
                objs[obj] = "carrying"
            for obj in char.wearing_objects["db"]:
                objs[obj] = "equipped"
            for obj in char.wielding_objects["db"]:
                objs[obj] = "equipped"
        elif self.suggestion_type == "model":
            objs = {
                obj.db_id: (
                    "equipped" if obj.is_wearable or obj.is_weapon else "carrying"
                )
                for obj in await self.get_contained_items(char.db_id, DB_TYPE_CHAR)
            }
        if self.suggestion_type == "hybrid" and len(objs) == 0:
            objs = {
                obj.db_id: (
                    "equipped" if obj.is_weapon or obj.is_wearable else "carrying"
                )
                for obj in await self.get_contained_items(char.db_id, DB_TYPE_CHAR, 2)
            }

        for obj in objs:
            obj_node = await self.add_object_to_graph(
                g, self.get_obj_from_id(obj), agent_node
            )
            if obj_node is not None:
                if objs[obj] == "equipped":
                    obj_node.set_prop("equipped", True)
        return agent_node

    async def add_random_new_agent_to_graph(self, world):
        """Add a random agent to the OOGraph at a random room node"""
        raise Exception("There shouldn't be any random additions")

    async def add_neighbors(self, room):
        """Try to add all possible exits to a given room"""
        if self.use_best_match:
            neighbors = room.get_text_edges(DB_EDGE_NEIGHBOR)
        else:
            # Not using best match model but the starspace model for model prediction
            neighbors = [
                e.setting
                for e in await self.get_neighbor_rooms(
                    room_id=room.db_id, banned_rooms=[]
                )
            ]
        return neighbors

    ##########For best match model###################
    async def get_similar_element(self, txt_feats, element_type):
        """Given a text feature, and the corresponding Database type
        return an DBElement of the DB type"""
        agent_type = None
        banned_items = {}
        feats_to_id = None
        get_x_from_id = None
        if element_type == DB_TYPE_ROOM:
            agent_type = "room"
            banned_items = self.banned_rooms
            feats_to_id = self.roomfeats_to_id
            get_x_from_id = self.get_room_from_id
        elif element_type == DB_TYPE_OBJ:
            agent_type = "object"
            feats_to_id = self.objfeats_to_id
            get_x_from_id = self.get_obj_from_id
        elif element_type == DB_TYPE_CHAR:
            agent_type = "character"
            feats_to_id = self.charfeats_to_id
            get_x_from_id = self.get_char_from_id
        if agent_type is not None:
            self.agents[agent_type].reset()
            msg = {"text": txt_feats, "episode_done": True}
            self.agents[agent_type].observe(msg)
            response = await self.agents[agent_type].act()
            ind = 0
            while ind < len(response["text_candidates"]):
                key = response["text_candidates"][ind]
                rind = feats_to_id(key)
                if rind is not None and rind not in banned_items:
                    return get_x_from_id(rind)
                ind = ind + 1
            return None

    async def get_similar_room(self, txt_feats):
        """Find a similar room to the text room given
        based on a starspace prediction"""
        return await self.get_similar_element(txt_feats, DB_TYPE_ROOM)

    async def get_similar_object(self, txt_feats):
        """Find a similar object to the text given
        based on starspace prediciton"""
        return await self.get_similar_element(txt_feats, DB_TYPE_OBJ)

    async def get_similar_character(self, txt_feats):
        """Find a similar object to the text given
        based on starspace prediciton"""
        return await self.get_similar_element(txt_feats, DB_TYPE_CHAR)

    ###################################################

    async def get_neighbor_rooms(self, room_id, num_results=5, banned_rooms=None):
        """get prediction of neighbor room with StarSpaceModel, return DBRoom Object """
        if banned_rooms is None:
            banned_rooms = [room_id]
        if room_id not in self.roomid_to_feats:
            txt_feats = self.get_text_features(self.get_room_from_id(room_id))
            # This is added due to the new model prediction for neighbors
        else:
            txt_feats = self.roomid_to_feats[room_id]
        response = await self.agent_recommend(txt_feats, "room")
        ind = 0
        results = []
        while len(results) < num_results:
            key = response["text_candidates"][ind]
            if key in self.feats_to_roomid:
                rind = self.feats_to_roomid[key]
            else:
                rind = self.roomfeats_to_id(key)
            if rind not in banned_rooms:
                results.append(self.get_room_from_id(rind))
            ind = ind + 1
            if len(response["text_candidates"]) <= ind:
                if len(results) == 0:
                    return None
                else:
                    return results
        return results

    async def get_graph_from_quest(self, quest):
        graph_json = quest["data"]["graph"]
        g = OOGraph.from_json(graph_json)
        world = World(WorldConfig(opt=self.graph_opt, graph_builder=self))
        world.oo_graph = g

        base_room = list(g.rooms.values())[0]
        db_id = base_room.db_id
        if db_id is None:
            neighbors = [self.get_random_room(), self.get_random_room()]
        else:
            neighbors = await self.get_neighbor_rooms(db_id)
        for neighbor_room in neighbors:
            if neighbor_room is None:
                continue
            g.add_room(
                neighbor_room.setting,
                {
                    "room": True,
                    "desc": neighbor_room.description,
                    "extra_desc": neighbor_room.background,
                    "size": 2000,  # TODO turk room sizes
                    "contain_size": 2000,  # TODO turk room sizes
                    "name_prefix": "the",
                    "surface_type": "in",
                    "classes": {"room"},
                },
                db_id=neighbor_room.db_id,
            )
        return g, world

    async def _get_constrained_graph(self, location=None, player=None, num_partners=1):
        """
        Location is of the form "Location Name. location description"
        player is of the form "Player Name. player persona"
        """
        if location is None:
            set_room = self.get_random_room()
        else:
            set_room = self.get_room_from_id(self.roomfeats_to_id(location))

        g = OOGraph(self.graph_opt)
        room_node = g.add_room(
            set_room.setting,
            {
                "room": True,
                "desc": set_room.description,
                "extra_desc": set_room.background,
                "size": 2000,  # TODO turk room sizes
                "contain_size": 2000,  # TODO turk room sizes
                "name_prefix": "the",
                "surface_type": "in",
                "classes": {"room"},
            },
            db_id=set_room.db_id,
        )
        set_room.g_id = room_node.node_id

        possible_chars = await self.get_contained_characters(
            room_id=set_room.db_id, num_results=5
        )
        if "db" in set_room.ex_characters:
            for char_id in set_room.ex_characters["db"]:
                char = self.get_char_from_id(char_id)
                possible_chars.append(char)
        if "db" in set_room.in_characters:
            for char_id in set_room.in_characters["db"]:
                char = self.get_char_from_id(char_id)
                possible_chars.append(char)

        if player is None:
            player_char = random.choice(possible_chars)
            possible_chars.remove(player_char)
            self_char_id = await self.add_new_agent_to_graph(g, player_char, room_node)
            while self_char_id is None:
                player_char = random.choice(possible_chars)
                possible_chars.remove(player_char)
                self_char_id = await self.add_new_agent_to_graph(
                    g, player_char, room_node
                )
        else:
            player_char = self.get_char_from_id(self.charfeats_to_id(player.lower()))
            self_char_id = await self.add_new_agent_to_graph(g, player_char, room_node)

        for _ in range(num_partners):
            partner_char = random.choice(possible_chars)
            possible_chars.remove(partner_char)
            parner_char_id = await self.add_new_agent_to_graph(
                g, partner_char, room_node
            )
            while parner_char_id is None:
                partner_char = random.choice(possible_chars)
                possible_chars.remove(partner_char)
                parner_char_id = await self.add_new_agent_to_graph(
                    g, partner_char, room_node
                )

        if "db" in set_room.ex_objects:
            for item_id in set_room.ex_objects["db"]:
                if random.random() > self.prob_skip_ex_objects:
                    continue
                obj = self.get_obj_from_id(item_id)
                if obj is not None:
                    self.add_object_to_graph(g, obj, room_node)
        if "db" in set_room.in_objects:
            for item_id in set_room.in_objects["db"]:
                obj = self.get_obj_from_id(item_id)
                props = {}
                if obj is not None:
                    self.add_object_to_graph(g, obj, room_node, props)
        if self.suggestion_type == "model":
            predicted_objects = await self.get_contained_items(
                container_id=set_room.db_id, container_type=DB_TYPE_ROOM
            )
            for o in predicted_objects:
                if o is not None:
                    room_node = g.get_node(set_room.g_id)
                    self.add_object_to_graph(g, o, room_node)

        neighbors = await self.get_neighbor_rooms(set_room.db_id)
        for neighbor_room in neighbors:
            if neighbor_room is None:
                continue
            g.add_room(
                neighbor_room.setting,
                {
                    "room": True,
                    "desc": neighbor_room.description,
                    "extra_desc": neighbor_room.background,
                    "size": 2000,  # TODO turk room sizes
                    "contain_size": 2000,  # TODO turk room sizes
                    "name_prefix": "the",
                    "surface_type": "in",
                    "classes": {"room"},
                },
                db_id=neighbor_room.db_id,
            )

        world = World(WorldConfig(opt=self.graph_opt, graph_builder=self))
        world.oo_graph = g
        return g, world

    async def get_constrained_graph(self, location=None, player=None, num_partners=1):
        """Take a few attempts to get the graph meeting the given constraints"""
        attempts = 9
        graph = None
        world = None
        while graph is None and attempts > 0:
            try:
                random.seed(time.time())
                graph, world = await self._get_constrained_graph(
                    location=location,
                    player=player,
                    num_partners=num_partners,
                )
            except Exception as _e:
                print(_e)
                attempts -= 1
        return graph, world

    async def get_graph(self):
        """Construct a graph using the grid created with build_world after
        selecting new characters and objects to place within.
        """
        return await self.get_constrained_graph(None, None, num_partners=1)

    async def get_contained_items(
        self, container_id, container_type, num_results=5, banned_items=None
    ):
        """
        Get prediction of contained items from StarSpace model
        given a container's database id and container type.
        """
        if banned_items is None:
            banned_items = []
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
        response = await self.agent_recommend(txt_feats, "object")
        ind = 0
        results = []
        while len(results) < num_results and ind < len(response["text_candidates"]):
            key = response["text_candidates"][ind]
            if "{{}}" in key:
                ind = ind + 1
                continue
            oid = self.objfeats_to_id(key)
            if oid is not None and oid not in banned_items:
                obj = self.get_obj_from_id(oid)
                if obj.is_gettable or not must_be_gettable:
                    results.append(obj)
            ind = ind + 1
        return results

    async def get_contained_characters(
        self, room_id, num_results=5, banned_characters=None
    ):
        """ Get prediction of contained characters in given room_id from StarSpace model."""
        if banned_characters is None:
            banned_characters = []
        if type(room_id) is str and room_id[0] == "f":
            # To check for filler_rooms, if it is filler_room, using the db_id of the room it has replaced
            room_id = room_id[1:]
        if room_id in self.roomid_to_feats:
            txt_feats = self.roomid_to_feats[room_id]
        else:
            txt_feats = self.get_text_features(self.get_room_from_id(room_id))
        response = await self.agent_recommend(txt_feats, "character")
        ind = 0
        results = []
        while len(results) < num_results:
            key = response["text_candidates"][ind]

            if "wench" in key:
                ind = ind + 1
                continue
            cind = self.charfeats_to_id(key)
            if cind is not None and cind not in banned_characters:
                results.append(self.get_char_from_id(cind))
            ind = ind + 1
            if len(response["text_candidates"]) <= ind:
                if len(results) == 0:
                    return None
                else:
                    return results
        return results

    def get_text_features(self, c, full=False):
        """Return text feature given a candidate and return and cache the text feature"""
        feat = ""
        if type(c) is DBRoom:
            feat = c.room_features(full)
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
