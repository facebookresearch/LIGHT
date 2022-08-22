#!/usr/bin/env python3
from light.graph.viz.graph_printer import GraphPrinter
from light.graph.structured_graph import OOGraph
from light.graph.elements.graph_nodes import GraphRoom
from light.world.action_parser import ActionParser

from copy import deepcopy
import emoji
import os
import random

from light.graph.utils import rm, deprecated
from light.graph.events.base import GraphEvent, ErrorEvent
from light.graph.events.graph_events import (
    SpawnEvent,
    SystemMessageEvent,
    DeleteObjectEvent,
    init_safety_classifier,
)
from light.graph.events.all_events_list import (
    ALL_EVENTS,
    ALL_EVENTS_LIST,
)
from light.graph.events.magic import init_magic
from light.graph.elements.graph_nodes import GraphNode, GraphAgent
from light.world.views import WorldViewer
from light.world.purgatory import Purgatory

from typing import List, Optional, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass, field


if TYPE_CHECKING:
    from light.data_model.db.episodes import EpisodeDB
    from light.graph.builders.base import GraphBuilder


def check_integrity(f):
    """Wrapper for ensuring that the world retains invariants both before and
    after all key function calls. To be used in debug mode only."""

    def wrapper(*args, **kwargs):
        world = args[0]
        if world.debug:
            world.check_graph()
            world.check_world()
        res = f(*args, **kwargs)
        if world.debug:
            world.check_graph()
            world.check_world()
        return res

    return wrapper


@dataclass
class WorldConfig:
    """
    Class containing (optional) world configuration data. Important for
    the sub-portions of the broader LIGHTConfig that are world-specific
    """

    # TODO create LIGHTConfig that can write out a WorldConfig
    # args: DictConfig (to replace opt)
    opt: Optional[Dict[str, Any]] = field(default_factory=dict)
    episode_db: Optional["EpisodeDB"] = None
    graph_builder: Optional["GraphBuilder"] = None


