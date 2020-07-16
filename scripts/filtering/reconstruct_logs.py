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

def load_event_log(event_file):
    '''
    Given a log file, this method reconstructs the graph jsons and event jsons associated with said log.
    To replay, all that is required is using event execute methods
    '''
    graph_dir = os.
    graph_buffer = []
    event_buffer = []
    self.assertNotEqual(os.stat(event_file).st_size, 0)
    with open(event_file, 'r') as event_json_file:
        parity = 0
        for line in event_json_file:
            if parity == 0:
                line = line.strip()
                self.assertEqual(room_logger._last_graph, line)
            if parity == 2:
                written_event = json.loads(line)
                ref_json = json.loads(event_room_node_observed)
                self.assertEqual(ref_json, written_event)
            parity += 1
            parity %= 3

def main():
    parser = argparse.ArgumentParser(description='Choose the event to reconstruct')
    parser.add_argument('--event-file', type=str,
                        help='Cookie secret for issueing cookies (SECRET!!!)')
    FLAGS, _unknown = parser.parse_known_args()

    load_event_log(FLAGS.event_file)

if __name__ == '__main__':
    main()