#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import json

def read_event_logs(event_file):
    '''
        Parses an event file, returning the read file in a buffer
    '''
    buffer = []
    with open(event_file, 'r') as event_json_file:
        parity = 0
        for line in event_json_file:
            if parity == 0:
                world_hash = line.split(" ")
            if parity == 1:
                timestamp = line
            elif parity == 2:
                written_event = json.loads(line)
                buffer.append((world_hash[0], world_hash[1].strip(), timestamp, written_event))
            parity += 1
            parity %= 3
    return buffer
