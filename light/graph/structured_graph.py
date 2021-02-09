#!/usr/bin/env python3
import json
import os
import copy
from light.graph.elements.graph_nodes import (
    GraphObject,
    GraphAgent,
    GraphRoom,
    GraphNode,
    GraphVoidNode,
    GraphEdge,
)
from light.world.utils.json_utils import GraphEncoder
from light.world.content_loggers import RoomInteractionLogger


class OOGraph(object):
    """Graph class that takes normal graph and formats it in an easily
    inspectible version from an Object-Oriented point of view
    """

    def __init__(self, opt=None):
        self.objects = {}
        self.agents = {}
        self.rooms = {}
        self.room_id_to_loggers = {}
        self.all_nodes = {}
        self.void = GraphVoidNode()
        self.cnt = 0
        self._nodes_to_delete = []
        self._deleted_nodes = {}
        self.dead_nodes = {}
        self._opt = opt

    @staticmethod
    def from_graph(graph, start_location=None):
        oo_graph = OOGraph(graph._opt)
        oo_graph._graph = graph
        object_ids = set(graph.get_all_by_prop("object"))
        room_ids = set(graph.get_all_by_prop("room"))
        agent_ids = set(graph.get_all_by_prop("agent"))
        if start_location is None:
            all_node_ids = graph.all_node_ids()
        else:
            # Iteratively build the list of all sub-items of the given item
            all_node_ids = set()
            to_add = {start_location}
            while len(to_add) > 0:
                curr_elem = to_add.pop()
                all_node_ids.add(curr_elem)
                to_add = to_add.union(graph.node_contains(curr_elem))
            object_ids = object_ids.intersection(all_node_ids)
            room_ids = room_ids.intersection(all_node_ids)
            agent_ids = agent_ids.intersection(all_node_ids)

        oo_graph.objects = {x: GraphObject.from_graph(graph, x) for x in object_ids}
        oo_graph.agents = {x: GraphAgent.from_graph(graph, x) for x in agent_ids}
        oo_graph.rooms = {x: GraphRoom.from_graph(graph, x) for x in room_ids}
        oo_graph.all_nodes = {}
        oo_graph.all_nodes.update(oo_graph.objects)
        oo_graph.all_nodes.update(oo_graph.agents)
        oo_graph.all_nodes.update(oo_graph.rooms)
        for node in oo_graph.all_nodes.values():
            node.sync(oo_graph.all_nodes)

        # settle edges over the whole graph
        for obj in oo_graph.objects.values():
            target_id = graph._node_contained_in[obj.node_id]
            obj.force_move_to(oo_graph.all_nodes[target_id])

        for char in oo_graph.agents.values():
            target_id = graph._node_contained_in[char.node_id]
            char.force_move_to(oo_graph.all_nodes[target_id])
            if char.node_id in graph._node_follows:
                char.follow(oo_graph.all_nodes[graph._node_follows[char.node_id]])

        for room in oo_graph.rooms.values():
            room_id = room.node_id
            for ((edge_type, neighbor_id), edge) in graph._node_to_edges[
                room.node_id
            ].items():
                if edge_type != "path_to":
                    continue
                locked_node = None
                if edge["locked_with"] is not None:
                    locked_node = oo_graph.all_nodes[edge["locked_with"]]
                room.add_neighbor(
                    oo_graph.rooms[neighbor_id],
                    edge["label"],
                    locked_node,
                    edge["examine_desc"],
                    edge["full_label"],
                )
                # TODO parse other edge locked parameters
            room.move_to(oo_graph.void)
            oo_graph.room_id_to_loggers[room_id] = RoomInteractionLogger(
                oo_graph, room_id
            )

        if hasattr(graph, "void_id"):
            oo_graph.delete_nodes([oo_graph.get_node(graph.void_id)])
        return oo_graph

    # consistency and graph validation

    def _assert_all_are_nodes(self):
        """Ensure every node tracked in this graph is a graph node"""
        for node in self.get_all_nodes():
            assert isinstance(node, GraphNode), f"Node {node} not a GraphNode"

    def _assert_correct_contains(self):
        """Ensure every tracked node has a container and is contained by it"""
        for node in self.get_all_nodes():
            assert (
                node.get_container() is not None
            ), f"Node {node} has None as container"
            container = node.get_container()
            assert (
                node in container.get_contents()
            ), f"Node {node} has not in container {container} contents {container.get_contents()}"

    def _assert_correct_containing_rooms(self):
        """Ensure every tracked node is a member of a room"""
        for node in self.get_all_nodes():
            assert node.get_room() is not False, f"Node {node} get_room is False"

    def _assert_all_nodes_properly_tracked_dict(self):
        """Ensure all_nodes is correctly tracking the other dicts"""
        for check_list in [self.agents, self.objects, self.rooms]:
            for id in check_list:
                assert (
                    id in self.all_nodes
                ), f"Node id {id} in type dict but not is all_nodes"
        assert len(self.agents) + len(self.objects) + len(self.rooms) == len(
            self.all_nodes
        ), "all_nodes has node not in the checked dicts"

    def _assert_no_deleted_nodes_remains(self):
        """Ensure any node that has been deleted doesn't exist in the graph"""
        for node_id in self._deleted_nodes:
            assert (
                node_id not in self.all_nodes
            ), f"deleted node {node_id} still in all_nodes"

    def _assert_all_nodes_valid(self):
        """Ensure every node tracked in this graph is valid"""
        for node in self.get_all_nodes():
            node.assert_valid()

    def assert_valid(self):
        """Run through a series of checks to ensure that the contents of the
        graph are considered to be valid, as in there are no broken invariants
        that could potentially cause operations on this graph that assume
        those invariants to break. These invariants should be separate functions
        """
        self._assert_all_are_nodes()
        self._assert_all_nodes_valid()
        self._assert_correct_containing_rooms()
        self._assert_correct_contains()
        self._assert_all_nodes_properly_tracked_dict()
        self._assert_no_deleted_nodes_remains()

    # Graph node creators

    def _create_node_of_type(
        self, name, props, node_type, is_player=False, uid="", db_id=None
    ):
        """Create a new node of the given type and return it. Handles parsing
        the props object to the correct form"""
        id = name.lower()
        if not is_player:
            id = "{}_{}".format(id, self.cnt)
            if uid != "":
                id += "_{}".format(uid)
        self.cnt = self.cnt + 1
        if type(props) == str:
            # TODO deprecate props as a string
            props_dict = {props: True, "is_player": is_player}
            node = node_type(id, name, props_dict, db_id)
            node.add_class(props)
        elif type(props) == dict:
            props["is_player"] = is_player
            node = node_type(id, name, props, db_id)
        else:
            # TODO deprecate props as a list of classes
            props_dict = {prop_name: True for prop_name in props}
            props_dict["is_player"] = is_player
            node = node_type(id, name, props_dict, db_id)
            for p in props:
                node.add_class(p)
        return node, node.node_id

    def add_agent(self, name, props, is_player=False, uid="", db_id=None):
        """Add an agent node to the graph"""
        if uid != "":
            assert uid not in self.all_nodes, "Already a node with this id in graph"
        node, id = self._create_node_of_type(
            name, props, GraphAgent, is_player, uid, db_id
        )
        node.force_move_to(self.void)
        self.agents[id] = node
        self.all_nodes[id] = node
        return node

    def add_room(self, name, props, uid="", db_id=None):
        """Add a room node to the graph"""
        if uid != "":
            assert uid not in self.all_nodes, "Already a node with this id in graph"
        node, id = self._create_node_of_type(name, props, GraphRoom, False, uid, db_id)
        node.force_move_to(self.void)
        self.rooms[id] = node
        self.all_nodes[id] = node

        self.room_id_to_loggers[id] = RoomInteractionLogger(self, id)

        return node

    def add_object(self, name, props, uid="", db_id=None):
        """Add an object node to the graph"""
        if uid != "":
            assert uid not in self.all_nodes, "Already a node with this id in graph"
        node, id = self._create_node_of_type(
            name, props, GraphObject, False, uid, db_id
        )
        node.force_move_to(self.void)
        self.objects[id] = node
        self.all_nodes[id] = node
        return node

    def add_node(self, name, props, is_player=False, uid="", is_room=False):
        """Method for adding generic nodes for backwards compatibility"""
        # TODO deprecate
        if is_room:
            return self.add_room(name, props, uid).node_id
        elif "classes" in props:
            classes = props["classes"]
            if "room" in classes:
                return self.add_room(name, props, uid).node_id
            elif "object" in classes:
                return self.add_object(name, props, uid).node_id
            elif "agent" in classes:
                return self.add_agent(name, props, is_player, uid).node_id
        print("Could not find node type! defaulting object")
        return self.add_object(name, props, uid).node_id

    def add_paths_between(
        self,
        node1,
        node2,
        desc1=None,
        desc2=None,
        locked_with=None,
        examine1=None,
        examine2=None,
    ):
        """Create a path between two rooms"""
        assert node1 != node2, "cannot create path from room to itself"
        node1.add_neighbor(node2, desc1, locked_with, examine1)
        node2.add_neighbor(node1, desc2, locked_with, examine2)

    def mark_node_for_deletion(self, id):
        """Mark a node to be removed from the graph on next deletion"""
        assert id in self.all_nodes, "Cannot prepare to delete non-existent node"
        self._nodes_to_delete.append(id)

    def delete_nodes(self, nodes_to_delete=None):
        """Trigger deletion of all nodes in the given list. If no list provided,
        default to deleting the entire deletion queue
        """
        if nodes_to_delete is None:
            nodes_to_delete = [self.get_node(i) for i in self._nodes_to_delete]
            self._nodes_to_delete = []
        cleared_nodes = []
        for node in nodes_to_delete:
            cleared_nodes += node.delete_and_cleanup()
        for node in cleared_nodes:
            self.mark_deleted(node)

    def mark_deleted(self, node):
        """Remove all references for a node from the graph from the main dicts"""
        i = node.node_id
        if self.all_nodes[i] == node:
            del self.all_nodes[i]
        for check_dict in [self.agents, self.objects, self.rooms, self.dead_nodes]:
            if i in check_dict:
                if check_dict[i] == node:
                    del check_dict[i]
        self._deleted_nodes[node.node_id] = node

    # Graph setters and getters and simple accessors

    def get_node(self, id):
        return self.all_nodes.get(id)

    def node_exists(self, id):
        return id in self.all_nodes

    def get_edge(self, from_id, to_id):
        """Return the edge between two nodes by id if it exists, None otherwise"""
        room = self.get_node(from_id)
        dest = self.get_node(to_id)
        return room.get_edge_to(dest)

    def get_all_ids(self):
        return list(self.all_nodes.keys())

    def get_all_nodes(self):
        return list(self.all_nodes.values())

    def get_npcs(self):
        """Get a list of agent nodes that aren't currently being played by
        a human character"""
        return [
            x
            for x in self.agents.values()
            if x._human is False and not x.is_player and not x.get_prop("dead")
        ]

    def set_desc(self, id, desc):
        """Update the name for a node"""
        # TODO deprecate all calls to this
        self.set_name(id, desc)

    def set_name(self, id, name):
        """Update the name for a node"""
        node = self.get_node(id)
        node.name = name

    def get_dead_nodes(self):
        """get a list of nodes that are objects representing dead agents"""
        return [x for x in self.dead_nodes.values()]

    # Derived graph logic

    def get_local_nodes(self, actor_id):
        """Get nodes local to the given actor_id"""
        actor = self.get_node(actor_id)
        room = actor.get_room()
        o1 = set(actor.get_contents())
        o2 = set(room.get_contents())
        o3 = set(room.get_neighbors())
        o4 = [room]
        return o1.union(o2).union(o3).union(o4)

    def get_local_ids(self, actor_id):
        """Return all accessible ids for an actor"""
        local_nodes = self.get_local_nodes(actor_id)
        return [x.node_id for x in local_nodes]

    def find_nodes_by_name(self, node_name):
        """
        Return all nodes that exact match the given node name,
        if any exist.
        """
        return [n for n in self.get_all_nodes() if n.name == node_name]

    def desc_to_nodes(self, desc, nearby_node=None, nearbytype=None):
        """Get nodes nearby to a given node from that node's perspective"""
        # TODO the logic of finding the nearby node searchlist and the
        # actual search should probably separated into separate functions
        if desc.strip() == "":
            return []

        from_node = None
        if nearby_node is not None:
            from_node = nearby_node.get_container()
        if nearby_node is not None:
            o = set()
            if "all" in nearbytype and "here" in nearbytype:
                o = self.get_local_nodes(nearby_node.node_id)
            else:
                if "path" in nearbytype:
                    # TODO this logic is somewhat unclear. All other searches
                    # are definitely from the given node, while this is paths
                    # from the parent node (which needs to be a room)
                    assert isinstance(
                        from_node, GraphRoom
                    ), f"Must be an agent in a room to use path in desc_to_nodes, was {from_node}"
                    o1 = set(from_node.get_neighbors())
                    o = set(o).union(o1).union([from_node])
                if "carrying" in nearbytype:
                    o = set(o).union(set(nearby_node.get_contents()))
                if "sameloc" in nearbytype:
                    o1 = set(from_node.get_contents())
                    o = o.union(o1)
                if "all" in nearbytype:
                    o1 = set(nearby_node.get_contents())
                    o2 = set(from_node.get_contents())
                    o3 = set(from_node.get_neighbors())
                    o = o.union(o1).union(o2).union(o3)
                if "contains" in nearbytype:
                    o = o.union({from_node})
                if "others" in nearbytype:
                    for item in o:
                        if item.room or (item.object and item.container):
                            o = o.union(item.get_contents())
        else:
            o = set(self.get_all_nodes())

        if nearby_node is not None and nearby_node in o:
            o.remove(nearby_node)

        query = desc.lower()
        # Go through official in-game special case aliases for real nodes
        if nearby_node is not None and nearby_node.get_room() in o and desc == "room":
            return [nearby_node.get_room()]

        # get the nodes in the set that match the given desc
        valid_nodes_1 = [
            (node, node.get_view_from(from_node))
            for node in o
            if query in node.get_view_from(from_node).lower() + "s"
        ]

        # Check the parent name trees for names that also could match in the
        # case that nothing could be found
        node_names = [(node, node.get_names()) for node in o]
        all_pairs = [
            (node, name) for (node, name_list) in node_names for name in name_list
        ]
        valid_nodes_2 = [
            (node, name) for (node, name) in all_pairs if query in name + "s"
        ]

        valid_nodes_1.sort(key=lambda x: len(x[1]))
        valid_nodes_2.sort(key=lambda x: len(x[1]))

        # Extract the nodes, then join lists
        valid_nodes_1 = [node for (node, _name) in valid_nodes_1]
        valid_nodes_2 = [
            node for (node, _name) in valid_nodes_2 if node not in valid_nodes_1
        ]
        valid_nodes = valid_nodes_1 + valid_nodes_2
        return valid_nodes

    # TODO remove
    def agent_die(self, node):
        """Kill an agent, turn them into an object"""
        assert isinstance(node, GraphAgent), "Can only kill agents"
        new_node_id, new_node_object = node.die()
        self.all_nodes[new_node_id] = new_node_object
        self.objects[new_node_id] = new_node_object
        self.dead_nodes[new_node_id] = new_node_object
        self.delete_nodes([node])
        return new_node_object

    def to_json(self):
        dicts = {
            "objects": sorted(list(self.objects.keys())),
            "agents": sorted(list(self.agents.keys())),
            "rooms": sorted(list(self.rooms.keys())),
            "nodes": self.all_nodes,
        }
        return json.dumps(dicts, cls=GraphEncoder, sort_keys=True, indent=4)

    def to_json_rv(self, room_id):
        """Export a graph with room_id, its descendants, and its direct neighbors (for logging)"""
        room_node = self.all_nodes[room_id]

        # Do not forget neighbors for Leave / Arrive events, but drop the things in them
        neighbors = room_node.get_neighbors()
        neighbors_contained_removed = set(
            [copy.deepcopy(neighbor) for neighbor in neighbors]
        )
        for neighbor in neighbors_contained_removed:
            neighbor.contained_nodes = {}
            neighbor.neighbors = {}

        # Get everything contained inside this room using BFS, then union with neighbors
        contained_nodes = OOGraph.get_contained_in_room(room_node)
        nodes = contained_nodes.union(neighbors_contained_removed)

        agents = []
        objects = []
        rooms = []
        for node in nodes:
            if node.room:
                rooms.append(node.node_id)
            elif node.agent:
                agents.append(node.node_id)
            elif node.object:
                objects.append(node.node_id)
            # If it is none of those do not worry, nodes still has it

        dicts = {
            "agents": sorted(agents),
            "nodes": {node.node_id: node for node in nodes},
            "objects": sorted(objects),
            "rooms": sorted(rooms),
        }
        return json.dumps(dicts, cls=GraphEncoder, sort_keys=True, indent=4)

    @staticmethod
    def get_contained_in_room(room_node):
        """
        Starting from room_node, use a BFS to get all descendant nodes of
        the room node in the graph (including the room node)
        """
        content_queue = room_node.get_contents()
        contained_nodes = set()
        contained_nodes.add(room_node)
        while len(content_queue) != 0:
            next_node = content_queue.pop(0)
            if next_node not in contained_nodes:
                contained_nodes.add(next_node)
                content_queue.extend(next_node.get_contents())
        return contained_nodes

    @staticmethod
    def from_json(input_json: str):
        dict_format = json.loads(input_json)
        oo_graph = OOGraph()
        object_ids = set(dict_format["objects"])
        agent_ids = set(dict_format["agents"])
        room_ids = set(dict_format["rooms"])
        node_dicts = dict_format["nodes"]

        oo_graph.objects = {
            x: GraphObject.from_json_dict(node_dicts[x]) for x in object_ids
        }
        oo_graph.agents = {
            x: GraphAgent.from_json_dict(node_dicts[x]) for x in agent_ids
        }
        oo_graph.rooms = {x: GraphRoom.from_json_dict(node_dicts[x]) for x in room_ids}
        oo_graph.all_nodes = {}
        oo_graph.all_nodes.update(oo_graph.objects)
        oo_graph.all_nodes.update(oo_graph.agents)
        oo_graph.all_nodes.update(oo_graph.rooms)

        sync_nodes = {oo_graph.void.node_id: oo_graph.void}
        sync_nodes.update(oo_graph.all_nodes)
        for node in oo_graph.all_nodes.values():
            node.sync(sync_nodes)

        # settle edges over the whole graph
        # Follows
        for char in oo_graph.agents.values():
            char_dict = node_dicts[char.node_id]
            if char_dict["following"] is not None:
                char.follow(sync_nodes[char_dict["following"]["target_id"]])

        # Neighbors/locks
        for room in oo_graph.rooms.values():
            room_id = room.node_id
            room_dict = node_dicts[room_id]
            for edge_dict in room_dict["neighbors"].values():
                target_node = sync_nodes[edge_dict["target_id"]]
                if edge_dict["locked_edge"] is not None:
                    room.add_neighbor(
                        other_node=target_node,
                        edge_label=edge_dict["label"],
                        locked_with=sync_nodes[edge_dict["locked_edge"]["target_id"]],
                        edge_desc=edge_dict["examine_desc"],
                        is_locked=edge_dict["locked_edge"]["is_locked"],
                    )
                else:
                    room.add_neighbor(
                        other_node=target_node,
                        edge_label=edge_dict["label"],
                        edge_desc=edge_dict["examine_desc"],
                    )
            room.force_move_to(oo_graph.void)
            # need to read opts back somehow?  Or just do not worry about it - not logging from json
            oo_graph.room_id_to_loggers[room_id] = RoomInteractionLogger(
                oo_graph, room_id
            )

        # Container locks
        for obj in oo_graph.objects.values():
            obj_dict = node_dicts[obj.node_id]
            lock_edge_dict = obj_dict.get("locked_edge")
            if lock_edge_dict is not None:
                obj.add_locked_edge(
                    sync_nodes[lock_edge_dict["target_id"]],
                    start_locked=lock_edge_dict["is_locked"],
                )

        return oo_graph

    @staticmethod
    def from_worldbuilder_json(input_json: str):
        f = open(input_json, "rb")
        dict_format = json.load(f)
        f.close()
        g = OOGraph()

        entities = dict_format["entities"]
        locations = dict_format["map"]

        rooms = {}
        for ind, r in entities["room"].items():
            n = g.add_room(
                r["name"],
                {"desc": r["description"], "backstory": r["backstory"]},
                uid=int(ind),
            )
            rooms[int(ind)] = n
            n.force_move_to(g.void)

        agents = {}
        for ind, props in entities["character"].items():
            n = g.add_agent(props["name"], props, uid=str(ind),)
            agents[int(ind)] = n

        objects = {}
        for ind, obj in entities["object"].items():
            n = g.add_object(obj["name"], obj, uid=str(ind))
            objects[int(ind)] = n

        grid = {}
        for grid_loc, v in locations[0]["tiles"].items():
            # TODO: not used yet: name (of map floor), walls
            rid = int(v["room"])
            grid[grid_loc] = rid
            for c in v["characters"]:
                aid = int(c)
                agents[aid].force_move_to(rooms[rid])
            for o in v["objects"]:
                oid = int(o)
                objects[oid].force_move_to(rooms[rid])

        # Make paths
        # TODO: no up, down as yet.
        directions = [
            ([-1, 0], "west"),
            ([+1, 0], "east"),
            ([0, -1], "south"),
            ([0, +1], "north"),
        ]
        for loc, rid in grid.items():
            loc1 = [int(loc.split()[0]), int(loc.split()[1])]
            for d in directions:
                grad = d[0]
                edge = d[1]
                loc2 = (loc1[0] + grad[0], loc1[1] + grad[1])
                grid2 = str(loc2[0]) + " " + str(loc2[1])
                if grid2 in grid:
                    rooms[rid].add_neighbor(
                        other_node=rooms[grid[grid2]],
                        edge_label="path to the " + edge,
                        edge_desc="You see a path!",
                    )

        return g
