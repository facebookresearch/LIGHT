#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from light.graph.structured_graph import OOGraph
from light.graph.events.base import GraphEvent
from light.world.world import World

import argparse
import os
'''
This file contains a script for reconstructing a meta episode from
the point of view (and logs) of either an agent or a room.  
'''

def load_event_log(event_file):
    '''
    Given a log file, this method reconstructs the graph jsons and event jsons associated with said log.
    To replay, all that is required is using event execute methods
    '''
    graph_dir = os.path.join(os.path.abspath(os.path.dirname(event_file)), '../../light_graph_dumps')
    log_type = 'agent' if 'agent' in os.path.abspath(os.path.dirname(event_file) )else 'room'

    uuid_to_world = {}
    event_buffer = []
    with open(event_file, 'r') as event_json_file:
        parity = 0
        for line in event_json_file:
            if parity == 0:
                world_uuid_and_hash = line.split(" ")
                world_uuid = world_uuid_and_hash[0]
                if world_uuid not in uuid_to_world:
                    world = get_world(world_uuid, graph_dir)
                    uuid_to_world[world_uuid] = world
                else:
                    world = uuid_to_world[world_uuid]
                hash_ = world_uuid_and_hash[1].strip()
            if parity == 1:
                timestamp = line.strip()
            elif parity == 2:
                written_event = GraphEvent.from_json(line, world)
                event_buffer.append((hash_, timestamp, written_event))
            parity += 1
            parity %= 3
    # Return the worlds and the event buffer which is in order of the events 
    # NOTE: In future, if asynch writes, can define a sort on the timestamp 
    return (uuid_to_world, event_buffer)

def get_world(uuid, graph_dir):
    '''
        Given a directory containing graph dumps and a graph uuid, reconstruct a world 
        from the serialized graph
    '''
    graph_file = os.path.join(graph_dir, f'{uuid}.json')
    with open(graph_file, 'r') as graph_json_file:
        graph = OOGraph.from_json(graph_json_file.read())
    world  = World(None, None, False)
    world.oo_graph = graph
    return world

def main():
    parser = argparse.ArgumentParser(description='Args for the event to reconstruct')
    parser.add_argument('--event-log', type=str,
                        help='The event log to reconstruct')
    FLAGS, _unknown = parser.parse_known_args()
    uuid_to_world, event_buffer = load_event_log(FLAGS.event_log,)
    # TODO:  Process these in future - for now just display
    print(uuid_to_world)
    print(event_buffer)

if __name__ == '__main__':
    main()
