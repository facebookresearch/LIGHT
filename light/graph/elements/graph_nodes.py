#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import random
import json
from typing import List, Set

UNINTERESTING_PHRASES = [
    "There's nothing special about it.",
    "You really don't have a good reason to be examining this closer.",
    "You try to get a better look, but it's just as non-descript.",
    # TODO more uninteresting phrases?
]

DEAD_DESCRIPTIONS = [
    "They look pretty dead.",
    "They are very dead.",
    "Their corpse is inanimate.",
]


def node_to_json(node):
    return json.dumps(node, cls=GraphEncoder, sort_keys=True, indent=4)


# TODO:  refactor to not use here
class GraphEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return sorted(list(o))
        if isinstance(o, list):
            return sorted(o)
        if isinstance(o, GraphEdge):
            return {k: v for k, v in o.__dict__.copy().items() if not k.startswith("_")}
        if not isinstance(o, GraphNode):
            return super().default(o)
        use_dict = {k: v for k, v in o.__dict__.copy().items() if not k.startswith("_")}
        return use_dict


class GraphEdge(object):
    """Representative structure for having an edge between two nodes in the
    graph. Provides an interface for dereferencing edges but can still be
    serialized"""

    EDGE_TYPE = "GraphEdge"

    def __init__(self, target_node):
        assert isinstance(
            target_node, GraphNode
        ), f"Edges must be to other graph nodes, given {target_node}"
        self._target_node = target_node
        self.target_id = target_node.node_id

    def get(self):
        return self._target_node

    def __repr__(self):
        return f"{self.EDGE_TYPE}({self._target_node})"


class LockEdge(GraphEdge):
    def __init__(self, locking_node, is_locked=True, locked_desc=None):
        super().__init__(locking_node)
        self.is_locked = is_locked
        self.locked_desc = locked_desc

    def lock(self):
        self.is_locked = True

    def unlock(self):
        self.is_locked = False

    def get_is_locked(self):
        return self.is_locked


class NeighborEdge(GraphEdge):
    """Structure for edges between rooms in a graph. Contains relevant details
    for traversing through the graph"""

    def __init__(self, target_node, label=None, examine_desc=None, locked_edge=None):
        super().__init__(target_node)
        self.label = label
        self.examine_desc = examine_desc
        self.locked_edge = locked_edge

    def get_examine_desc(self):
        """Return the description this path should give when examined"""
        # TODO consider locking
        return self.examine_desc

    # TODO consider locking in multiplayer games - keys per player?
    def lock_path(self, key_node):
        """lock the edge from id1 to id2 using the given key"""
        assert self.locked_edge is not None, "Cannot unlock path with no lock"
        self.locked_edge.lock()

    def unlock_path(self, id1, id2, key_id):
        """unlock the edge from id1 to id2 using the given key"""
        assert self.locked_edge is not None, "Cannot lock path with no lock"
        self.locked_edge.unlock()

    def path_is_locked(self):
        return self.locked_edge is not None and self.locked_edge.get_is_locked()

    def get_path_locked_with(self):
        return self.locked_edge.get()


