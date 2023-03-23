#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai.core.params import ParlaiParser
from light.registry.models.starspace_model import MapStarspaceModelConfig
from light.world.world import World, WorldConfig
from light.graph.structured_graph import OOGraph
from light.registry.model_pool import ModelTypeName
from light.graph.builders.base import (
    DBGraphBuilder,
    GraphBuilderConfig,
    SingleSuggestionGraphBuilder,
)
from light.data_model.db.environment import (
    EnvDB,
    DBElem,
    DBAgent,
    DBObject,
    DBRoom,
    DBEdgeType,
)

import random
import time

from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig  # type: ignore
from typing import Dict, Any, List, Optional, Tuple, TYPE_CHECKING

from light.registry.model_pool import  ModelTypeName

from light.registry.model_pool import  ModelTypeName

if TYPE_CHECKING:
    from light.registry.model_pool import ModelPool
    from light.graph.elements.graph_nodes import (
        GraphNode,
        GraphObject,
        GraphAgent,
        GraphRoom,
    )

ROOM_TYPE = "room"
AGENT_TYPE = "agent"
OBJECT_TYPE = "object"

POSSIBLE_NEW_ENTRANCES = [
    "somewhere you can't see",
    "an undiscernable place",
    "a puff of smoke",
    "behind the shadows",
    "nowhere in particular",
    "a flash of light",
]


@dataclass
class OneRoomChatBuilderConfig(GraphBuilderConfig):
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


