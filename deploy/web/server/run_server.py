#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from deploy.web.server.game_instance import (
    GameInstance,
)
from deploy.web.server.telnet_server import (
    TelnetPlayerProvider,
)
from deploy.web.server.tornado_server import (
    TornadoWebappPlayerProvider,
)

DEFAULT_PORT = 35496
DEFAULT_HOSTNAME = "localhost"

def main():
    import argparse
    import inspect
    import numpy
    import os.path
    import random
    import subprocess
    from time import sleep


    parser = argparse.ArgumentParser(description='Start the game server.')
    parser.add_argument('--light-model-root', type=str,
                        default="/checkpoint/light/models/",
                        help='models path. For local setup, use: /checkpoint/jase/projects/light/dialog/')
    parser.add_argument('-port', metavar='port', type=int,
                        default=DEFAULT_PORT,
                        help='port to run the server on.')
    parser.add_argument('--hostname', metavar='hostname', type=str,
                        default=DEFAULT_HOSTNAME,
                        help='host to run the server on.')
    FLAGS, _unknown = parser.parse_known_args()

    random.seed(6)
    numpy.random.seed(6)

    game = GameInstance()
    graph = game.g
    provider = TornadoWebappPlayerProvider(graph, FLAGS.hostname, FLAGS.port)
    game.register_provider(provider)
    provider = TelnetPlayerProvider(graph, FLAGS.hostname, FLAGS.port + 1)
    game.register_provider(provider)

    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path     = os.path.dirname(os.path.abspath(filename))
    ui_out_path = path + '/ui_out.txt'
    # TODO: Figure out how to pass configurable port
    out = open(ui_out_path, 'w')
    ui_cmd = ["npm", "start", "-s", "-q",] #"--", "--port", DEFAULT_PORT,]
    # TODO: Change to using location of this script
    ui = subprocess.Popen(ui_cmd, cwd=path + '/../webapp', stdout=out)

    print("Waiting for ui to spin up...")
    sleep(60)
    with open(ui_out_path, 'r') as f:
        txt = f.read()
        print(txt)
        txt = txt.split()
        links = [ word for word in txt if word.startswith('http://')]

    assert len(links) > 0
    print("Play the game at any of {}".format(str(links)))    
    game.run_graph()

    ui.wait(timeout=1000)

if __name__ == "__main__":
    main()
