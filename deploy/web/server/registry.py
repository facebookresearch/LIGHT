#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import time
import uuid
import asyncio
import tornado.web
from tornado.routing import (
    PathMatches,
    Rule,
    RuleRouter,
)
from deploy.web.server.game_instance import GameInstance, TutorialInstance
from deploy.web.server.tornado_server import TornadoPlayerFactory
from light.graph.builders.user_world_builder import UserWorldBuilder
from light.data_model.db.users import PlayerStatus
from light.world.world import WorldConfig

from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from light.registry.model_pool import ModelPool
    from light.data_model.db.episodes import EpisodeDB
    from light.data_model.db.users import UserDB

    # TODO refactor when WorldServer is realized fully
    from deploy.web.server.run_server import WorldServerConfig


def get_rand_id():
    return str(uuid.uuid4())


class RegistryApplication(tornado.web.Application):
    """
    This application simply takes the user game request and will
        - Forward it to the designated tornado provider (if an id is given)
        - Assign to a random (or default) game based on some load balancing
    """

    def __init__(
        self,
        cfg: "WorldServerConfig",
        model_pool: "ModelPool",
        tornado_settings: Dict[str, Any],
        episode_db: "EpisodeDB",
        user_db: "UserDB",
    ):
        self.game_instances = {}
        self.step_callbacks = {}
        self.tutorial_map = {}  # Player ID to game ID
        self.model_pool = model_pool
        self.episode_db = episode_db
        self.user_db = user_db
        self.base_world_config = WorldConfig(
            episode_db=episode_db,
            model_pool=model_pool,
            is_logging=cfg.is_logging,
            safety_classifier_path=cfg.safety_classifier_path,
            magic_db_path=cfg.magic_db_path,
        )
        self.tutorial_builder_config = cfg.tutorial_builder
        self.builder_config = cfg.builder
        super(RegistryApplication, self).__init__(
            self.get_handlers(cfg, user_db, tornado_settings), **tornado_settings
        )
        self.opt = vars(self.FLAGS)

    def get_handlers(self, cfg: "WorldServerConfig", user_db, tornado_settings):
        self.tornado_provider = TornadoPlayerFactory(
            self,
            cfg.hostname,
            cfg.port,
            given_tornado_settings=tornado_settings,
            user_db=user_db,
        )
        self.router = RuleRouter(
            [
                Rule(PathMatches(f"/game.*/socket"), self.tornado_provider.app),
                Rule(PathMatches(f"/game/api/.*"), self.tornado_provider.app),
            ]
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

    async def run_new_game(self, game_id, player_id=None, world_id=None):
        if world_id is not None and player_id is not None:
            # TODO remake loading user worlds as part of phase 3
            raise NotImplementedError(
                "We don't handle this case yet, will need UserWorldBuilder"
            )
            # builder = UserWorldBuilder(ldb, player_id=player_id, world_id=world_id)
            # _, world = await builder.get_graph()
            # game = await GameInstance.get(game_id, ldb, g=world, opt=self.opt)
        else:
            game = await GameInstance.get(
                game_id,
                builder_config=self.builder_config,
                world_config=self.base_world_config,
            )
            world = game.world
        game.fill_souls(self.model_pool)

        self.game_instances[game_id] = game
        game.register_provider(self.tornado_provider)
        self.step_callbacks[game_id] = tornado.ioloop.PeriodicCallback(
            game.run_graph_step, 125
        )
        self.step_callbacks[game_id].start()
        return game

    async def run_tutorial(self, user_id, on_complete):
        game_id = get_rand_id()
        game = await TutorialInstance.get(
            game_id,
            builder_config=self.tutorial_builder_config,
            world_config=self.base_world_config,
        )
        game.fill_souls(self.model_pool)
        world = game.world

        async def run_or_cleanup_world():
            await game.run_graph_step()
            if game._should_shutdown or game._did_complete:
                if (
                    game._did_complete and self.user_db is not None
                ):  # TODO should always be set
                    self.user_db.update_player_status(user_id, PlayerStatus.STANDARD)
                    on_complete()
                self.step_callbacks[game_id].stop()
                del self.step_callbacks[game_id]
                # TODO delete this game instance
                del self.game_instances[game_id]
                del self.tutorial_map[user_id]

        self.game_instances[game_id] = game
        self.tutorial_map[user_id] = game_id
        game.register_provider(self.tornado_provider)
        self.step_callbacks[game_id] = tornado.ioloop.PeriodicCallback(
            run_or_cleanup_world, 125
        )
        self.step_callbacks[game_id].start()
        return game_id


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
    This web handler is responsible for registering new game instances,
    as well as forwarding player request to the correct game instance
    """

    def initialize(self, app):
        self.app = app
        self.game_instances = app.game_instances

    @tornado.web.authenticated
    async def post(self, game_id):
        """
        Registers a new TornadoProvider at the game_id endpoint
        """
        # Ensures we do not overwrite the default game if someone forgets an id
        if game_id == "":
            game_id = get_rand_id()

        world_id = self.get_argument("world_id", None, True)
        if world_id is not None:
            username = tornado.escape.xhtml_escape(self.current_user)
            with self.app.user_db as user_db:
                player = user_db.get_user_id(username)
                # TODO update with the env DB
                # if not user_db.is_world_owned_by(world_id, player):
                #     self.set_status(403)
                #     return
            game = await self.app.run_new_game(game_id, player, world_id)
        else:
            game = await self.app.run_new_game(game_id)

        # Create game_provider here
        print("Registering: ", game_id)
        self.game_instances[game_id] = game
        self.set_status(201)
        self.write(json.dumps(game_id))
