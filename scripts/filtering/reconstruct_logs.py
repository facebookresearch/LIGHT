#!/usr/bin/env python3


# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from light.graph.events.base import GraphEvent
from light.graph.structured_graph import OOGraph
from light.world.utils.json_utils import read_event_logs
from light.world.world import World, WorldConfig

import argparse
import os

"""
This file contains a script for reconstructing a meta episode from
the point of view (and logs) of either an agent or a room.
"""


def load_event_log(event_file):
    """
    Given a log file, this method reconstructs the graph jsons and event jsons
    associated with said log. To replay, all that is required is using event
    execute methods
    """
    graph_dir = os.path.join(
        os.path.abspath(os.path.dirname(event_file)), "../../light_graph_dumps"
    )
    uuid_to_world = {}
    events = []
    event_buffer = read_event_logs(event_file)
    for (world_uuid, hash_, timestamp, event_json) in event_buffer:
        if world_uuid not in uuid_to_world:
            world = get_world(world_uuid, graph_dir)
            uuid_to_world[world_uuid] = world
        else:
            world = uuid_to_world[world_uuid]

        event_obj = GraphEvent.from_json(event_json, world)
        events.append((world_uuid, hash_, timestamp, event_obj))

    # Return the worlds and the event buffer which is in order of the events
    # NOTE: In future, if async writes, can define a sort on the timestamp
    return (uuid_to_world, events)


def get_world(uuid, graph_dir):
    """
    Given a directory containing graph dumps and a graph uuid, reconstruct a world
    from the serialized graph
    """
    graph_file = os.path.join(graph_dir, f"{uuid}.json")
    with open(graph_file, "r") as graph_json_file:
        graph = OOGraph.from_json(graph_json_file.read())
    world = World(WorldConfig(), False)
    world.oo_graph = graph
    return world


def main():
    parser = argparse.ArgumentParser(description="Args for the event to reconstruct")
    parser.add_argument("--event-log", type=str, help="The event log to reconstruct")
    FLAGS, _unknown = parser.parse_known_args()
    uuid_to_world, event_buffer = load_event_log(
        FLAGS.event_log,
    )
    # TODO:  Process these in future - for now just display
    print(uuid_to_world)
    print(event_buffer)


if __name__ == "__main__":
    main()