class GraphNode(object):
    """Node object for contents in the graph. Everything in the graph
    has this structure, and thus shared functionality should all go here"""

    DEFAULT_CONTAIN_SIZE = 20
    DEFAULT_SIZE = 1
    NODE_TYPE = "GraphNode"

    # -------- Creating functions -------- #

    def __init__(self, node_id, name, props=None, db_id=None):
        """Init this node from an existing place in the graph"""
        # TODO force props, or define a props object. Special props can be
        # class members (and handled differently by get_prop and other methods)
        if props is None:
            props = {}
        self._props = props.copy()

        if 'contain_size' in self._props and self._props['contain_size'] is None:
            del self._props['contain_size']
        if 'size' in self._props and self._props['size'] is None:
            del self._props['size']

        # TODO perhaps these should be edges rather than special cases?
        self.container_node = None
        self.contained_nodes = {}

        # Properties of all graph nodes
        self.contain_size = self._props.get("contain_size", 20)
        self.size = self._props.get("size", 1)
        self.node_id = node_id
        self.db_id = db_id  # TODO populate with id from the database
        self.name = name
        self.name_prefix = self._props.get(
            "name_prefix", "an" if name[0] in "aeiou" else "a"
        )
        self.names = self._props.get("names", [self.name]).copy()
        field = "desc"
        if "desc" not in self._props:
            field = "physical_description"
        self.desc = self._props.get(field, random.choice(UNINTERESTING_PHRASES))
        self.classes = set(self._props.get("classes", set()).copy())

        self.agent = False
        self.room = False
        self.object = False
        self._is_from_graph = False
        self._is_from_json = False

        # TODO there are probably more properties currently abstracted by
        # the overarching graph class

    @classmethod
    def from_graph(cls, graph, node_id):
        """Init this node from an existing place in the graph"""
        node = cls(node_id, graph._node_to_desc[node_id], graph._node_to_prop[node_id])
        node._graph = graph
        node._container_id = graph.location(node_id)
        node._contained_ids = graph.node_contains(node_id)
        node._is_from_graph = True
        return node

    @classmethod
    def from_json_dict(cls, input_dict):
        """Init this node from a json encoding of the original node"""
        node = cls(input_dict.get("node_id", -1), input_dict["name"], props=input_dict,)
        if "container_node" in input_dict:
            node._container_id = input_dict["container_node"]["target_id"]
        if "contained_nodes" in input_dict:
            node._contained_ids = [
                x["target_id"] for x in input_dict["contained_nodes"].values()
            ]
        node._is_from_json = True
        return node

    def sync(self, all_node_list):
        """Populate remaining fields that could not be created with from_graph
        because dependent nodes didn't exist yet"""
        assert (
            self._is_from_graph or self._is_from_json
        ), "Only need to sync nodes created from static"
        if self._container_id is not None:
            if all_node_list.get(self._container_id) is None:
                print(self, all_node_list, self._container_id)
            self.container_node = GraphEdge(all_node_list.get(self._container_id))
        self.contained_nodes = {
            x: GraphEdge(all_node_list[x]) for x in self._contained_ids
        }

    # -------- Node validation functions ---------- #

    def assert_valid(self):
        """Ensure no invariants are broken for this node that would make it
        impossible to exist"""
        assert self.size is not None
        assert self.contain_size is not None
        assert self.name is not None
        assert self.desc is not None
        assert self.contain_size >= 0
        assert self.size >= 0
        assert self.container_node is None or isinstance(self.container_node, GraphEdge)
        assert self.get_container() != self
        assert self.get_container() is None or isinstance(
            self.get_container(), GraphNode
        )

    # ------- Simple property accessors and mutators -------- #

    def get_contain_size(self):
        """Return the remaining containment size for this object"""
        # TODO contain_size should be a special prop
        return self.contain_size

    def add_contained_node(self, contained_node):
        """Add the given node to the nodes contained within the self node
        Following a successful call to update containment, the container
        of contained_node should be updated to be this node with set_container
        """
        assert isinstance(
            contained_node, GraphNode
        ), f"Only nodes can be inserted, found {contained_node}"
        assert (
            contained_node not in self.get_contents()
        ), "Given node already inside this node"
        assert contained_node is not self, "Can't put node in itself"
        assert contained_node.size <= self.contain_size, "Can't fit anything else"
        self.contained_nodes[contained_node.node_id] = GraphEdge(contained_node)
        self.contain_size -= contained_node.size

    def remove_contained_node(self, contained_node):
        """Remove the given node from the list of nodes contained in this one"""
        assert contained_node.node_id in self.contained_nodes, "Given node not present"
        del self.contained_nodes[contained_node.node_id]
        self.contain_size += contained_node.size

    def get_contents(self):
        """get copy of the list of nodes inside this node"""
        return [x.get() for x in self.contained_nodes.values()]

    def set_container(self, container_node):
        """Set the container and container id for this node"""
        assert container_node is not self, "Can't put node in itself"
        assert (
            container_node not in self.get_contents()
        ), "Can't create containment loop"
        assert isinstance(
            container_node, GraphNode
        ), f"Only nodes can be inserted, found {container_node}"
        self.container_node = GraphEdge(container_node)
        self._container_id = container_node.node_id

    def reset_container(self):
        """Clear the container set for this node"""
        self.container_node = None
        self._container_id = None

    def get_container(self):
        """Get this node's immediate container"""
        if self.container_node is None:
            return None
        return self.container_node.get()

    def get_prop(self, prop_name, default=False):
        return self.__dict__.get(prop_name, default)

    def has_prop(self, prop_name):
        """Return if the node has the given prop"""
        return self.get_prop(prop_name) is not False

    def set_prop(self, prop_name, val):
        """Set key class attributes as props for this node"""
        # TODO - try not to use this until formalized, it's hard to track
        self.__dict__[prop_name] = val

    def add_class(self, class_name):
        """Add a class to this node"""
        self.classes.add(class_name)

    def remove_class(self, class_name):
        """remove a class from this node"""
        self.classes.remove(class_name)

    def get_room(self) -> "GraphRoom":
        """get this node's first containing room"""
        checked_nodes: Set["GraphNode"] = set()
        node = self
        while not node.room:
            assert node not in checked_nodes, "detected a containment cycle"
            checked_nodes.add(node)
            node = node.get_container()
            if node is None:
                return False  # There is no room in the chain
        assert isinstance(node, GraphRoom), "node.room set but not GraphRoom"
        return node

    def get_view(self):
        """Nicely named wrapper for getting the view desciption of this node"""
        return self.get_view_from()

    def get_view_from(self, from_node=None):
        """Return how this node would look like from the given location"""
        return self.name

    def get_prefix_view(self):
        """Return the name of this node, with any expected prefix"""
        return f"{self.name_prefix} {self.get_view()}"

    def get_prefix_view_from(self, from_node=None):
        """Return the name of this node, with any expected prefix"""
        return f"{self.name_prefix} {self.get_view_from(from_node)}"

    def get_names(self):
        """Return all names for this node"""
        return list(self.names)

    def __repr__(self):
        return f"{self.NODE_TYPE}({self.node_id})"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return node_to_json(self) == node_to_json(other)
        else:
            return False

    # Have to override hash, but do not want to
    def __hash__(self):
        return super.__hash__(self)

    # -------- Derived functions that employ some graph logic ------ #

    def would_fit(self, other_node):
        """See if other_node would fit into this node"""
        assert isinstance(
            other_node, GraphNode
        ), f"Only nodes can be checked, given {other_node}"
        return other_node.size <= self.get_contain_size()

    def move_to(self, container_node):
        """Move this node into the node specified in container_node, update
        containing edges, update sizes.
        """
        # Remove from the old container if it exists
        old_container = self.get_container()
        if old_container is not None:
            old_container.remove_contained_node(self)
        # Add to new container and update
        container_node.add_contained_node(self)
        self.set_container(container_node)

    def force_move_to(self, container_node):
        """Force this node into the node specified in container_node, update
        containing edges.

        Only call when building a world or killing an agent. Other calls can
        cause the contain sizes for nodes vary in an untracable way
        """
        # Remove from the old container if it exists
        old_container = self.get_container()
        if old_container is not None:
            if self.node_id in old_container.contained_nodes:
                if old_container.contained_nodes[self.node_id].get() == self:
                    del old_container.contained_nodes[self.node_id]
        # Add to new container and update
        container_node.contained_nodes[self.node_id] = GraphEdge(self)
        self.set_container(container_node)

    def delete_and_cleanup(self):
        """Remove this node and all contents from being linked, return nodes deleted"""
        old_container = self.get_container()
        if old_container is not None:
            old_container.remove_contained_node(self)

        # all things inside this are deleted too
        contained_nodes = self.get_contents()
        deleted_nodes = contained_nodes.copy()
        for node in contained_nodes:
            deleted_nodes += node.delete_and_cleanup()
        return list(set(deleted_nodes + [self]))


