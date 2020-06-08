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
    TornadoWebappPlayerProvider, StaticUIHandler,
)
from deploy.web.server.builder_server import (
    get_handlers,
)
from tornado.routing import (
    PathMatches, Rule, RuleRouter,
)
from tornado.web import (
    Application, StaticFileHandler,
)
from tornado.httpserver import (
    HTTPServer,
)
from tornado.ioloop import (
    IOLoop,
)

import os.path
import threading
import time

DEFAULT_PORT = 35496
DEFAULT_HOSTNAME = "localhost"


here = os.path.abspath(os.path.dirname(__file__))

def make_app(FLAGS, tornado_provider):
    worldBuilderApp = Application(get_handlers(FLAGS.data_model_db))
    staticApp = Application([(r"/(.*)", StaticUIHandler, {'path' : here + "/../build/"})])
    # provider.app gives application
    router = RuleRouter([
        Rule(PathMatches("/builder/.*"), worldBuilderApp),
        Rule(PathMatches("/game/(.*)"), tornado_provider.app),
        Rule(PathMatches("/(.*)"), staticApp),
    ])
    server = HTTPServer(router)
    server.listen(DEFAULT_PORT)

def _run_server(FLAGS, tornado_provider):
    my_loop = IOLoop()
    make_app(FLAGS, tornado_provider)
    # self.app.listen(port, max_buffer_size=1024 ** 3)
    if "HOSTNAME" in os.environ and hostname == DEFAULT_HOSTNAME:
        hostname = os.environ["HOSTNAME"]
    else:
        hostname = FLAGS.hostname
    print("\nYou can connect to the game at http://%s:%s/" % (FLAGS.hostname, FLAGS.port))
    print("You can connect to the worldbuilder at http://%s:%s/builder/" % (FLAGS.hostname, FLAGS.port))
    print("or you can connect to http://%s:%s/game/socket \n" % (FLAGS.hostname, FLAGS.port))
    my_loop.current().start()

# Threading used here for simplicity, but PeriodicCallback is a more deterministic way to handle 
# switching  vs the python scheduler.
def router_run(FLAGS, tornado_provider):
    t = threading.Thread(
        target=_run_server, args=(FLAGS, tornado_provider), name='RoutingServer', daemon=True
    )
    t.start()


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
    parser.add_argument('--data_model_db', type=str,
                        default=here + "/../../../light/data_model/database.db",
                        help='Databse path for the datamodel')
    FLAGS, _unknown = parser.parse_known_args()

    random.seed(6)
    numpy.random.seed(6)


    game = GameInstance()
    graph = game.g
    tornado_provider = TornadoWebappPlayerProvider(graph, FLAGS.hostname, FLAGS.port)
    game.register_provider(tornado_provider)
    router_run(FLAGS, tornado_provider)
    provider = TelnetPlayerProvider(graph, FLAGS.hostname, FLAGS.port + 1)
    game.register_provider(provider)
    game.run_graph()



if __name__ == "__main__":
    main()
