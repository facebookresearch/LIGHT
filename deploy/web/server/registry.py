#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
import sys
import ast
import inspect
import threading
import time
import uuid
import tornado.web
from tornado.ioloop import IOLoop
from tornado import locks
from tornado import gen
from tornado.routing import (
    PathMatches, Rule, RuleRouter,
)
from deploy.web.server.game_instance import (
    GameInstance,
)
from deploy.web.server.tornado_server import (
    TornadoWebappPlayerProvider,
)
from deploy.web.server.telnet_server import (
    TelnetPlayerProvider,
)


def get_rand_id():
    return str(uuid.uuid4())

tornado_settings = {
    "autoescape": None,
    "cookie_secret": "0123456789", #TODO: Placeholder, do not include in repo when deploy!!!
    "compiled_template_cache": False,
    "debug": "/dbg/" in __file__,
    "login_url": "/login",
}

class RegistryApplication(tornado.web.Application):
    '''
    This application simply takes the user game request and will
        - Forward it to the designated tornado provider (if an id is given)
        - Assign to a random (or default) game based on some load balancing
    '''
    def __init__(self, FLAGS):
        self.game_instances = {}
        self.FLAGS = FLAGS
        super(RegistryApplication, self).__init__(self.get_handlers(FLAGS), **tornado_settings)

    def get_handlers(self, FLAGS):
        self.tornado_provider = TornadoWebappPlayerProvider({}, FLAGS.hostname, FLAGS.port)
        self.router = RuleRouter([Rule(PathMatches(f'/game.*/socket'), self.tornado_provider.app)])
        game_instance = self.run_new_game("", FLAGS)
        return [
            (r"/game/new/(.*)", GameCreatorHandler, {'app': self}),
            (r"/game(.*)", self.router)
        ]

    # TODO: Move this to utils
    # This is basically it though - want to create a new world?  For now call these methods, then
    # attach the game's tornado provider 
    def run_new_game(self, game_id, FLAGS):

        game = GameInstance(game_id)
        graph = game.g
        self.tornado_provider.graphs[game_id] = graph
        self.game_instances[game_id] = game

        game.register_provider(self.tornado_provider)
        # TODO: Decide if threading is the right approach or not
        t = threading.Thread(
            target=game.run_graph, name=f'Game{game_id}GraphThread', daemon=True
        )
        t.start()

        return game

# Default BaseHandler - should be extracted to some util?
class BaseHandler(tornado.web.RequestHandler):
    def options(self, *args, **kwargs):
        pass

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if user_json:
            return tornado.escape.json_decode(user_json)
        else:
            return None

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Acces-Control-Allow-Credentials', 'true')
        self.set_header('Content-Type', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')


class GameCreatorHandler(BaseHandler):
    '''
    This web handler is responsible for registering new game instances, as well as forwarding
    player request to the correct game instance
    '''

    def initialize(self, app):
        self.app = app
        self.game_instances = app.game_instances

    @tornado.web.authenticated
    def post(self, game_id):
        '''
        Registers a new TornadoProvider at the game_id endpoint
        '''
        if (game_id == ""):
            game_id = get_rand_id()
        # Create game_provider here
        print("Registering: ", game_id)
        game = self.app.run_new_game(game_id, self.app.FLAGS)
        self.game_instances[game_id] = game
        self.set_status(201)
        self.write(json.dumps(game_id))