class GraphVoidNode(GraphNode):
    """Initial container of everything still in the world"""

    INIT_CONTAIN_SIZE = 10000000

    NODE_TYPE = "VoidNode"

    def __init__(self):
        super().__init__("VOID", "VOID", {})
        self.void = True
        # TODO make it possible to have infinite contain size
        self.contain_size = self.INIT_CONTAIN_SIZE

    def get_container(self):
        return self

    def get_contents(self):
        return super().get_contents() + [self]


class GraphRoom(GraphNode):
    """Represents rooms in the graph. Has all required attributes."""

    DEFAULT_CONTAIN_SIZE = 100000
    NODE_TYPE = "GraphRoom"

    def __init__(self, node_id, name, props=None, db_id=None):
        super().__init__(node_id, name, props, db_id)
        self.room = True
        if props is not None and 'desc' not in props:
            self.desc = props.get('description', '')
        self.extra_desc = self._props.get("extra_desc", self.desc)
        self.name_prefix = self._props.get("name_prefix", "the")
        self.surface_type = self._props.get("surface_type", "in")
        self.classes = set(self._props.get("classes", {"room"}))
        self.contain_size = self._props.get("contain_size", self.DEFAULT_CONTAIN_SIZE)
        self.grid_location = self._props.get("grid_location", [0, 0, 0])
        self.neighbors = {}

    def assert_valid(self):
        """Ensure no invariants are broken for this node that would make it
        impossible to exist"""
        super().assert_valid()
        assert isinstance(self.neighbors, dict)
        for x in self.get_neighbors():
            assert isinstance(x, GraphRoom)

    def get_neighbors(self) -> List["GraphRoom"]:
        """return the neighboring nodes across outgoing edges from this room"""
        return list([x.get() for x in self.neighbors.values()])

    def get_edge_to(self, other_node):
        """return edge to the other node if it exists, None otherwise"""
        assert other_node is not self, "Can't have self edge"
        assert isinstance(
            other_node, GraphRoom
        ), f"Only rooms can be checked, not {other_node}"
        return self.neighbors.get(other_node.node_id)

    def get_view_from(self, from_node=None):
        """Return how this node would look like from the given location"""
        if from_node is None:
            return self.name
        elif from_node == self:
            return self.name
        elif self in from_node.get_neighbors():
            return from_node.get_edge_to(self).label
        else:
            return self.name

    def add_neighbor(
        self,
        other_node,
        edge_label=None,
        locked_with=None,
        edge_desc=None,
        full_label=False,
        is_locked=False,
    ):
        """Add an edge to another room. Takes optional view label,
        locking node, and examine description
        """
        locked_edge = None
        if locked_with is not None:
            # TODO update with locking descriptions
            locked_edge = LockEdge(locked_with, is_locked, None)
        self.neighbors[other_node.node_id] = NeighborEdge(
            other_node, edge_label, edge_desc, locked_edge
        )

    def remove_neighbor(self, other_node):
        assert (
            other_node in self.get_neighbors()
        ), "Can't remove neighbor that isn't there"
        del self.neighbors[other_node.node_id]

    def delete_and_cleanup(self):
        """Remove this room from being present in the graph, return nodes deleted"""
        deleted_nodes = super().delete_and_cleanup()
        # now remove edges from other rooms
        for neighbor_node in self.get_neighbors():
            if self in neighbor_node.get_neighbors():
                neighbor_node.remove_neighbor(self)
        return deleted_nodes


