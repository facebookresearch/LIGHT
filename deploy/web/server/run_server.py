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

DEFAULT_PORT = 35496
DEFAULT_HOSTNAME = "localhost"


here = os.path.abspath(os.path.dirname(__file__))

class StaticUIHandler(StaticFileHandler):
    def parse_url_path(self, url_path):
        path_to_build = here + "/../builderapp/build/" + url_path
        path_to_game = here + "/../webapp/build/" + url_path
        build_exists = os.path.exists(path_to_build)
        game_exists = os.path.exists(path_to_game)
        if (game_exists):
            url_path = path_to_game
        elif (build_exists):
            url_path = path_to_build

        if not url_path or url_path.endswith('/'):
            url_path =  url_path + 'index.html'
        print(url_path)

        return url_path
        
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
    provider = TornadoWebappPlayerProvider(graph, FLAGS.hostname, FLAGS.port)
    worldBuilderApp = Application(get_handlers(FLAGS.data_model_db))
    staticApp = Application([(r"/(.*)", StaticUIHandler, {'path' : ""})])

    # provider.app gives application
    router = RuleRouter([
        Rule(PathMatches("/builder/.*"), worldBuilderApp),
        Rule(PathMatches("/game/(.*)"), provider.app),
        Rule(PathMatches("/(.*)"), staticApp),
    ])
    server = HTTPServer(router)
    server.listen(DEFAULT_PORT)
    IOLoop.current().start()

    game.register_provider(provider)
    provider = TelnetPlayerProvider(graph, FLAGS.hostname, FLAGS.port + 1)
    game.register_provider(provider)
    game.run_graph()


if __name__ == "__main__":
    main()
