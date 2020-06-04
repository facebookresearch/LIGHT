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
    import numpy
    import random


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
    game.run_graph()


if __name__ == "__main__":
    main()
