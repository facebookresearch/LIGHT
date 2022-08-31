#!/usr/bin/env python3
from parlai.core.params import ParlaiParser
import random
import asyncio
from light.graph.structured_graph import OOGraph
from light.graph.events.graph_events import ArriveEvent
from light.graph.builders.base import (
    DBGraphBuilder,
    POSSIBLE_NEW_ENTRANCES,
)
from light.world.world import World, WorldConfig


# TODO:  Refactor common functionality between builders!
class UserWorldBuilder(DBGraphBuilder):
    """Builds a LIGHT map using a predefined world saved to the light database."""

    def __init__(self, ldb, world_id=None, player_id=None, debug=True, opt=None):
        """Initializes required models and parameters for this graph builder"""

        if opt is None:
            parser = ParlaiParser(
                True,
                True,
                "Arguments for building a LIGHT world with User Defined Builder",
            )
            self.add_parser_arguments(parser)
            opt, _unknown = parser.parse_and_process_known_args()
        self.opt = opt
        self.filler_probability = opt["filler_probability"]
        self._no_npc_models = not opt["use_npc_models"]
        self.db = ldb
        DBGraphBuilder.__init__(self, self.db)
        self.debug = debug

        # Need world id to be non none, check that here
        self.world_id = world_id
        self.player_id = player_id

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

    def heuristic_name_cleaning(self, use_desc):
        if use_desc.lower().startswith("a "):
            use_desc = use_desc[2:]
        if use_desc.lower().startswith("an "):
            use_desc = use_desc[3:]
        if use_desc.lower().startswith("the "):
            use_desc = use_desc[4:]
        return use_desc

    def add_object_to_graph(self, g, obj, container_node, extra_props={}):
        """Adds a particular DBObject to the given OOgraph, adding to the specific
        container node. Returns the newly created object node"""
        obj.description = obj.description.capitalize()
        if obj.is_plural == 1:
            if not extra_props.get("not_gettable", False):
                # TODO: figure out making plurals work better
                return None
            else:
                # modify object description to make plural work.
                # TODO: fix in data
                desc = obj.description
                desc = f"You peer closer at one of them. {desc}"
                obj.description = desc
            obj_node = self._add_object_to_graph(g, obj, container_node)
            return obj_node

    def add_new_agent_to_graph(self, g, char, pos_room):
        if "is_banned" in vars(char):
            print("skipping BANNED character! " + char.name)
            return None
        if char.is_plural > 0:
            print("skipping PLURAL character! " + char.name)
            return None
        use_desc = char.name if char.is_plural == 0 else char.base_form
        use_desc = self.heuristic_name_cleaning(use_desc)
        if use_desc in [node.name for node in g.get_npcs()]:
            # Don't create the same agent twice.
            return None
        agent = g.add_agent(use_desc, self._props_from_char(char), db_id=char.db_id)
        agent.force_move_to(pos_room)

        # Is this necesary?  I have never seen these attributes...
        objs = {}
        for obj in char.carrying_objects["db"]:
            # Only use the database id objects, as add object to graph takes an obj_id
            objs[obj] = "carrying"
        for obj in char.wearing_objects["db"]:
            objs[obj] = "equipped"
        for obj in char.wielding_objects["db"]:
            objs[obj] = "equipped"

        for obj in objs:
            obj_node = self.add_object_to_graph(g, self.get_obj_from_id(obj), agent)
            if obj_node is not None:
                if objs[obj] == "equipped":
                    obj_node.set_prop("equipped", True)
        return agent

    async def add_random_new_agent_to_graph(self, world):
        # pick a random room
        g = world.oo_graph
        id = random.choice(list(g.rooms.keys()))
        pos_room = g.all_nodes[id]
        char = self.get_random_char()
        agent = self.add_new_agent_to_graph(g, char, pos_room)
        if agent is None:
            return

        # Send message notifying people in room this agent arrived.
        arrival_event = ArriveEvent(
            agent, text_content=random.choice(POSSIBLE_NEW_ENTRANCES)
        )
        arrival_event.execute(world)

    async def get_graph(self):
        """Return an OOGraph built by this builder"""
        g = OOGraph(self.opt)
        self.g = g
        with self.db as ldb:
            world = ldb.get_world(self.world_id, self.player_id)
            assert len(world) == 1, "Must get a single world back to load game from it"
            resources = ldb.get_world_resources(self.world_id, self.player_id)

        # Gives us the contains and neighbor edges
        edges = resources[1]
        edge_list = [dict(edge) for edge in edges]

        db_to_g = {}
        node_to_g = {}
        self.roomid_to_db = {}

        self.add_nodes(g, resources, db_to_g, node_to_g)
        self.add_edges(g, edge_list, node_to_g)

        world = World(WorldConfig(opt=self.opt, graph_builder=self))
        world.oo_graph = g
        return g, world

    def add_nodes(self, g, resources, db_to_g, node_to_g):
        """
        Iterates over the entities in the saved world, adding them
        to the graph as nodes
        """
        type_to_entities = {
            "room": resources[2],
            "agent": resources[3],
            "object": resources[4],
        }
        for type_ in type_to_entities.keys():
            for entity in type_to_entities[type_]:
                props = dict(entity)
                if type_ == "room":
                    props["desc"] = (
                        props["description"] if "description" in props else None
                    )
                    props["extra_desc"] = (
                        props["backstory"] if "backstory" in props else None
                    )
                else:
                    props["desc"] = (
                        props["physical_description"]
                        if "physical_description" in props
                        else None
                    )
                func = getattr(g, f"add_{type_}")
                # No uid or player for any of these
                g_id = func(props["name"], props, db_id=props["entity_id"]).node_id
                db_to_g[props["entity_id"]] = g_id
                node_to_g[props["id"]] = g_id
                if type_ == "room":
                    self.roomid_to_db[g_id] = props["entity_id"]

    def add_edges(self, g, edge_list, node_to_g):
        """
        Adds the edges from the edge_lsit to the graph, g, using node_to_g map
        to map ids
        """
        for edge in edge_list:
            src = g.get_node(node_to_g[edge["src_id"]])
            dst = g.get_node(node_to_g[edge["dst_id"]])
            edge = edge["edge_type"]
            # TODO: Link to light_database (hardcoding paths rn)
            if edge == "neighbors to the north":
                g.add_paths_between(
                    src, dst, "a path to the north", "a path to the south"
                )
            elif edge == "neighbors to the south":
                g.add_paths_between(
                    src, dst, "a path to the south", "a path to the north"
                )
            elif edge == "neighbors to the east":
                g.add_paths_between(
                    src, dst, "a path to the east", "a path to the west"
                )
            elif edge == "neighbors to the west":
                g.add_paths_between(
                    src, dst, "a path to the west", "a path to the east"
                )
            # This cannot be right...
            elif edge == "neighbors above":
                g.add_paths_between(src, dst, "a path to the up", "a path to the down")
            elif edge == "neighbors below":
                g.add_paths_between(src, dst, "a path to the down", "a path to the up")
            elif edge == "contains":
                dst.force_move_to(src)

    @staticmethod
    def add_parser_arguments(parser):
        """
        Add arguments to a parser to be able to set the required options for
        this builder
        """
        parser.add_argument(
            "--suggestion-type",
            type=str,
            default="model",
            help="Input 'model', 'human', or 'hybrid', for the suggestion type",
        )
        parser.add_argument(
            "--hybridity-prob",
            type=float,
            default=0.5,
            help="Set probability how often ex-object or character is skipped",
        )
        parser.add_argument(
            "--use-best-match-model",
            type="bool",
            default=False,
            help="use human suggestions for predicting placement things",
        )
        parser.add_argument(
            "--light-db-file",
            type=str,
            default="/checkpoint/light/data/database3.db",
            help="specific path for light database",
        )
        parser.add_argument(
            "--light-model-root",
            type=str,
            default="/checkpoint/light/models/",
            help="specific path for light models",
        )
        parser.add_argument(
            "--filler-probability",
            type=float,
            default=0.3,
            help="probability for retrieving filler rooms",
        )
        parser.add_argument(
            "--use-npc-models",
            type="bool",
            default=True,
            help="whether to use NPC model ",
        )
        parser.add_argument(
            "--map-size", type=int, default=6, help="define the size of the map"
        )