class World(object):
    """High-level class that manages gameplay logic for players over a graph.
    Should provide an interface to advance the game, register callbacks, and
    manage data for saving and storage. Wires the other components together
    Still very much defining the behavior clearly until deprecations are finished
    """

    def __init__(
        self,
        config: WorldConfig,
        debug: bool = False,
    ):
        self._config = config
        self._opt = config.opt
        self._node_freeze = False
        self._cnt = 0
        self.debug = debug
        self._oo_graph = OOGraph(config.opt)
        self.view = WorldViewer(self)
        self.purgatory = Purgatory(self)

        # TODO better specific player management?
        self._player_cnt = 0
        self._playerid_to_agentid = {}
        self._agentid_to_playerid = {}

        self.graph_builder = config.graph_builder

        # Set up safety classifier.
        init_safety_classifier(self._opt.get("safety_classifier_path", ""))

        # Set up magic!
        init_magic(self._opt.get("magic_db_path", "/scratch/light/data/magic.db"))

        # Set up action parser.

        self.action_parser = config.opt.get("_action_parser")
        if self.action_parser is None:
            self.action_parser = ActionParser(config.opt)

    @property
    def oo_graph(self):
        """Wrapper around oo_graph allowing us to do special configuration when set"""
        return self._oo_graph

    @oo_graph.setter
    def oo_graph(self, oo_graph: "OOGraph"):
        """
        Wrapper around oo_graph setter allowing us to properly attach room interaction
        loggers and handle other initialization
        """
        # TODO maybe there's a better way to do this? What happens when we add a new room
        # to an existin graph?
        self._oo_graph = oo_graph
        for room_node in oo_graph.room_id_to_loggers.values():
            room_node.episode_db = self._config.episode_db

    @staticmethod
    def from_graph(graph, config: WorldConfig = None):
        """Loads the world from the older versions of graph."""
        if config is None:
            config = WorldConfig()
        world = World(config)
        world.oo_graph = OOGraph.from_graph(graph)
        world._node_freeze = graph._node_freeze
        world._cnt = graph._cnt
        world._player_cnt = len(world.oo_graph.agents)
        return world

    # ------- debug and test helpers ------#

    def check_graph(self):
        """check the integrity of the graph in various ways."""
        self.oo_graph.assert_valid()

    def check_world(self):
        """check that the world itself is still consistent."""
        # TODO determine some invariants
        assert True

    # -- Graph properties -- #
    # These generally wrap OOGraph functionality to ensure backwards
    # compatibility with older graphs.

    def copy(self):
        """return a copy of this world"""
        # TODO copy the graph, then copy the world
        return deepcopy(self)

    def unique_hash(self):
        # TODO: consider world properties
        return self.oo_graph.to_json()

    def __eq__(self, other):
        return self.unique_hash() == other.unique_hash()

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, {})
        return result

    def all_node_ids(self):
        """return a list of all the node ids in the graph"""
        return self.oo_graph.get_all_ids()

    def save_graph(self, fname):
        """Save this graph to the file"""
        # TODO implement
        raise NotImplementedError

    def load_graph(self, fname):
        """load the contents of the file to this graph"""
        # TODO implement
        raise NotImplementedError

    def freeze(self, freeze=None):
        if freeze is not None:
            self._node_freeze = freeze
        return self._node_freeze

    def version(self):
        return 4

    # -- Full node editors/creators/getters/deleters -- #
    def add_node(self, desc, props, is_player=False, uid="", is_room=False):
        return self.oo_graph.add_node(
            desc, props, is_player=False, uid="", is_room=False
        )

    @deprecated
    def delete_node(self, id):
        self.oo_graph.mark_node_for_deletion(id)

    def node_exists(self, id):
        return self.oo_graph.node_exists(id)

    # -- Prop accessors -- #

    @deprecated
    def get_prop(self, id, prop, default=None):
        """Get the given prop, return None if it doesn't exist"""
        # TODO deprecate calls here, go to oo_graph
        node = self.oo_graph.get_node(id)
        if node is None:
            return "ErrorNodeNotFound"
        else:
            return node.get_prop(prop, default)

    @deprecated
    def set_prop(self, id, prop, val=True):
        """Set a prop to a given value, True otherwise"""
        # TODO deprecate calls here, go to oo_graph
        self.oo_graph.get_node(id).set_prop(prop, val)

    @deprecated
    def has_prop(self, id, prop):
        """Return whether or not id has the given prop"""
        # TODO deprecate calls here, go to node directly
        return self.get_prop(id, prop, False) is not False

    @deprecated
    def inc_prop(self, id, prop, val=1):
        """Increment a given prop by the given value"""
        # TODO deprecate calls here, go to node directly
        old_val = self.get_prop(id, prop, 0)
        new_val = old_val + val
        self.set_prop(id, prop, new_val)

    @deprecated
    def add_class(self, object_id, class_name):
        # TODO deprecate calls here, go to oo_graph
        self.oo_graph.get_node(object_id).add_class(class_name)

    @deprecated
    def remove_class(self, object_id, class_name):
        # TODO deprecate calls here, go to oo_graph
        self.oo_graph.get_node(object_id).remove_class(class_name)

    # -- Graph locators -- #

    @deprecated
    def location(self, node_id):
        """Get id of whatever the immediate container of a node is"""
        # TODO deprecate calls here, go to oo_graph
        return self.oo_graph.get_node(node_id).get_container().node_id

    @deprecated
    def room(self, node_id):
        """Get id of the room that contains a given node"""
        # TODO deprecate calls here, go to oo_graph
        return self.oo_graph.get_node(node_id).get_room().node_id

    @deprecated
    def node_contains(self, id):
        # TODO deprecate calls here, go to oo_graph
        return [x.node_id for x in self.oo_graph.get_node(id).get_contents()]

    @deprecated
    def desc_to_nodes(self, desc, nearbyid=None, nearbytype=None):
        """Get nodes nearby to a given node from that node's perspective"""
        # TODO deprecate calls here, go to oo_graph
        nearby_node = None if nearbyid is None else self.oo_graph.get_node(nearbyid)
        return [
            x.node_id
            for x in self.oo_graph.desc_to_nodes(desc, nearby_node, nearbytype)
        ]

    @deprecated
    def node_path_to(self, id):
        """get ids for the nodes that are this node's neighbors"""
        # TODO deprecate calls here, go to oo_graph
        room = self.oo_graph.get_node(id)
        assert isinstance(room, GraphRoom)
        return [x.node_id for x in room.get_neighbors()]

    @deprecated
    def get_actionable_ids(self, actor_id):
        # TODO deprectate when new action generator done
        o = self.get_local_ids(actor_id)
        new_o = set(o)
        for obj in o:
            if self.get_prop(obj, "container") or self.get_prop(obj, "agent"):
                new_o = new_o.union(self.node_contains(obj))
        return new_o

    def get_local_ids(self, actor_id):
        """Return all accessible ids for an actor given the current area"""
        return self.oo_graph.get_local_ids(actor_id)

    # -- Text creators -- #
    @deprecated
    def get_inventory_text_for(self, id, give_empty=True):
        """Get a description of what id is carrying or equipped with"""
        # TODO deprecate calls here to view
        return self.view.get_inventory_text_for(id, give_empty)

    @deprecated
    def health(self, id):
        """Return the text description of someone's numeric health"""
        # TODO deprecate calls here to view
        return self.view.get_health_text_for(id)

    # -- Text accessors -- #

    def get_action_history(self, agent_id):
        """Get the observation history for the given agent id"""
        agent = self.oo_graph.get_node(agent_id)
        return agent.get_observations()

    @deprecated
    def node_to_desc(self, id, from_id=False, use_the=False, drop_prefix=False):
        # TODO go straight to view
        return self.view.get_node_desc_id(id, from_id, use_the, drop_prefix)

    def node_to_desc_raw(self, id, from_id=False):
        node = self.oo_graph.get_node(id)
        if from_id:
            from_node = self.oo_graph.get_node(from_id)
            if isinstance(from_node, GraphRoom) and isinstance(node, GraphRoom):
                path_desc = self.view.path_to_desc_id(id, from_id)
                if path_desc is not False:
                    return path_desc

        return node.name

    # -- Messaging commands -- #

    def send_action(self, agent_id, action):
        """Parse the action and send it to the agent with send_msg"""
        if isinstance(action, GraphEvent):
            agent = agent_id
            if not isinstance(agent_id, GraphAgent):
                agent = self.oo_graph.get_node(agent_id)
            viewed_message = action.view_as(agent)
            self.send_msg(agent_id, viewed_message, action)
        else:
            # TODO update with action objects
            if action["caller"] is None:
                val = action["txt"]
                if type(val) is dict and "iter" in val:
                    i = val["iter"]
                    val["iter"] = (i + 1) % len(val["data"])
                    extracted_text = val["data"][i]
                else:
                    extracted_text = val
                self.send_msg(agent_id, extracted_text, action)
                return
            try:
                func_wrap = GRAPH_FUNCTIONS[action["caller"]]
            except BaseException:
                func_wrap = CONSTRAINTS[action["caller"]]
            try:
                t = func_wrap.format_observation(self, agent_id, action).rstrip()
            except Exception:
                # self.send_msg(agent_id, "You can't do that.")
                import traceback

                traceback.print_exc()
                return  # the agent doesn't accept observations
            t += " "
            self.send_msg(agent_id, t, action)

    def extract_action(self, agent_id, event):
        """
        Parse the given event and provide a graph-independent action
        of that event for consumption by other apis
        """
        return event.to_frontend_form(self.oo_graph.get_node(agent_id))

    def send_msg(self, agent_id, txt, action=None):
        """Send an agent an action and a message"""
        if isinstance(agent_id, GraphNode):
            # TODO eventually all cases should be this case
            agent = agent_id
        else:
            agent = self.oo_graph.get_node(agent_id)
        if agent is None:
            print(txt, agent_id)
        if action is None:
            action = SystemMessageEvent(agent, [], text_content=txt)
        self.purgatory.send_event_to_soul(action, agent)
        # TODO remove below when server game has Soul-based PlayerProvider
        agent.observe_action(txt, action)
        pos_playerid = self.agentid_to_playerid(agent_id)

    def broadcast_to_agents(self, action, agents, exclude_agents=None):
        """send a message to agents in the specified list """
        if exclude_agents is None:
            exclude_agents = []
        else:
            exclude_agents = list(exclude_agents)
        if isinstance(action, GraphEvent):
            for a in agents:
                if a in exclude_agents:
                    continue
                self.send_action(a, action)
            self.oo_graph.room_id_to_loggers[
                action.actor.get_room().node_id
            ].observe_event(action)
        else:
            if "actors" in action:
                # send message to the actor first
                actor = action["actors"][0]
                if actor in agents and actor not in exclude_agents:
                    self.send_action(actor, action)
                    exclude_agents.append(actor)
            action["present_agent_ids"] = agents
            for a in agents:
                if a in exclude_agents:
                    continue
                self.send_action(a, action)

    def broadcast_to_room(
        self, action, exclude_agents=None, told_by=None, target_room=None
    ):
        """send a message to everyone in a room"""
        if isinstance(action, GraphEvent):
            room = action.room if target_room is None else target_room
        else:
            room = self.oo_graph.get_node(action["room_id"])
        agents_list = [a.node_id for a in room.get_contents() if a.agent]
        agents = set(agents_list)
        self.broadcast_to_agents(action, agents, exclude_agents)
        # self._room_convo_buffers[action['room_id']].observe_turn(action)

    def broadcast_to_all_agents(self, action, exclude_agents=None, told_by=None):
        """send a message to everyone """
        agents = set(self.oo_graph.agents.values())
        self.broadcast_to_agents(action, agents, exclude_agents)

    # -- Create helpers -- #

    def create(self, agent_id, params):
        # TODO fix
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
        # from parlai_internal.tasks.graph_world3.class_nodes import (
        #     create_thing,
        #     CLASS_NAMES,
        # )

        if not self.has_prop(agent_id, "agent"):
            return False, "create"
        if params is None:
            return False, "create"
        room_id = self.room(agent_id)
        all_params = " ".join(params)
        txt = " ".join(params[1:])
        resp = "create " + " ".join(params)
        if not (all_params in ["save", "load", "freeze", "unfreeze"]):
            if txt == "":
                return False, resp
        if params[0] == "print":
            ids = self.desc_to_nodes(txt, nearbyid=agent_id, nearbytype="all")
            if len(ids) == 0:
                self.send_msg(agent_id, "Not found.\n ")
                return False, resp
            id = ids[0]
            self.send_msg(agent_id, id + " has:\n{}".format(self._node_to_prop[id]))
            return True, resp
        if params[0] == "save":
            self.save_graph(txt)
            self.send_msg(agent_id, "[ saved: " + self._save_fname + " ]\n")
            return True, resp
        if params[0] == "load" or params[0] == "reset":
            self.load_graph(txt)
            self.send_msg(agent_id, "[ loaded: " + self._save_fname + " ]\n")
            return True, resp
        if params[0] == "freeze":
            self.freeze(True)
            self.send_msg(agent_id, "Frozen.\n")
            return True, resp
        if params[0] == "unfreeze":
            self.freeze(False)
            self.send_msg(agent_id, "Unfrozen.\n")
            return True, resp
        if params[0] in ["delete", "del", "rm"]:
            ids = self.desc_to_nodes(txt, nearbyid=agent_id, nearbytype="all")
            if len(ids) == 0:
                self.send_msg("Not found.\n ")
                return False, resp
            id = ids[0]
            self.delete_node(id)
            self.send_msg(agent_id, "Deleted.\n")
            return True, resp
        if params[0] == "rename":
            params = self.split_params(params[1:], "to")
            to_ids = self.desc_to_nodes(params[0], nearbyid=agent_id, nearbytype="all")
            if len(to_ids) == 0:
                self.send_msg(agent_id, "Not found.\n ")
                return False, resp
            to_id = to_ids[0]
            self.set_desc(to_id, params[1])
            self.send_msg(agent_id, "Done.\n")
            return True, resp
        if params[0] == "agent":
            create_thing(self, room_id, params[0], force=True, use_name=txt)
            self.send_msg(agent_id, "Done.\n")
            return True, resp
        if params[0] == "room":
            new_id = self.add_node(txt, params[0])
            self.add_path_to(new_id, room_id)
            self.set_prop(new_id, "contain_size", 2000)
            self.send_msg(agent_id, "Done.\n")
            return True, resp
        if params[0] == "set_prop":
            params = self.split_params(params[1:], "to")
            to_ids = self.desc_to_nodes(params[0], nearbyid=agent_id, nearbytype="all")
            if len(to_ids) == 0:
                self.send_msg(agent_id, "Not found.\n ")
                return False, resp
            to_id = to_ids[0]
            key = params[1]
            value = True
            if "=" in key:
                sp = key.split("=")
                if len(sp) != 2:
                    return False, resp
                key = sp[0]
                value = sp[1]
                if value == "True":
                    value = True
                try:
                    value = int(value)
                except ValueError:
                    pass
            self.set_prop(to_id, key, value)
            self.send_msg(agent_id, "Done.\n")
            return True, resp
        if params[0] in CLASS_NAMES:
            if params[0] == "key" and txt.find("key") == -1:
                self.send_msg(agent_id, "Keys must be called keys!\n")
                return False, resp
            create_thing(self, room_id, params[0], force=True, use_name=txt)
            self.send_msg(agent_id, "Done.\n")
            return True, resp
        if params[0] == "lockable":
            ps = self.split_params(params[1:], "with")
            if len(ps) != 2:
                return False, resp
            to_ids = self.desc_to_nodes(ps[0], nearbyid=agent_id, nearbytype="all")
            with_ids = self.desc_to_nodes(ps[1], nearbyid=agent_id, nearbytype="all")
            if len(to_ids) == 0 or len(with_ids) == 0:
                self.send_msg(agent_id, "Something was not found.\n ")
                return False, resp
            to_id = to_ids[0]
            with_id = with_ids[0]
            if not self.get_prop(with_id, "key"):
                self.send_msg(agent_id, "You need to use a key!\n")
                return False, resp
            self.set_prop(to_id, "locked_with", with_id)
            self.set_prop(to_id, "locked", True)
            self.send_msg(agent_id, "Done.\n")
            return True, resp
        if params[0] == "path":
            to_id = self.desc_to_nodes(txt)
            if to_id is False:
                return False, resp
            self.add_path_to(to_id, room_id)
            self.send_msg(agent_id, "Done.\n")
            return True, resp
        self.send_msg(agent_id, "Create is not supported for: " + resp)
        return False, resp

    def split_params(self, params, word):
        """
        Split an incoming param phrase by a splitword or list of splitwords
        """
        if type(word) is str:
            word = {word}
        for w in word:
            search = " {} ".format(w)
            phrase = " ".join(params)
            if phrase.find(w) != -1:
                return phrase.split(search)
        return None

    # -- GraphFunction Helpers -- #

    @deprecated
    def path_is_locked(self, id1, id2):
        return False

    @deprecated
    def obj_fits(self, object_id, container_id):
        """Return if one object will fit into another"""
        # TODO ask the nodes directly, deprecate this
        test_object = self.oo_graph.get_node(object_id)
        test_container = self.oo_graph.get_node(container_id)
        return test_container.would_fit(test_object)

    @deprecated
    def move_object(self, object_id, container_id):
        """Move an object from wherever it is into somewhere else"""
        container = self.oo_graph.get_node(container_id)
        contained = self.oo_graph.get_node(object_id)
        contained.move_to(container)

    @deprecated
    # TODO update with players and actions
    def die(self, id):
        """Update an agent into a dead state"""
        node = self.oo_graph.get_node(id)
        if not node.agent:
            return False

        # TODO move graph interaction logic into the action
        if node.has_prop("human"):
            add_text = ""
            skull_msg = emoji.emojize(":skull:") * 31
            self.send_msg(
                id,
                "\n"
                + skull_msg
                + "\n"
                + "                      YOU ARE DEAD !!!       \n"
                + skull_msg
                + "\n",
            )

        agent_desc = self.node_to_desc(id, use_the=True).capitalize()
        self.broadcast_to_room(
            {
                "caller": None,
                "name": "died",
                "actors": [id],
                "room_id": node.get_room().node_id,
                "txt": agent_desc + " died!\n",
                "room_agents": self.get_room_agents(
                    self.location(id), drop_prefix=True
                ),
            },
            [id],
        )
        room = node.get_room()
        self.oo_graph.agent_die(node)
        return True

    @deprecated
    def get_room_edge_text(self, room_descs, past=False):
        """Get text for all the edges outside of a room"""
        # TODO update callsites to use view
        return self.view.get_room_edge_text(room_descs)

    @deprecated
    def get_room_object_text(self, object_descs, ents, past=False, give_empty=True):
        """Get text for all the objects in a room"""
        # TODO update callsites to use view
        return self.view.get_room_object_text(object_descs, ents, give_empty)

    @deprecated
    def get_room_agent_text(self, agent_descs, past=False):
        """Get text for all the agents in a room"""
        return self.view.get_room_agent_text(agent_descs)

    @deprecated
    def get_room_edges(self, room_id):
        """Return a list of edges from a room and their current descriptions"""
        room = self.oo_graph.get_node(room_id)
        neighbors = room.get_neighbors()
        neighbor_ids = [x.node_id for x in neighbors]
        neighbor_descs = [
            self.view.path_to_desc_id(id, room.node_id) for id in neighbor_ids
        ]
        return neighbor_ids, neighbor_descs

    @deprecated
    def get_nondescribed_room_objects(self, room_id):
        """Return a list of objects in a room and their current descriptions"""
        return self.get_room_objects(room_id, False)

    @deprecated
    def get_room_objects(self, room_id, show_descript=True):
        """Return a list of objects in a room and their current descriptions"""
        objects = self.node_contains(room_id)
        objects = [o for o in objects if self.get_prop(o, "object")]
        if not show_descript:
            objects = [
                o for o in objects if "described" not in self.get_prop(o, "classes")
            ]
        object_descs = [self.node_to_desc(o) for o in objects]
        return objects, object_descs

    @deprecated
    def get_nondescribed_room_agents(self, room):
        """Return a list of agents in a room and their current descriptions
        if those agents aren't described in the room text"""
        return self.get_room_agents(room, show_descript=False)

    @deprecated
    def get_room_agents(self, room, drop_prefix=False, show_descript=True):
        """Return a list of agents in a room and their current descriptions"""
        agents = self.node_contains(room)
        agents = [a for a in agents if self.get_prop(a, "agent")]
        if not show_descript:
            agents = [
                a for a in agents if "described" not in self.get_prop(a, "classes")
            ]
        agent_descs = [self.node_to_desc(a, drop_prefix=drop_prefix) for a in agents]
        return agents, agent_descs

    @deprecated
    def get_text(self, agent, clear_actions=True):
        """Get text from the text buffer for an agent, clear that buffer"""
        # TODO pull from agent directly
        return self.oo_graph.get_node(agent).get_text(clear_actions)

    def display_node(self, id):
        """Return the displayed form of a node's contents"""
        node = self.oo_graph.get_node(id)
        return self.view.node_contents(node)

    @deprecated
    def help(self):
        # TODO call directly from view
        return self.view.help_text()

    def print_graph(self, start_node, agentid, visited=False):
        return self._graph_printer.print(self, start_node, agentid, visited)

    def get_possible_actions(self, my_agent_id, use_actions=None):
        graph_events = self.get_possible_events(my_agent_id, use_actions)
        return [e.to_canonical_form() for e in graph_events]

    def get_possible_events(self, my_agent_id, use_actions=None):
        if self.get_prop(my_agent_id, "dead"):
            return []
        use_events = ALL_EVENTS_LIST
        if use_actions is not None:
            use_events = [ALL_EVENTS[name] for name in use_actions]

        actor_node = self.oo_graph.get_node(my_agent_id)

        all_events = []
        for EventClass in use_events:
            all_events += EventClass.get_valid_actions(self.oo_graph, actor_node)
        return all_events

    # TODO refactor parsing methods with action objects
    def help_message(self):
        h = ["Have you tried typing help?"]
        return random.choice(h)

    def parse_exec(self, actor, inst=None, event_id: Optional[str] = None):
        if not isinstance(actor, GraphNode):
            actor = self.oo_graph.get_node(actor)
        if self._opt.get("dont_catch_errors", False):
            return self.parse_exec_internal(actor, inst=inst, event_id=event_id)

        else:
            try:
                return self.parse_exec_internal(actor, inst=inst, event_id=event_id)
            except Exception:
                import traceback

                traceback.print_exc()
                self.send_msg(
                    actor, "Strange magic is afoot. This failed for some reason..."
                )
                return False, "FailedParseExec"

    def attempt_parse_event(
        self, EventClass, actor_node, arguments, event_id: Optional[str] = None
    ):
        """Return the possible parsed event given the event, actor, and arguments"""
        # Parse the text into string args
        possible_text_args = EventClass.split_text_args(actor_node, arguments)
        if isinstance(possible_text_args, ErrorEvent):
            return possible_text_args

        # Parse the string arguments into nodes
        for string_args in possible_text_args:
            result = EventClass.find_nodes_for_args(
                self.oo_graph, actor_node, *string_args
            )
            if not isinstance(result, ErrorEvent):
                break

        if isinstance(result, ErrorEvent):
            return result

        # Create the final event. May be an error but that's okay
        return EventClass.construct_from_args(
            actor_node, result.targets, result.text, event_id=event_id
        )

    def parse_exec_internal(self, actor, inst=None, event_id: Optional[str] = None):
        """Try to parse and execute the given event"""
        # basic replacements
        inst = self.action_parser.post_process(inst, actor)
        parse_shortcuts = {
            "e": "go east",
            "w": "go west",
            "n": "go north",
            "s": "go south",
            "ex self": "inv",
            "examine self": "inv",
        }
        if inst in parse_shortcuts:
            inst = parse_shortcuts[inst]
        if inst.startswith('"'):
            inst = "say " + inst

        instruction_list = inst.strip().split()

        if (
            len(inst) == 1
            and ((inst[0] == "respawn") or (inst[0] == "*respawn*"))
            and actor.get_prop("human")
            and actor.get_prop("dead")
        ):
            self.respawn_player(actor.node_id)
            return True, "Respawn"
        dead = actor.get_prop("dead")
        if dead or (dead == "ErrorNodeNotFound"):
            self.send_msg(
                actor,
                "You are dead, you can't do anything, sorry.\nType *respawn* to try at life again.\n",
            )
            return False, "dead"

        if instruction_list == []:
            errs = [
                "Huh?",
                "What?",
                "Are you going to type anything?",
                "Maybe try help...?",
                "Sigh.",
            ]
            self.send_msg(actor, random.choice(errs))
            return False

        executable = instruction_list[0].lower()
        arguments = " ".join(instruction_list[1:])

        hint_calls = ["a", "actions", "hints"]
        if executable in hint_calls:
            # TODO remove the list of valid instructions from the main game,
            # Perhaps behind an admin gatekeeper of sorts
            self.send_msg(
                actor, "\n".join(self.get_possible_actions(actor.node_id)) + "\n"
            )
            return True, "actions"
        if False:
            # Switch these off for now.
            if executable == "map" and len(arguments) == 0:
                # TODO fix print_graph
                self.send_msg(
                    actor, self.print_graph(actor.room(), actor.node_id, visited=False)
                )
                return True, "Print graph"
            if executable == "fogmap" and len(arguments) == 0:
                # TODO fix print_graph
                self.send_msg(
                    actor, self.print_graph(actor.room(), actor.node_id, visited=True)
                )
                return True, "Print graph"
            if executable == "commit" and arguments == "suicide":
                # TODO fix send_msg
                self.send_msg(actor, "You commit suicide!")
                self.die(actor.node_id)
                return True, "Suicide"
        if executable not in ALL_EVENTS:
            # Try again with the full model parser.
            new_inst = self.action_parser.parse(inst, actor)
            if new_inst != "":
                instruction_list = new_inst.strip().split()
                executable = instruction_list[0]
                arguments = " ".join(instruction_list[1:])
            if executable not in ALL_EVENTS:
                self.send_msg(
                    actor, "You can't {}. {}".format(executable, self.help_message())
                )
                return False, inst[0]

        EventClass = ALL_EVENTS[executable]

        parsed_event = self.attempt_parse_event(EventClass, actor, arguments, event_id)
        if isinstance(parsed_event, ErrorEvent):
            self.broadcast_to_agents(parsed_event, [actor])
            return False, inst
        else:
            parsed_event.execute(self)
            return True, parsed_event.to_canonical_form()

    def get_possible_player_nodes(self):
        """Return any nodes that would be allowed to be reinhabited by a player"""
        agents = self.oo_graph.get_npcs()
        allowed_agents = []
        for a in agents:
            if not a.usually_npc:
                # only allow a player to be from the non-NPC set
                allowed_agents.append(a)
        return allowed_agents

    # TODO refactor players
    def spawn_player(self, existing_player_id=-1):
        """Spawn the given player into an uninhabited npc in the graph"""
        possible_agents = self.oo_graph.get_npcs()
        if len(possible_agents) == 0:
            if existing_player_id != -1:
                # send message that we can't respawn
                a_id = self.playerid_to_agentid(existing_player_id)
                self.send_msg(
                    a_id,
                    "Your lost soul attempts to join the living...but the path is blocked.\n",
                )
            return -1

        # Pick an agent, then send event
        use_agent = random.choice(possible_agents)
        a_id = use_agent.node_id
        if existing_player_id == -1:
            self._player_cnt += 1
            p_id = "_player_" + str(self._player_cnt)
        else:
            self.send_msg(
                self.playerid_to_agentid(existing_player_id),
                "Your lost soul attempts to join the living...\n",
            )
            p_id = existing_player_id

        use_agent.set_player(p_id)

        self._playerid_to_agentid[p_id] = a_id
        self._agentid_to_playerid[a_id] = p_id
        # self._room_convo_buffers[self.room(a_id)].enter_human()

        event = SpawnEvent(use_agent)
        event.execute(self)
        return p_id

    def playerid_to_agentid(self, pid):
        return self._playerid_to_agentid[pid]

    def agentid_to_playerid(self, aid):
        return self._agentid_to_playerid.get(aid)

    # TODO refactor players
    def respawn_player(self, a_id):
        p_id = self.agentid_to_playerid(a_id)
        if p_id != None:
            try:
                old_node = self.oo_graph.get_node(a_id)
                if old_node.agent:
                    old_node.set_player(None)
            except Exception:
                pass
            p_id2 = self.spawn_player(existing_player_id=p_id)
            new_a_id = self.playerid_to_agentid(p_id2)
            self.parse_exec(new_a_id, "look")

    def clean_corpses_and_respawn(self) -> List[GraphAgent]:
        """
        Clean any corpses that have been lying around for a while,
        then try to do a respawn for each corpse cleaned.

        Return any respawned GraphAgent nodes created like this
        """
        dead_nodes = self.oo_graph.get_dead_nodes()
        cleaned_count = 0
        for node in dead_nodes:
            if node.ready_to_clean_corpse():
                cleaned_count += 1
                clear_event = DeleteObjectEvent(
                    actor=node, text_content="corpse disintegrates in a puff of magic."
                )
                clear_event.execute(self)

        created = []
        if self.graph_builder is not None:
            for _x in range(cleaned_count):
                new_agent = self.graph_builder.add_random_new_agent_to_graph(self)
                if new_agent is not None:
                    created.append(new_agent)
        return created