class GraphAgent(GraphNode):
    """Represents agents in the graph. Has all required attributes."""

    DEFAULT_SIZE = 20
    DEFAULT_CONTAIN_SIZE = 20
    DEFAULT_MAX_WEARABLE_ITEMS = 3
    DEFAULT_MAX_WIELDABLE_ITEMS = 1
    DEFAULT_HEALTH = 6
    DEFAULT_MOVEMENT_ENERGY_COST = 0.00
    DEFAULT_SPEED = 10
    DEFAULT_STRENGTH = 0
    DEFAULT_DEXTERITY = 0
    DEFAULT_PERSONA = "I am a player in the LIGHT world."
    DEFAULT_TAGS = []
    # NPC Defaults
    DEFAULT_AGGRESSION = 0
    DEFAULT_ATTACK_TAGGED_AGENTS = []
    DEFAULT_MAX_DISTANCE_FROM_START_LOCATION = 1000000
    DEFAULT_DONT_ACCEPT_GIFTS = False

    NODE_TYPE = "GraphAgent"

    def __init__(self, node_id, name, props=None, db_id=None):
        super().__init__(node_id, name, props, db_id)
        self.agent = True
        self.size = self._props.get("size", self.DEFAULT_SIZE)
        self.strength = self._props.get("strength", self.DEFAULT_STRENGTH)
        self.dexterity = self._props.get("dexterity", self.DEFAULT_DEXTERITY)
        self.contain_size = self._props.get("contain_size", self.DEFAULT_CONTAIN_SIZE)
        self.max_wearable_items = self._props.get(
            "max_wearable_items", self.DEFAULT_MAX_WEARABLE_ITEMS
        )
        self.max_wieldable_items = self._props.get(
            "max_wieldable_items", self.DEFAULT_MAX_WIELDABLE_ITEMS
        )
        self.num_wearable_items = self._props.get("num_wearable_items", 0)
        self.num_wieldable_items = self._props.get("num_wieldable_items", 0)
        self.contain_size = self._props.get("contain_size", self.DEFAULT_CONTAIN_SIZE)
        self.health = self._props.get("health", self.DEFAULT_HEALTH)
        self.movement_energy_cost = self._props.get(
            "movement_energy_cost", self.DEFAULT_MOVEMENT_ENERGY_COST
        )
        self.damage = self._props.get("damage", 1)
        self.defense = self._props.get("defense", 0)
        self.food_energy = self._props.get("food_energy", 1)
        self.name_prefix = self._props.get("name_prefix", "the")
        self.char_type = self._props.get("char_type", "person")
        self.classes = set(self._props.get("classes", {"agent"}))
        self.persona = self._props.get("persona", self.DEFAULT_PERSONA)
        self.on_events = self._props.get("on_events", None)
        if self._props.get("dead", None) is not None:
            self.dead = self._props.get("dead")
        else:
            self.dead = False
        # Flag to resolve when a death event is in the stack, but possibly not processed
        self._dying = False
        self.is_player = self._props.get("is_player", False)
        self.usually_npc = self._props.get("usually_npc", False)
        self.pacifist = self._props.get("pacifist", False)
        self.tags = self._props.get("tags", self.DEFAULT_TAGS)

        self.following = None
        self.followed_by = {}

        self.blocking = None
        self.blocked_by = {}

        # NPC properties. TODO move to another class somehow?
        self.aggression = self._props.get("aggression", self.DEFAULT_AGGRESSION)
        self.speed = self._props.get("speed", self.DEFAULT_SPEED)
        self.max_distance_from_start_location = self._props.get(
            "max_distance_from_start_location",
            self.DEFAULT_MAX_DISTANCE_FROM_START_LOCATION,
        )
        self.dont_accept_gifts = self._props.get(
            "dont_accept_gifts", self.DEFAULT_DONT_ACCEPT_GIFTS
        )
        self.attack_tagged_agents = self._props.get(
            "attack_tagged_agents", self.DEFAULT_ATTACK_TAGGED_AGENTS
        )

        if self.on_events is None:
            self.on_events = []
        self.quests = self._props.get("quests", [])
        self.mission = self._props.get("mission", '')

        # Game properties to track for this agent, TODO move to other class?
        self._human = False
        self._current_player = None
        self.clear_memory()

    def assert_valid(self):
        """Ensure no invariants are broken for this node that would make it
        impossible to exist"""
        super().assert_valid()
        assert self.following is None or isinstance(self.following, GraphEdge)
        assert self.blocking is None or isinstance(self.blocking, GraphEdge)
        assert isinstance(self.followed_by, dict)
        assert isinstance(self.blocked_by, dict)
        for key, value in self.followed_by:
            assert value.get().node_id == key
            assert value.get().following == self
        for key, value in self.blocked_by:
            assert value.get().node_id == key
            assert value.get().blocking == self
        for x in self.get_followers():
            assert isinstance(x, GraphAgent)
        for x in self.get_blockers():
            assert isinstance(x, GraphAgent)
        assert self.get_following() is None or isinstance(
            self.get_following, GraphAgent
        )
        assert self.get_blocking() is None or isinstance(self.get_blocking, GraphAgent)

    def block(self, other_agent):
        """Create an edge between this and the agent being blocked"""
        assert isinstance(
            other_agent, GraphAgent
        ), f"Can only block agents, given {other_agent}"
        assert self.node_id not in other_agent.blocked_by, "Already blocking"
        assert (
            other_agent.get_room() == self.get_room()
        ), "Can only block agents in the same room"
        self.blocking = GraphEdge(other_agent)
        other_agent.blocked_by[self.node_id] = GraphEdge(self)

    def unblock(self):
        """Remove the edges between this agent and the agent they are blocking"""
        assert self.blocking is not None, "Not blocking anyone"
        blocked_agent = self.blocking.get()
        del blocked_agent.blocked_by[self.node_id]
        self.blocking = None

    def get_blockers(self):
        """Get a list of the nodes blocking this node"""
        return [x.get() for x in self.blocked_by.values()]

    def get_blocking(self):
        if self.blocking is None:
            return None
        return self.blocking.get()

    def follow(self, other_agent):
        """Create an edge between this and the agent being followed"""
        assert isinstance(
            other_agent, GraphAgent
        ), f"Can only follow agents, given {other_agent}"
        assert self.node_id not in other_agent.followed_by, "Already following"
        assert (
            other_agent.get_room() == self.get_room()
        ), "Can only follow agents in the same room"
        self.following = GraphEdge(other_agent)
        other_agent.followed_by[self.node_id] = GraphEdge(self)

    def unfollow(self):
        """Remove the edges between this agent and the agent they are following"""
        assert self.following is not None, "Not following anyone"
        followed_agent = self.following.get()
        del followed_agent.followed_by[self.node_id]
        self.following = None

    def get_followers(self):
        """Get a list of the nodes following this node"""
        return [x.get() for x in self.followed_by.values()]

    def get_following(self):
        if self.following is None:
            return None
        return self.following.get()

    def delete_and_cleanup(self):
        """Remove this agent from being present in the graph, return nodes deleted"""
        deleted_nodes = super().delete_and_cleanup()
        if self.get_following() is not None:
            self.unfollow()
        if self.get_blocking() is not None:
            self.unblock()
        for node in self.get_followers():
            node.unfollow()
        for node in self.get_blockers():
            node.unblock()
        # TODO sever the player connection

        return deleted_nodes

    # ------------ player logic ----------#
    # TODO move into a player class, link from here

    def clear_memory(self):
        """Clear memory buffers for this player"""
        # TODO consider moving to a player object
        self._text_buffer = ""  # clear buffer
        self._observations = []  # clear buffer
        self._visited_rooms = set()
        self._last_room = None

    def get_text(self, clear_actions=True):
        """Return the text in this agent's buffer"""
        txt = self._text_buffer
        self._text_buffer = ""  # clear buffer
        if clear_actions:
            self._observations = []  # clear buffer
        return txt

    def observe_action(self, text, action=None):
        """Observe text and an optional action. Update local state to store
        the new action"""
        if action is None:
            action = {"caller": None, "room_id": self.get_room(), "txt": text}
        self._observations.append(action)
        if text is not None:
            self._text_buffer += text

    def get_observations(self):
        """Return all the observations from this character's history"""
        obs = []
        while len(self._observations) > 0:
            obs.append(self._observations.pop(0))
        return obs

    def set_player(self, current_player):
        """Have a new player take over this agent. None returns to npc"""
        self._human = current_player is not None
        self.clear_memory()
        self._current_player = current_player

    def die(self):
        """Kill off this agent, turn them into an object"""
        self.desc = random.choice(DEAD_DESCRIPTIONS)
        self.set_prop("dead", True)
        new_node_id = self.node_id + "__dead__"
        new_node = GraphObject(new_node_id, self.name, self.__dict__)
        room = self.get_room()
        new_node.set_prop("dead", True)
        new_node.set_prop("container", True)
        new_node.add_class("container")
        new_node.add_class("object")
        for item in self.get_contents():
            item.force_move_to(new_node)
        new_node.move_to(room)
        return new_node_id, new_node


