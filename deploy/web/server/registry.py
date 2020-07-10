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

def get_rand_id():
    return str(uuid.uuid4())

tornado_settings = {
    "autoescape": None,
    "cookie_secret": "0123456789", #TODO: Placeholder, do not include in repo when deploy!!!
    "compiled_template_cache": False,
    "debug": "/dbg/" in __file__,
    "login_url": "/login",
}

class Application(tornado.web.Application):
    def __init__(self):
        self.subs = {}
        self.new_subs = []
        super(Application, self).__init__(self.get_handlers(), **tornado_settings)

    def get_handlers(self):
        path_to_build = here + "/../build/"
        # NOTE: We choose to keep the StaticUIHandler, despite this handler never being
        #       hit in the top level RuleRouter from run_server.py in case this application
        #       is run standalone for some reason.
        return [
            (r"/game(.*)", GameRouterHandler, {'app': self}),
        ]


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

    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)
            self.finish(
                json.dumps(
                    {
                        'error': {
                            'code': status_code,
                            'message': self._reason,
                            'traceback': lines,
                        }
                    }
                )
            )
        else:
            self.finish(
                json.dumps({'error': {'code': status_code, 'message': self._reason}})
            )

class GameRouterHandler(BaseHandler):
'''
This web handler is responsible for registering new game instances, as well as forwarding
player request to the correct game instance
'''
    @tornado.web.authenticated
    def get(self, game_id):
        '''
        Given a game id, forward the request to the appropiate game 
        '''
        name = tornado.escape.xhtml_escape(self.current_user)

    @tornado.web.authenticated
    def post(self, game_id):
        '''
        Registers a new TornadoProvider at the game_id endpoint
        '''
