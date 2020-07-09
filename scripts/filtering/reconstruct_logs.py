#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

'''
This file contains a script for reconstructing a meta episode from
the point of view (and logs) of either an agent or a room.  
'''

# General flow: take given events file, go through, rebuilding the buffers
# as appropriate. Should be super simple!

def load_event(log_id):
    '''
    Given a log id, this method reconstructs the graph jsons and event jsons associated with said log.
    To replay, all that is required is using the .from_json methods of the OOGraph and GraphEvent to
    rebuild whatever events you want!
    '''
    event_file = os.path.join("/private/home/lucaskabela/LIGHT/logs/light_event_dumps/room",f'{log_id}_events.json')
    buffer = []
    self.assertNotEqual(os.stat(event_file).st_size, 0)
    with open(event_file, 'r') as event_json_file:
        parity = True
        for line in event_json_file:
            if parity:
                time_stamp = line
            else:
                written_event = line
                buffer.append(written_event)
            parity = not parity

if __name__ == '__main__':
    load_event(0)
