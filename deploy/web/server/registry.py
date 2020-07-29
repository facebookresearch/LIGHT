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
from tornado import ioloop
from tornado import locks
from tornado import gen
from tornado.routing import (
    PathMatches,
    Rule,
    RuleRouter,
)
from deploy.web.server.game_instance import GameInstance
from deploy.web.server.tornado_server import TornadoPlayerFactory
from deploy.web.server.telnet_server import TelnetPlayerProvider
from light.graph.builders.user_world_builder import UserWorldBuilder
from light.data_model.light_database import LIGHTDatabase
import copy


def get_rand_id():
    return str(uuid.uuid4())


tornado_settings = {
    "autoescape": None,
    "cookie_secret": "0123456789",  # TODO: Placeholder, do not include in repo when deploy!!!
    "compiled_template_cache": False,
    "debug": "/dbg/" in __file__,
    "login_url": "/login",
}


class RegistryApplication(tornado.web.Application):
    """
    This application simply takes the user game request and will
        - Forward it to the designated tornado provider (if an id is given)
        - Assign to a random (or default) game based on some load balancing
    """

    def __init__(self, FLAGS, ldb, default=True):
        self.game_instances = {}
        self.step_callbacks = {}
        self.FLAGS = FLAGS
        self.ldb = ldb
        super(RegistryApplication, self).__init__(
            self.get_handlers(FLAGS, ldb, default), **tornado_settings
        )

    def get_handlers(self, FLAGS, ldb, default=True):
        self.tornado_provider = TornadoPlayerFactory(
            self.game_instances, FLAGS.hostname, FLAGS.port
        )
        self.router = RuleRouter(
            [Rule(PathMatches(f"/game.*/socket"), self.tornado_provider.app)]
        )
        TEN_MINUTES = 600000
        tornado.ioloop.PeriodicCallback(self.cleanup_games, TEN_MINUTES).start()

        return [
            (r"/game/new/(.*)", GameCreatorHandler, {"app": self}),
            (r"/game(.*)", self.router),
        ]

    def cleanup_games(self):
        """
            Goes through the game instances, cleaning up any game that does
            not have a connection in the past 10 minutes
        """
        TIMEOUT = 10  # timeout to clear with no players, in minutes
        curr_time = time.time()
        iterate_over = [
            (g_id, len(g.players), g.last_connection)
            for g_id, g in self.game_instances.items()
        ]

        for game_id, num_players, last_conn in iterate_over:
            if game_id == "":
                continue
            no_players = num_players == 0
            diff = (curr_time - last_conn) / 60  # get minutes
            if no_players and diff > TIMEOUT:
                print("deleting:", game_id)
                self.step_callbacks[game_id].stop()
                del self.step_callbacks[game_id]
                del self.game_instances[game_id]

    # TODO: Move this to utils
    # This is basically it though - want to create a new world?  For now call these methods, then
    # attach the game's tornado provider
    def run_new_game(self, game_id, ldb, player_id=None, world_id=None):

        if world_id is not None and player_id is not None:
            builder = UserWorldBuilder(ldb, player_id=player_id, world_id=world_id)
            _, graph = builder.get_graph()
            game = GameInstance(game_id, ldb, g=graph)
        else:
            game = GameInstance(game_id, ldb)
            graph = game.g

        self.game_instances[game_id] = game
        game.register_provider(self.tornado_provider)
        self.step_callbacks[game_id] = tornado.ioloop.PeriodicCallback(
            game.run_graph_step, 125
        )
        self.step_callbacks[game_id].start()
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
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Acces-Control-Allow-Credentials", "true")
        self.set_header("Content-Type", "*")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")


class GameCreatorHandler(BaseHandler):
    """
    This web handler is responsible for registering new game instances, as well as forwarding
    player request to the correct game instance
    """

    def initialize(self, app):
        self.app = app
        self.game_instances = app.game_instances

    @tornado.web.authenticated
    def post(self, game_id):
        """
        Registers a new TornadoProvider at the game_id endpoint
        """
        # Ensures we do not overwrite the default game if someone forgets an id
        if game_id == "":
            game_id = get_rand_id()

        world_id = self.get_argument("world_id", None, True)
        if world_id is not None:
            username = tornado.escape.xhtml_escape(self.current_user)
            with self.app.ldb as db:
                player = db.get_user_id(username)
                if not db.is_world_owned_by(world_id, player):
                    self.set_status(403)
                    return
            game = self.app.run_new_game(game_id, self.app.ldb, player, world_id)
        else:
            game = self.app.run_new_game(game_id, self.app.ldb)

        # Create game_provider here
        print("Registering: ", game_id)
        self.game_instances[game_id] = game
        self.set_status(201)
        self.write(json.dumps(game_id))
