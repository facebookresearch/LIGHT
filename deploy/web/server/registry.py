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
        self.router = RuleRouter([])
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
        new_rule = Rule(PathMatches(f'/game/{game_id}'), game_provider)
        self.app.router.add_rules([new_rule])
