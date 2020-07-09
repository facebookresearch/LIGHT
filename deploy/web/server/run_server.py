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
    TornadoWebappPlayerProvider, LandingApplication,
)
from deploy.web.server.builder_server import (
    BuildApplication, get_handlers,
)
from tornado.routing import (
    PathMatches, Rule, RuleRouter,
)
from tornado.web import (
    Application,
)
from tornado.httpserver import (
    HTTPServer,
)
from tornado.ioloop import (
    IOLoop,
)

import os.path
import threading

here = os.path.abspath(os.path.dirname(__file__))

def make_app(FLAGS, tornado_provider):
    worldBuilderApp = BuildApplication(get_handlers(FLAGS.data_model_db))
    landingApp = LandingApplication(FLAGS.data_model_db, FLAGS.hostname, FLAGS.password)
    router = RuleRouter([
        Rule(PathMatches("/builder.*"), worldBuilderApp),
        Rule(PathMatches("/game.*"), tornado_provider.app),
        Rule(PathMatches("/.*"), landingApp),
    ])
    server = HTTPServer(router)
    server.listen(FLAGS.port)

def _run_server(FLAGS, tornado_provider):
    my_loop = IOLoop()
    make_app(FLAGS, tornado_provider)
    if "HOSTNAME" in os.environ and hostname == FLAGS.hostname:
        hostname = os.environ["HOSTNAME"]
    else:
        hostname = FLAGS.hostname
    print("\nYou can connect to the game at http://%s:%s/" % (FLAGS.hostname, FLAGS.port))
    print("You can connect to the worldbuilder at http://%s:%s/builder/" % (FLAGS.hostname, FLAGS.port))
    my_loop.current().start()


def router_run(FLAGS, tornado_provider):
    '''
    Router run spins up the router for request to send to the correct application.
    
    In doing so, we have a tornado application that blocks listening for request.  Since this executes in the
    same thread as the game instance, we have to do something to avoid blocking the game instance from running.
    
    Our options are spinning a seperate thread, or using the PeriodicCallback function in tornado to switch
    between the router and the game instance.  Here we have chosen to use threading for precedence, as this
    is how the TornadoWebAppProvider runs, and for the simplicity of the implementation, however
    PeriodicCallback is a more deterministic way to handle to control switching as opposed
    to this method, which relies on the the python scheduler.  
    '''
    t = threading.Thread(
        target=_run_server, args=(FLAGS, tornado_provider), name='RoutingServer', daemon=True
    )
    t.start()


def main():
    import argparse
    import numpy
    import random

    DEFAULT_PORT = 35496
    DEFAULT_HOSTNAME = "localhost"

    parser = argparse.ArgumentParser(description='Start the game server.', fromfile_prefix_chars='@')
    parser.add_argument('--cookie-secret', type=str,
                        default="0123456789",
                        help='Cookie secret for issueing cookies (SECRET!!!)')
    parser.add_argument('--data-model-db', type=str,
                        default=here + "/../../../light/data_model/database.db",
                        help='Databse path for the datamodel')
    parser.add_argument('--hostname', metavar='hostname', type=str,
                        default=DEFAULT_HOSTNAME,
                        help='host to run the server on.')
    parser.add_argument('--light-model-root', type=str,
                        default="/checkpoint/light/models/",
                        help='models path. For local setup, use: /checkpoint/jase/projects/light/dialog/')
    parser.add_argument('--password', type=str,
                        default="LetsPlay",
                        help='password for users to access the game.')
    parser.add_argument('--port', metavar='port', type=int,
                        default=DEFAULT_PORT,
                        help='port to run the server on.')
    FLAGS, _unknown = parser.parse_known_args()

    random.seed(6)
    numpy.random.seed(6)

    # Need to package this stuff into a new method for spawning game, so wrap it up!
    # Just one tornado listener that passes people along to correct graph?
    # Look at the tornado_server for handling this mostly - can just add the graphs to tornadoWebbapp
    game = GameInstance()
    graph = game.g
    tornado_provider = TornadoWebappPlayerProvider(graph, FLAGS.hostname, FLAGS.port)
    game.register_provider(tornado_provider)
    provider = TelnetPlayerProvider(graph, FLAGS.hostname, FLAGS.port + 1)
    game.register_provider(provider)
    router_run(FLAGS, tornado_provider)
    game.run_graph()



if __name__ == "__main__":
    main()
