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
import time
import tornado.web
from tornado.ioloop import IOLoop
from tornado import locks
from tornado import gen
from tornado.routing import (
    PathMatches, Rule, RuleRouter,
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
    def __init__(self):
        self.game_instances = {}
        super(Application, self).__init__(self.get_handlers(), **tornado_settings)

    def get_handlers(self):
        id = get_rand_id()
        t_provider_default = run_new_game(id)
        self.router = RuleRouter([Rule(PathMatches(f'/game/socket'), t_provider_default.application)])
        return [
            (r"/game/new/(.*)", GameCreatorHandler, {'app': self}),
            (r"/game/(.*)", self.router)
        ]

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
        self.default = None

    @tornado.web.authenticated
    def post(self, game_id):
        '''
        Registers a new TornadoProvider at the game_id endpoint
        '''
        # Create game_provider here
        tornado_provider = run_new_game(game_id)
        new_rule = Rule(PathMatches(f'/game/{game_id}.*'), tornado_provider.application)
        self.app.router.add_rules([new_rule])

# TODO: Move this to utils
# This is basically it though - want to create a new world?  For now call these methods, then
# attach the game's tornado provider 
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

def run_new_game(game_id):
    game = GameInstance()
    graph = game.g
    tornado_provider = TornadoWebappPlayerProvider(graph, FLAGS.hostname, FLAGS.port)
    game.register_provider(tornado_provider)
    provider = TelnetPlayerProvider(graph, FLAGS.hostname, FLAGS.port + 1)
    game.register_provider(provider)
    router_run(FLAGS, tornado_provider)
    t = threading.Thread(
        target=game.run_graph(), args=(FLAGS, tornado_provider), name=f'Game{game_id}Thread', daemon=True
    )
    t.start()
    return tornado_provider