class GraphObject(GraphNode):
    """Represents objects in the graph. Has all required attributes."""

    DEFAULT_SIZE = 1
    DEFAULT_CONTAIN_SIZE = 0
    DEFAULT_CONTAINER_SIZE = 20

    NODE_TYPE = "GraphObject"

    def __init__(self, node_id, name, props=None, db_id=None):
        super().__init__(node_id, name, props, db_id)
        self.object = True
        self.size = self._props.get("size", self.DEFAULT_SIZE)
        self.food_energy = self._props.get("food_energy", 1)
        self.value = self._props.get("value", 1)
        self.drink = self._props.get("drink", self._props.get("is_drink", False))
        self.food = self._props.get("food", self._props.get("is_food", False))
        self.dead = self._props.get("dead", False)
        self.on_use = self._props.get("on_use", None)
        self.container = self._props.get("container", False)
        if self._props.get("is_container", False) or self._props.get("is_surface", False):
            self.container = True
        self.surface_type = self._props.get("surface_type", "on")
        if 'is_surface' in self._props:
            if self._props.get("is_surface") == 1.0:
                self.surface_type = 'on'
            else:
                self.surface_type = 'in'
        self.gettable = self._props.get("gettable", self._props.get("is_gettable", True))
        self.wearable = self._props.get("wearable", self._props.get("is_wearable", False))
        self.wieldable = self._props.get("wieldable", self._props.get("is_weapon", False))
        self.classes = set(self._props.get("classes", {"object"}))
        self.equipped = self._props.get("equipped", None)


        self.contain_size = self._props.get(
            "contain_size",
            self.DEFAULT_CONTAINER_SIZE
            if self.container
            else self.DEFAULT_CONTAIN_SIZE,
        )
        if self.contain_size > self.size:
            self.size = self.contain_size
        # TODO object stat multipliers should not be a simple dict
        self.stats = self._props.get(
            "stats", {"damage": int(self.wieldable), "defense": int(self.wearable)}
        )
        self.locked_edge = None

    def add_locked_edge(self, locked_with: "GraphObject", start_locked=True):
        """Add an edge to note that this container is locked by the given object"""
        assert self.container, "Only containers can be locked!"
        self.locked_edge = LockEdge(locked_with, start_locked, None)
