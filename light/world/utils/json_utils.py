#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
from light.graph.elements.graph_nodes import (
    GraphAgent,
    GraphEdge,
    GraphNode,
    GraphObject,
    GraphRoom,
)
from typing import Any, Dict, Union, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from light.world.world import World


class GraphEncoder(json.JSONEncoder):
    def default(self, o):
        from light.graph.events.base import GraphEvent

        if isinstance(o, set):
            return sorted(list(o))
        if isinstance(o, list):
            return sorted(o)
        if isinstance(o, GraphEdge):
            return {k: v for k, v in o.__dict__.copy().items() if not k.startswith("_")}
        if isinstance(o, GraphEvent):
            return o.to_json()
        if not isinstance(o, GraphNode):
            return super().default(o)
        use_dict = {k: v for k, v in o.__dict__.copy().items() if not k.startswith("_")}
        return use_dict


def create_agent_tree(node: GraphAgent) -> Dict[str, GraphNode]:
    unvisited_nodes: List[GraphNode] = [node]
    agent_nodes: Dict[str, GraphNode] = {}
    while len(unvisited_nodes) > 0:
        new_node = unvisited_nodes.pop()
        agent_nodes[new_node.node_id] = new_node
        for v in new_node.contained_nodes.values():
            if v._target_node.node_id not in agent_nodes:
                unvisited_nodes.append(v._target_node)

    return agent_nodes


def node_to_json(node: GraphNode) -> str:
    return json.dumps(node, cls=GraphEncoder, sort_keys=True, indent=4)


def convert_dict_to_node(
    obj: Union[List[Any], Dict[str, Any]],
    world: "World",
) -> Union[Dict[str, Any], List[Any], "GraphNode"]:
    """
    Given a dictionary (typically loaded from json), iterate over the elements
    recursively, reconstructing any nodes that we are able to using the reference
    world.

    If the node_id is not in the reference world, this means it was deleted during
    execution, so construct a new node object with it
    """
    if type(obj) is dict and "node_id" in obj:
        if obj["node_id"] in world.oo_graph.all_nodes:
            return world.oo_graph.all_nodes[obj["node_id"]]
        else:
            if obj["agent"]:
                agent = GraphAgent.from_json_dict(obj)
                if obj["container_node"]["target_id"] in world.oo_graph.rooms:
                    agent.force_move_to(
                        world.oo_graph.rooms[obj["container_node"]["target_id"]]
                    )
                return agent
            elif obj["object"]:
                return GraphObject.from_json_dict(obj)
            elif obj["room"]:
                return GraphRoom.from_json_dict(obj)
            else:
                return GraphNode.from_json_dict(obj)
    elif type(obj) is dict:
        return {k: convert_dict_to_node(obj[k], world) for k in obj.keys()}
    elif type(obj) is list:
        return [convert_dict_to_node(item, world) for item in obj]
    else:
        # TODO: Consider other datatypes such as set or tuples (although none in events
        # rn, so not an issue)
        return obj


def read_event_logs(event_file: str) -> List[Tuple[str, str, float, str]]:
    """
    Parses an event file, returning the read file in a buffer
    """
    buffer = []
    world_hash = [None, "None"]
    timestamp = -1.0
    with open(event_file, "r") as event_json_file:
        parity = 0
        for line in event_json_file:
            if parity == 0:
                world_hash = line.split(" ")
            if parity == 1:
                timestamp = line
            elif parity == 2:
                buffer.append((world_hash[0], world_hash[1].strip(), timestamp, line))
            parity += 1
            parity %= 3
    return buffer