class OneRoomChatBuilder(DBGraphBuilder, SingleSuggestionGraphBuilder):
    """Builds a one-room light Graph using a StarSpace model to connect everything."""

    def __init__(
        self,
        builder_config: "OneRoomChatBuilderConfig",  # Configuration for this builder
        db: "EnvDB",
        model_pool: "ModelPool",  # Models this builder can use
        world_opt: Optional[WorldConfig] = None,
    ):
        """Initializes required models and parameters for this graph builder"""
        self.world_opt = WorldConfig() if world_opt is None else world_opt
        self.world_opt.graph_builder = self

        # Setup correct path
        DBGraphBuilder.__init__(self, builder_config, db)
        SingleSuggestionGraphBuilder.__init__(self, model_pool=model_pool)
        self.config: "OneRoomChatBuilderConfig" = builder_config

        self.load_models()
        self.use_best_match = builder_config.use_best_match_model
        self.suggestion_type = builder_config.suggestion_type
        # Cache for retrieved room/ char/ obj dicts from the database
        self.roomid_to_feats: Dict[str, str] = {}
        self.feats_to_roomid: Dict[str, str] = {}
        self.objid_to_feats: Dict[str, str] = {}
        self.feats_to_objid: Dict[str, str] = {}
        self.charid_to_feats: Dict[str, str] = {}
        self.feats_to_charid: Dict[str, str] = {}
        # paramter to control the hybridity of the model
        self.prob_skip_ex_objects = builder_config.hybridity_prob
        self.prob_skip_ex_char = builder_config.hybridity_prob
        self.allowed_characters = None
        self.banned_rooms = []
        self.room = None
        self.neighbors = []

    def load_models(self) -> None:
        """Load starspace models for building the map"""
        if not self.model_pool.has_model(ModelTypeName.CONNECTIONS):
            self.model_pool.register_model(
                self.config.model_loader_config, [ModelTypeName.CONNECTIONS]
            )
        self.agents["room"] = self.model_pool.get_model(
            ModelTypeName.CONNECTIONS, {"target_type": "room"}
        )
        self.agents["object"] = self.model_pool.get_model(
            ModelTypeName.CONNECTIONS, {"target_type": "object"}
        )
        self.agents["character"] = self.model_pool.get_model(
            ModelTypeName.CONNECTIONS, {"target_type": "character"}
        )

    def _props_from_obj(self, obj: DBObject) -> Dict[str, Any]:
        """Given a DBObject representing an object in the world, extract the
        required props to create that object in the world
        """
        use_classes = ["object"]
        props = {
            "object": True,
            "size": 1,
            "food_energy": 0,
            "value": 1,
            "desc": obj.physical_description,
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

    def _props_from_char(self, char: DBAgent) -> Dict[str, Any]:
        """Given a DBAgent representing a character in the world, extract the
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
            "desc": char.physical_description,
            "persona": char.persona,
        }
        props["classes"] = use_classes
        props["name_prefix"] = char.name_prefix
        if char.is_plural == 1:
            props["is_plural"] = True
        else:
            props["is_plural"] = False
        return props

    def _heuristic_name_cleaning(self, use_desc: str) -> str:
        """Remove some artifacts of bad data collection."""
        if use_desc.lower().startswith("a "):
            use_desc = use_desc[2:]
        if use_desc.lower().startswith("an "):
            use_desc = use_desc[3:]
        if use_desc.lower().startswith("the "):
            use_desc = use_desc[4:]
        return use_desc

    async def add_object_to_graph(
        self,
        g: OOGraph,
        obj: DBObject,
        container_node: "GraphNode",
        extra_props: Optional[Dict[str, Any]] = None,
    ) -> Optional["GraphNode"]:
        """Adds a particular DBObject to the given OOgraph, adding to the specific
        container node. Returns the newly created object node"""
        if obj is None:
            return None
        if extra_props is None:
            extra_props = {}
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
                # Currently only adding one layer of contained object of an object
                print(
                    "Adding CONTAINED objects to CONTAINER object to ",
                    obj.name,
                    obj.db_id,
                )
                contained_objs = await self.get_contained_items(
                    obj.db_id, OBJECT_TYPE, 3
                )
                for o in contained_objs:
                    if self._name_not_in_graph(g, o.name):
                        self._add_object_to_graph(g, o, obj_node)
            return obj_node

    def _name_not_in_graph(self, g: "OOGraph", name: str) -> bool:
        """check if a node with a certain name is contained in the graph"""
        return name not in [n.name for n in g.all_nodes.values()]

    def _add_object_to_graph(
        self,
        g: "OOGraph",
        obj: "DBObject",
        container_node: "GraphNode",
        extra_props: Optional[Dict[str, Any]] = None,
    ) -> "GraphObject":
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
        obj_node.force_move_to(container_node)
        return obj_node

    async def add_new_agent_to_graph(
        self,
        g: "OOGraph",
        char: "DBAgent",
        room_node: "GraphRoom",
    ) -> Optional["GraphAgent"]:
        """Add the given DBAgent to the given room (room_node) in the
        given OOGraph. Return the new agent node on success, and None on failure"""
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
            for obj_edge in char.node_edges:
                # Only use the database id objects, as add object to graph takes an obj_id
                if obj_edge.edge_type in [
                    DBEdgeType.WEARING,
                    DBEdgeType.MAY_WEAR,
                    DBEdgeType.WIELDING,
                    DBEdgeType.MAY_WIELD,
                ]:
                    objs[obj_edge.child_id] = "equipped"
                elif obj_edge.edge_type in [
                    DBEdgeType.CONTAINS,
                    DBEdgeType.MAY_CONTAIN,
                ]:
                    objs[obj_edge.child_id] = "carrying"
        elif self.suggestion_type == "model":
            objs = {
                obj.db_id: (
                    "equipped" if obj.is_wearable or obj.is_weapon else "carrying"
                )
                for obj in await self.get_contained_items(char.db_id, AGENT_TYPE)
            }
        if self.suggestion_type == "hybrid" and len(objs) == 0:
            objs = {
                obj.db_id: (
                    "equipped" if obj.is_weapon or obj.is_wearable else "carrying"
                )
                for obj in await self.get_contained_items(char.db_id, AGENT_TYPE, 2)
            }

        for obj in objs:
            obj_node = await self.add_object_to_graph(
                g, self.get_obj_from_id(obj), agent_node
            )
            if obj_node is not None:
                if objs[obj] == "equipped":
                    obj_node.set_prop("equipped", True)
        return agent_node

    async def add_random_new_agent_to_graph(self, world: World):
        """Add a random agent to the OOGraph at a random room node"""
        raise Exception("There shouldn't be any random additions")

    async def add_neighbors(self, room: "DBRoom") -> List["DBRoom"]:
        """Try to add all possible exits to a given room"""
        if self.use_best_match:
            neighbors = room.node_edges
            neighbors = [
                n.child for n in neighbors if n.edge_type == DBEdgeType.NEIGHBOR
            ]
        else:
            # Not using best match model but the starspace model for model prediction
            neighbors = await self.get_neighbor_rooms(
                room_id=room.db_id, banned_rooms=[]
            )
        return neighbors  # type: ignore

    ##########For best match model###################
    async def get_similar_element(
        self,
        txt_feats: str,
        element_type: str,
    ):
        """Given a text feature, and the corresponding Database type
        return an DBElement of the DB type"""
        agent_type = None
        banned_items = {}
        feats_to_id = None
        get_x_from_id = None
        if element_type == ROOM_TYPE:
            agent_type = "room"
            banned_items = self.banned_rooms
            feats_to_id = self.roomfeats_to_id
            get_x_from_id = self.get_room_from_id
        elif element_type == OBJECT_TYPE:
            agent_type = "object"
            feats_to_id = self.objfeats_to_id
            get_x_from_id = self.get_obj_from_id
        elif element_type == AGENT_TYPE:
            agent_type = "character"
            feats_to_id = self.charfeats_to_id
            get_x_from_id = self.get_char_from_id
        else:
            raise Exception(f"Invalid element type: {element_type}")
        if agent_type is not None:
            self.agents[agent_type].reset()
            msg = {"text": txt_feats, "episode_done": True}
            self.agents[agent_type].observe(msg)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.agents[agent_type].act)
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
        return await self.get_similar_element(txt_feats, ROOM_TYPE)

    async def get_similar_object(self, txt_feats):
        """Find a similar object to the text given
        based on starspace prediciton"""
        return await self.get_similar_element(txt_feats, OBJECT_TYPE)

    async def get_similar_character(self, txt_feats):
        """Find a similar object to the text given
        based on starspace prediciton"""
        return await self.get_similar_element(txt_feats, AGENT_TYPE)

    ###################################################

    async def get_neighbor_rooms(
        self,
        room_id: str,
        num_results: int = 5,
        banned_rooms: Optional[List[str]] = None,
    ) -> List[DBRoom]:
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
            if rind is not None and rind not in banned_rooms:
                res = self.get_room_from_id(rind)
                if res is not None:
                    results.append(res)
            ind = ind + 1
            if len(response["text_candidates"]) <= ind:
                if len(results) == 0:
                    return []
                else:
                    return results
        return results

    async def get_graph_from_quest(
        self, quest: Dict[str, Any]
    ) -> Tuple["OOGraph", "World"]:
        graph_json = quest["data"]["graph"]
        g = OOGraph.from_json(graph_json)
        world = World(self.world_opt)
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
                neighbor_room.name,
                {
                    "room": True,
                    "desc": neighbor_room.description,
                    "extra_desc": neighbor_room.backstory,
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
            rid = self.roomfeats_to_id(location)
            assert rid is not None, f"Provided location not found {location}"
            set_room = self.get_room_from_id(rid)

        assert set_room is not None, "No room found!"
        g = OOGraph()
        room_node = g.add_room(
            set_room.name,
            {
                "room": True,
                "desc": set_room.description,
                "extra_desc": set_room.backstory,
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
            room_id=set_room.db_id, num_results=15
        )
        room_edges = set_room.node_edges
        # add characters from the room
        possible_chars.extend(
            [  # type: ignore
                c.child
                for c in room_edges
                if c.edge_type
                in [DBEdgeType.CONTAINED_IN, DBEdgeType.MAY_BE_CONTAINED_IN]
                and isinstance(c.child, DBAgent)
            ]
        )

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

        in_objs = [  # type: ignore
            c.child
            for c in room_edges
            if c.edge_type in [DBEdgeType.CONTAINED_IN]
            and isinstance(c.child, DBObject)
        ]
        ex_objs = [  # type: ignore
            c.child
            for c in room_edges
            if c.edge_type in [DBEdgeType.MAY_BE_CONTAINED_IN]
            and isinstance(c.child, DBObject)
        ]

        for obj in ex_objs:
            if random.random() > self.prob_skip_ex_objects:
                continue
            if obj is not None:
                await self.add_object_to_graph(g, obj, room_node)
        for obj in in_objs:
            props = {}
            if obj is not None:
                await self.add_object_to_graph(g, obj, room_node, props)
        if self.suggestion_type == "model":
            predicted_objects = await self.get_contained_items(
                container_id=set_room.db_id, container_type=ROOM_TYPE
            )
            for o in predicted_objects:
                if o is not None:
                    room_node = g.get_node(set_room.g_id)
                    assert room_node is not None
                    await self.add_object_to_graph(g, o, room_node)

        neighbors = await self.get_neighbor_rooms(set_room.db_id)
        for neighbor_room in neighbors:
            if neighbor_room is None:
                continue
            g.add_room(
                neighbor_room.name,
                {
                    "room": True,
                    "desc": neighbor_room.description,
                    "extra_desc": neighbor_room.backstory,
                    "size": 2000,  # TODO turk room sizes
                    "contain_size": 2000,  # TODO turk room sizes
                    "name_prefix": "the",
                    "surface_type": "in",
                    "classes": {"room"},
                },
                db_id=neighbor_room.db_id,
            )

        world = World(WorldConfig(graph_builder=self))
        world.oo_graph = g
        return g, world

    async def get_constrained_graph(
        self,
        location: Optional[str] = None,
        player: Optional[str] = None,
        num_partners: int = 1,
    ) -> Tuple[Optional["OOGraph"], Optional["World"]]:
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
                import traceback

                traceback.print_exc()
                attempts -= 1
        return graph, world

    async def get_graph(self) -> Tuple[Optional["OOGraph"], Optional["World"]]:
        """Construct a graph using the grid created with build_world after
        selecting new characters and objects to place within.
        """
        return await self.get_constrained_graph(None, None, num_partners=1)

    async def get_contained_items(
        self,
        container_id: str,
        container_type: str,
        num_results: int = 5,
        banned_items: Optional[List[str]] = None,
    ) -> List[DBObject]:
        """
        Get prediction of contained items from StarSpace model
        given a container's database id and container type.
        """
        if banned_items is None:
            banned_items = []
        must_be_gettable = True
        if container_type == ROOM_TYPE:
            must_be_gettable = False
            if container_id in self.roomid_to_feats:
                txt_feats = self.roomid_to_feats[container_id]
            else:
                txt_feats = self.get_text_features(self.get_room_from_id(container_id))
        elif container_type == OBJECT_TYPE:
            if container_id in self.objid_to_feats:
                txt_feats = self.objid_to_feats[container_id]
            else:
                txt_feats = self.get_text_features(self.get_obj_from_id(container_id))
        elif container_type == AGENT_TYPE:
            if container_id in self.charid_to_feats:
                txt_feats = self.charid_to_feats[container_id]
            else:
                txt_feats = self.get_text_features(self.get_char_from_id(container_id))
        else:
            raise Exception(f"Improper container type given: {container_type}")
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
                if obj is not None and (obj.is_gettable or not must_be_gettable):
                    results.append(obj)
            ind = ind + 1
        return results

    async def get_contained_characters(
        self,
        room_id: str,
        num_results: int = 5,
        banned_characters: Optional[List[str]] = None,
    ) -> List[DBAgent]:
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
                res = self.get_char_from_id(cind)
                if res is not None:
                    results.append(res)
            ind = ind + 1
            if len(response["text_candidates"]) <= ind:
                if len(results) == 0:
                    return []
                else:
                    return results
        return results

    def get_text_features(self, c: DBElem, full: bool = False):
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
        if type(c) is DBAgent:
            feat = c.character_features(full)
            self.feats_to_charid[feat] = c.db_id
            self.charid_to_feats[c.db_id] = feat
        return feat


if __name__ == "__main__":
    import os
    from light import LIGHT_DIR
    from light.data_model.db.base import LightLocalDBConfig
    from light.registry.model_pool import ModelPool

    print("Generating a random starspace map")

    opt_path = os.path.join(
        LIGHT_DIR, "light/registry/models/config/baseline_starspace.opt"
    )

    config = OneRoomChatBuilderConfig(
        model_loader_config=MapStarspaceModelConfig(opt_file=opt_path)
    )
    env_db = EnvDB(LightLocalDBConfig(file_root=os.path.join(LIGHT_DIR, "prod_db")))

    map_dir = os.path.join(LIGHT_DIR, "scripts", "examples", "maps")
    while True:
        builder = OneRoomChatBuilder(config, env_db, ModelPool())
        graph, world = asyncio.run(builder.get_graph())
        assert graph is not None, "Graph failed to build"
        output_name = input("\nProvide output name:\n>") + ".json"
        output_dir = os.path.join(map_dir, output_name)
        with open(output_dir, "w+") as json_file:
            json_file.write(graph.to_json())
        print(f"Written to {output_dir}")
        if input("Another? (y to continue)") != "y":
            break
    print("Bye!")
