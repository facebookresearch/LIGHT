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
    graph_dir = os.join(os.path.abspath(os.path.dirname(event_file), '../../light_graph_dumps')
    graph_buffer = []
    event_buffer = []
    self.assertNotEqual(os.stat(event_file).st_size, 0)
    with open(event_file, 'r') as event_json_file:
        parity = 0
        for line in event_json_file:
            if parity == 0:
                line = line.strip()
                self.assertEqual(room_logger._last_graph, line)
            elif parity == 1:
                # Timestamp
            else
                written_event = json.loads(line)
            parity += 1
            parity %= 3

def main():
    parser = argparse.ArgumentParser(description='Args for the event to reconstruct')
    parser.add_argument('--event-log', type=str,
                        help='The event log to reconstruct')
    FLAGS, _unknown = parser.parse_known_args()

    load_event_log(FLAGS.event_file,)

if __name__ == '__main__':
    main()