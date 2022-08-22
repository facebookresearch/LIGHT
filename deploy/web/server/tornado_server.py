#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from deploy.web.server.game_instance import (
    Player,
    GameInstance,
)
from light.data_model.db.users import PlayerStatus
from light.world.player_provider import PlayerProvider
from light.world.quest_loader import QuestLoader
from light.graph.events.graph_events import RewardEvent
from light.world.souls.tutorial_player_soul import TutorialPlayerSoul

import argparse
import inspect
import json
import logging
import os
import threading
import time
import traceback
import uuid
import warnings
import asyncio
import hashlib
from collections import defaultdict
import tornado.ioloop as ioloop
import tornado.web
import tornado.auth
import tornado.websocket
import tornado.escape
from light.graph.events.graph_events import (
    SoulSpawnEvent,
    SystemMessageEvent,
    DeathEvent,
)

from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.world.world import World
    from light.data_model.db.users import UserDB

# Monkeypatch to allow samesite for iframe usage
from http.cookies import Morsel

Morsel._reserved["samesite"] = "SameSite"


DEFAULT_PORT = 35496
DEFAULT_HOSTNAME = "localhost"
QUESTS_LOCATION = "/home/ubuntu/data/quests"
if QUESTS_LOCATION is not None and os.path.exists(QUESTS_LOCATION):
    quest_loader = QuestLoader(QUESTS_LOCATION)
else:
    quest_loader = None
TRANSITION_AFTER_TUTORIAL = 4
here = os.path.abspath(os.path.dirname(__file__))

_seen_warnings = set()

"""
TornadoWebappPlayers have a number of commands that they're able to communicate
using.

All messages are sent with a `command` field and a `data` field.

Server -> Player commands:
command      |   data
'act'        -  Text action that the user intends to take
'descs'      -  empty object. Will cause a responding `descs` call.
'contains'   -  Array of graph ids to query the contents of
'attributes' -  Array of graph ids to query the attributes for

Player -> server commands:
command      |   data
'actions'    -  Array of Action dicts, structure defined below in the
             |  Actions section (currently fairly informal, happy to expand)
             |  what is contained in this
'descs'      -  Contains a map from graph_ids to the canonical descriptive
             |  name for that character. Any additional queries should
             |  use these ids to refer to things in the graph world
'contains'   -  Returns a mapping from graph_id to objects contained in
             |  that node for every node listed in a 'contains' request
'attributes' -  Returns a mapping from graph_id to attributes for all
             |  nodes listed in the attributes request
'register'   -  When a socket connection is opened, this message comes through
             |  with a unique id for this socket connection
'reject'     -  When a socket connection fails, this message comes through
             |  with a text message for what went wrong

Actions follow the following structure approximately:
{
    caller: string name of the action that caused this message to be created,
            is sometimes 'null' for actions that were generated without a cause
    name:   string name of a specified format the action takes based on the
            caller. For example, "examine" has "examine_object" and "witnessed"
            as a possible name to distinguish between being the examiner and
            seeing someone else examine. These are defined in graph_functions
    room_id: graph id for location where this action happened
    text:  processed text for the action from the perspective of the reciever
    actors: graph ids of the actor and any recipients.
    text_actors: text names for the actors (does not handle "you")
    content: only present in speech-based actions, contains the actual speech
}
"""


def warn_once(msg, warningtype=None):
    """
    Raise a warning, but only once.
    :param str msg: Message to display
    :param Warning warningtype: Type of warning, e.g. DeprecationWarning
    """
    global _seen_warnings
    if msg not in _seen_warnings:
        _seen_warnings.add(msg)
        warnings.warn(msg, warningtype, stacklevel=2)


def get_salted_hash(in_string):
    """Return a hash string for the given string using sha-256"""
    salted_string = in_string + tornado_settings["preauth_secret"] + in_string
    return hashlib.sha256(salted_string.encode("utf-8")).hexdigest()[:20]


def get_rand_id():
    return str(uuid.uuid4())


def ensure_dir_exists(path):
    """Make sure the parent dir exists for path so we can write a file."""
    try:
        os.makedirs(os.path.dirname(path))
    except OSError as e1:
        assert e1.errno == 17  # errno.EEXIST
        pass


def get_path(filename):
    """Get the path to an asset."""
    cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    return os.path.join(cwd, filename)


tornado_settings = None


class Application(tornado.web.Application):
    def __init__(self, given_tornado_settings=None, user_db: Optional["UserDB"] = None):
        global tornado_settings
        use_tornado_settings = tornado_settings
        if given_tornado_settings is not None:
            use_tornado_settings = given_tornado_settings
        self.subs = {}
        self.new_subs = defaultdict(list)
        self.user_db = user_db
        self.user_node_map: Dict[str, Optional["GraphAgent"]] = {}
        self.world: Optional["World"] = None
        super(Application, self).__init__(self.get_handlers(), **use_tornado_settings)

    def get_handlers(self):
        path_to_build = here + "/../build/"
        # NOTE: We choose to keep the StaticUIHandler, despite this handler never being
        #       hit in the top level RuleRouter from run_server.py in case this application
        #       is run standalone for some reason.
        return [
            (r"/game/api/(.*)", ApiHandler, {"app": self, "user_db": self.user_db}),
            (
                r"/game(.*)/socket",
                SocketHandler,
                {"app": self, "user_db": self.user_db},
            ),
            (r"/play", GameHandler, {"app": self, "user_db": self.user_db}),
            (r"/(.*)", StaticUIHandler, {"path": path_to_build}),
        ]


# StaticUIHandler serves static front end, defaulting to index.html served
# If the file is unspecified.
class StaticUIHandler(tornado.web.StaticFileHandler):
    def parse_url_path(self, url_path):
        PRIMARY_PAGE = "index.html"
        print(url_path)
        if not url_path or url_path.endswith("/"):
            url_path = url_path + PRIMARY_PAGE
            print("UPDATED", url_path)
        return url_path


class SocketHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, app, user_db):
        self.user_db = user_db
        self.app = app
        self.subs = app.subs
        self.new_subs = app.new_subs
        self.alive = True
        self.alive_sent = False
        self.actions = []
        self.player = None
        self.sid = get_rand_id()
        self.user_db = app.user_db

    def safe_write_message(self, msg):
        try:
            self.write_message(msg)
        except tornado.websocket.WebSocketClosedError:
            self.alive = False

    def check_origin(self, origin):
        return True

    def set_player(self, player):
        self.player = player

    def user_should_do_tutorial(self, user_id):
        player = self.user_db.get_player(user_id)
        return player.account_status == PlayerStatus.TUTORIAL

    async def launch_game_for_user(self, user_id, game_id):
        # Check for custom game world
        if game_id not in self.app.registry.game_instances:
            self.close()
            # TODO: Have an error page about game deleted
            self.redirect("/game/")
        graph_purgatory = self.app.registry.game_instances[game_id].world.purgatory
        if self.alive:
            new_player = TornadoPlayerProvider(
                self,
                graph_purgatory,
                user_db=self.user_db,
                user_id=user_id,
            )
            await new_player.init_soul()
            self.app.registry.game_instances[game_id].players.append(new_player)

    async def open(self, game_id):
        """
        Open a websocket, validated either by a valid user cookie or
        by a validated preauth.
        """
        preauth_context = self.get_secure_cookie("preauth_context")
        user_id = None
        if preauth_context is not None:  # If there is any preauth
            preauth = self.get_secure_cookie("preauth")
            hashed_user_id = json.loads(preauth)
            user_id = self.user_db.get_player(hashed_user_id).db_id

            # See if the context matches our generated hash
            context_token = json.loads(self.get_secure_cookie("context_token"))
            preauth_context = json.loads(preauth_context)
            context_hash = get_salted_hash(preauth_context)
            if context_hash != context_token:
                # User created their own context cookie
                print(f"Logged in user {user} tried to use invalid preauth context!")
                self.close()
                return
        else:
            user_json = self.get_secure_cookie("user")
            if user_json is not None and user_json != "":
                user_id = json.loads(user_json)

        print("Requesting for user", user_id)
        if user_id is not None:
            logging.info("Opened new socket from ip: {}".format(self.request.remote_ip))
            logging.info("For game: {}".format(game_id))

            loop = tornado.ioloop.IOLoop.current()

            # First check for tutorials
            if self.user_should_do_tutorial(user_id):
                # Spawn a tutorial world for this user, or inject them into
                # their existing world
                if user_id in self.app.registry.tutorial_map:
                    game_id = self.app.registry.tutorial_map[user_id]
                else:
                    orig_game_id = game_id

                    def on_complete():
                        time.sleep(TRANSITION_AFTER_TUTORIAL)
                        loop.spawn_callback(
                            self.launch_game_for_user, user_id, orig_game_id
                        )

                    async def create_and_run_tutorial():
                        game_id = await self.app.registry.run_tutorial(
                            user_id, on_complete
                        )
                        await self.launch_game_for_user(user_id, game_id)

                    loop.spawn_callback(create_and_run_tutorial)
            else:
                loop.spawn_callback(self.launch_game_for_user, user_id, game_id)
        else:
            self.close()
            self.redirect("/#/login")

    def send_alive(self):
        self.safe_write_message(json.dumps({"command": "register", "data": self.sid}))
        self.alive_sent = True

    async def on_message(self, message):
        logging.info("from web client: {}".format(message))
        msg = tornado.escape.json_decode(tornado.escape.to_basestring(message))
        cmd = msg.get("command")
        if self.player is None:
            return
        if cmd == "act":
            data = msg["data"]
            await self.player.act(data["text"], data["event_id"])
        elif cmd == "hb":
            pass  # heartbeats
        else:
            logging.warning(f"THESE COMMANDS HAVE BEEN DEPRICATED: {msg}")

    def on_close(self):
        self.alive = False


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *request, **kwargs):
        self.include_host = False
        super(BaseHandler, self).__init__(*request, **kwargs)

    def initialize(self, user_db):
        self.user_db = user_db

    def get_login_url(self):
        return "/#/login"

    def get_current_user(self):
        user_json = self.get_secure_cookie(
            "user"
        )  # Need to refactor into 'get_identity', then have base and preauth handler implementations
        if user_json is not None and len(user_json) != 0:
            user_decoded = tornado.escape.json_decode(user_json)
            if len(user_decoded) == 0:
                return None
            try:
                user = self.user_db.get_player(user_decoded)
                user_id = user.db_id
            except Exception as e:
                # User id does not exist in the user_db, either
                # we've updated the user table or someone
                # is fishing :/
                # Also can be caused when auth is refreshed
                print(f"User {user_decoded} tried to log in, but was rejected.")
                return None
            print(f"User {user.extern_id, user_id} logged in.")
            return user_id
        else:
            return None

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")

    # TODO maybe use cookies to restore previous game state?
    def write_error(self, status_code, **kwargs):
        logging.error("ERROR: %s: %s" % (status_code, kwargs))
        if "exc_info" in kwargs:
            logging.info(
                "Traceback: {}".format(traceback.format_exception(*kwargs["exc_info"]))
            )
        if self.settings.get("debug") and "exc_info" in kwargs:
            logging.error("rendering error page")

            exc_info = kwargs["exc_info"]
            # exc_info is a tuple consisting of:
            # 1. The class of the Exception
            # 2. The actual Exception that was thrown
            # 3. The traceback opbject
            try:
                params = {
                    "error": exc_info[1],
                    "trace_info": traceback.format_exception(*exc_info),
                    "request": self.request.__dict__,
                }

                self.render("error.html", **params)
                logging.error("rendering complete")
            except Exception as e:
                logging.error(e)
        else:
            # In production, reroute to error
            self.redirect("/#/error")


class ApiHandler(BaseHandler):
    def initialize(self, app, user_db):
        self.user_db = user_db
        self.app = app

    @tornado.web.authenticated
    def get(self, *args):
        print("THE ARGS", *args)
        user_json = self.get_secure_cookie("user")
        if user_json is not None and user_json != "":
            user_decoded = tornado.escape.json_decode(user_json)

            split_inputs = args[0].split("/")
            api_command = split_inputs[0]
            other_path_args = split_inputs[1:]

            # TODO(jack) this should really be refactored alongside the
            # TornadoPlayerProvider. Too many complicated routes back here.
            # Then these can go to a subapplication and use Tornado routing
            # rather than whatever this is
            if api_command == "my_agent":

                # TODO do stuff here! You can access self.app.user_node_map
                print(self.app.user_node_map)
                print(other_path_args)
                print(user_decoded)

                self.write(json.dumps({"data": "Something"}))
                return
        # TODO Not a real error code, but should be sometime
        self.write(json.dumps({"failed": "user was logged out"}))

    @tornado.web.authenticated
    def post(self, *args):
        data = tornado.escape.json_decode(self.request.body)
        user_json = self.get_secure_cookie("user")
        print(data)
        if user_json is not None and user_json != "":
            user_decoded = tornado.escape.json_decode(user_json)

            split_inputs = args[0].split("/")
            api_command = split_inputs[0]
            other_path_args = split_inputs[1:]
            print("API COMMAND", api_command)
            print("ARGS", args)
            if api_command == "grant_reward":
                my_node = self.app.user_node_map[user_decoded]
                world = self.app.world
                target_event_id = data["target_event_id"]
                target_node_id = data["target_node_id"]
                print("EVENTID: " + target_event_id)
                print("NODEID: " + target_node_id)
                # TODO ensure that the target node exists
                target_node = world.oo_graph.get_node(target_node_id)

                event = RewardEvent(
                    my_node,
                    target_nodes=[target_node],
                    target_event_id=target_event_id,
                )
                event.execute(world)

                self.write(json.dumps({"data": event.to_frontend_form(my_node)}))
                return
            self.write(json.dumps({"failed": "invalid command"}))
        else:
            # TODO Not a real error code, but should be sometime
            self.write(json.dumps({"failed": "user was logged out"}))


class LandingApplication(tornado.web.Application):
    def __init__(
        self,
        user_db: "UserDB",
        hostname=DEFAULT_HOSTNAME,
        password="LetsPlay",
        given_tornado_settings=None,
    ):
        self.user_db = user_db
        global tornado_settings
        tornado_settings = given_tornado_settings
        super(LandingApplication, self).__init__(
            self.get_handlers(user_db, hostname, password), **tornado_settings
        )

    def get_handlers(self, user_db, hostname=DEFAULT_HOSTNAME, password="LetsPlay"):
        return [
            (r"/", LandingHandler, {"user_db": user_db}),
            (r"/#(.*)", LandingHandler, {"user_db": user_db}),
            (r"/#/login", LandingHandler, {"user_db": user_db}),
            (r"/#/error", NotFoundHandler, {"user_db": user_db}),
            (
                r"/preauth/(.*)/(.*)/(.*)/",
                PreauthGameHandler,
                {"user_db": user_db, "hostname": hostname},
            ),
            (r"/play", GameHandler, {"user_db": user_db}),
            (r"/play/?id=.*", GameHandler, {"user_db": user_db}),
            (r"/play/*", GameHandler, {"user_db": user_db}),
            (r"/build", BuildHandler, {"user_db": user_db}),
            (
                r"/login",
                LoginHandler,
                {"user_db": user_db, "hostname": hostname, "password": password},
            ),
            (
                r"/auth/fblogin",
                FacebookOAuth2LoginHandler,
                {"user_db": user_db, "hostname": hostname, "app": self},
            ),
            (r"/logout", LogoutHandler, {"hostname": hostname}),
            (
                r"/terms",
                StaticPageHandler,
                {"user_db": user_db, "target": "/html/terms.html"},
            ),
            (
                r"/#/bye",
                LandingHandler,
                {"user_db": user_db},
            ),
            (
                r"/about",
                StaticLoggedInPageHandler,
                {"user_db": user_db, "target": "/html/about.html"},
            ),
            (
                r"/profile",
                StaticLoggedInPageHandler,
                {"user_db": user_db, "target": "/html/profile.html"},
            ),
            (r"/report", ReportHandler, {"user_db": user_db}),
            (r"/(.*)", StaticUIHandler, {"path": here + "/../build/"}),
        ]


class LandingHandler(BaseHandler):
    def get(self):
        self.render(here + "/../build/index.html")


class BuildHandler(BaseHandler):
    def get(self):
        self.render(here + "/../build/builder.html")


class GameHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render(here + "/../build/game.html")


class PreauthGameHandler(BaseHandler):
    def initialize(
        self,
        user_db,
        hostname=DEFAULT_HOSTNAME,
    ):
        self.user_db = user_db
        self.hostname = hostname

    def validate_login_details(self, user_id, context_id, auth_token) -> bool:
        """
        Check if the provided details are correct, as the user id + context id + secret
        should hash to the auth token.
        """
        combo_string = f"{user_id}-{context_id}"
        hashed_key = get_salted_hash(combo_string)
        return hashed_key == auth_token

    def get(self, user_id, context_id, auth_token):
        """
        Preauth access requires that the salted hash of user_id and context_id matches
        the provided auth_token, which ensures that our server was the one to generate
        the auth token.

        We then set a cookie with a preauth user id, the context of the preauth, and
        a context auth token we generate the hash for (this way we can assert the
        cookie contents weren't edited).
        """
        if self.validate_login_details(user_id, context_id, auth_token):
            user_hash = get_salted_hash(user_id)
            context_hash = get_salted_hash(context_id)
            hashed_user_id = f"preauth-{user_hash}"
            self.user_db.create_user(extern_id=hashed_user_id, is_preauth=True)
            self.set_secure_cookie(
                "preauth",
                tornado.escape.json_encode(hashed_user_id),
                expires_days=1,
                domain=self.hostname,
                httponly=True,
                samesite=None,
                secure=True,
            )
            self.set_secure_cookie(
                "preauth_context",
                tornado.escape.json_encode(context_id),
                expires_days=1,
                domain=self.hostname,
                httponly=True,
                samesite=None,
                secure=True,
            )
            self.set_secure_cookie(
                "context_token",
                tornado.escape.json_encode(context_hash),
                expires_days=1,
                domain=self.hostname,
                httponly=True,
                samesite=None,
                secure=True,
            )
            self.render(here + "/../build/game.html")
        else:
            self.redirect("/#/error")


class NotFoundHandler(BaseHandler):
    def get(self):
        self.redirect("/#/error")


class StaticPageHandler(BaseHandler):
    def initialize(self, target, user_db):
        self.target_page = here + target
        self.user_db = user_db

    def get(self):
        self.render(self.target_page)


class StaticLoggedInPageHandler(StaticPageHandler):
    @tornado.web.authenticated
    def get(self):
        self.render(self.target_page)


class FacebookOAuth2LoginHandler(BaseHandler, tornado.auth.FacebookGraphMixin):
    """
    See https://www.tornadoweb.org/en/stable/_modules/tornado/auth.html#FacebookGraphMixin
    """

    def initialize(
        self,
        user_db,
        hostname,
        app,
    ):
        self.app = app
        self.user_db = user_db
        self.hostname = hostname

    async def get_privacy_restricted_user_id(self, redirect_url) -> str:
        """
        While we already don't request user input for our API key,
        this method ensures that we're only getting the `id` key.

        DO NOT CHANGE THIS METHOD
        """
        fb_user = await self.get_authenticated_user(
            redirect_uri=redirect_url,
            client_id=self.app.settings["facebook_api_key"],
            client_secret=self.app.settings["facebook_secret"],
            code=self.get_argument("code"),
        )
        return fb_user["id"]

    async def get(self):
        redirect = "https://" + self.request.host + "/auth/fblogin"
        if self.get_argument("code", False):
            fb_app_scoped_id = await self.get_privacy_restricted_user_id(
                redirect_url=redirect,
            )

            user_id = self.user_db.create_user(
                extern_id=fb_app_scoped_id, is_preauth=False
            )
            self.set_current_user(user_id)
            self.redirect("/play/")
            return
        self.authorize_redirect(
            redirect_uri=redirect,
            client_id=self.app.settings["facebook_api_key"],
        )

    def set_current_user(self, user_id):
        if user_id:
            self.set_secure_cookie(
                "user",
                tornado.escape.json_encode(user_id),
                domain=self.hostname,
                secure=True,
                httponly=True,
            )
        else:
            self.set_secure_cookie(
                "user",
                "",
                domain=self.hostname,
                secure=True,
                httponly=True,
            )


class LoginHandler(BaseHandler):
    def initialize(
        self,
        user_db,
        hostname=DEFAULT_HOSTNAME,
        password="LetsPlay",
    ):
        self.user_db = user_db
        self.hostname = hostname
        self.password = password

    def get(self):
        self.render(here + "/build/index.html", next=self.get_argument("next", "/"))
        self.next = next

    def post(self):
        name = self.get_argument("name", "")
        password = self.get_argument("password", "")
        if password == self.password:
            user_id = self.user_db.create_user(extern_id=name, is_preauth=False)
            self.set_current_user(user_id)
            # self.redirect(self.get_argument("next", "/"))
            self.redirect("/play/")
        else:
            error_msg = "?error=" + tornado.escape.url_escape("incorrect")
            self.redirect("/#/login" + error_msg)

    def set_current_user(self, user_id):
        if user_id:
            self.set_secure_cookie(
                "user",
                tornado.escape.json_encode(user_id),
                domain=self.hostname,
                # secure=True, login handler is for local testing
                httponly=True,
            )
        else:
            self.set_secure_cookie(
                "user",
                "",
                domain=self.hostname,
                secure=True,
                httponly=True,
            )


class LogoutHandler(BaseHandler):
    def initialize(
        self,
        hostname=DEFAULT_HOSTNAME,
    ):
        self.hostname = hostname

    def get(self):
        self.set_secure_cookie(
            "user",
            "",
            domain=self.hostname,
            secure=True,
            httponly=True,
        )
        self.redirect("/#/bye")


class ReportHandler(BaseHandler):
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        print("Report gotten:", data)
        report_dir = os.path.expanduser("~/light_reports/")
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        tmp_filename = f"report-{time.time()}"
        while os.path.exists(os.path.join(report_dir, f"{tmp_filename}.json")):
            # Disgusting hack to get multiple saves at the same time
            tmp_filename += "a"
        dump_loc = os.path.join(report_dir, f"{tmp_filename}.json")
        with open(os.path.join(report_dir, dump_loc), "w+") as report_file:
            json.dump(data, report_file)


class TornadoPlayerProvider(PlayerProvider):
    """
    Player Provider for the web app
    """

    def __init__(self, socket, purgatory, user_db=None, user_id=None, context=None):
        self.socket = socket
        self.player_soul = None
        self.purgatory = purgatory
        if quest_loader is not None:
            self.quest_loader = quest_loader
        socket.set_player(self)
        socket.send_alive()
        self.user_db = user_db
        self.user_id = user_id
        self.context = context
        # TODO a TornadoPlayerProvider refactor is likely desired, combining
        # the APIs for socket and HTTP requests to use logged in user
        # and their state in the world at the same time.
        self.app = socket.app
        self.app.world = purgatory.world

    def register_soul(self, soul: "PlayerSoul"):
        """Save the soul as a local player soul"""
        self.player_soul = soul
        if self.user_id is not None:
            if self.user_db is not None:
                base_score = self.user_db.get_agent_score(self.user_id)
                # TODO refactor into elsewhere
                target_node = soul.target_node
                target_node.xp = base_score.score
                target_node.reward_xp = base_score.reward_xp
                target_node._base_class_experience = 0
                target_node._num_turns = 0
                target_node._base_experience = target_node.xp
                target_node._base_reward_points = target_node.reward_xp
            self.app.user_node_map[self.user_id] = soul.target_node

    async def player_observe_event(self, soul: "PlayerSoul", event: "GraphEvent"):
        """
        Send observation forward to the player in whatever format the player
        expects it to be.
        """
        # This will need to pass through the socket?
        view = event.view_as(soul.target_node)
        if not self.socket.alive_sent:
            return  # the socket isn't alive yet, let's wait
        dat = event.to_frontend_form(self.player_soul.target_node)
        filtered_obs = (
            dat if dat["text"] is not None and len(dat["text"].strip()) else None
        )
        if filtered_obs is not None:
            self.socket.safe_write_message(
                json.dumps({"command": "actions", "data": [dat]})
            )
        if (
            isinstance(event, DeathEvent)
            and event.actor.node_id == soul.target_node.node_id
        ):
            await self.purgatory.clear_soul(soul.target_node)

    async def act(self, action_data, event_id: Optional[str] = None):
        if self.player_soul is not None and self.player_soul.is_reaped:
            self.player_soul = None
        if self.player_soul is None:
            await self.init_soul()
            return
        player_agent = await self.player_soul.handle_act(action_data, event_id)

    async def init_soul(self):
        await self.purgatory.get_soul_for_player(self)
        if self.player_soul is None:
            dat = {"text": "Could not find a soul for you, sorry"}
            self.socket.safe_write_message(
                json.dumps({"command": "fail_find", "data": [dat]})
            )
        else:
            soul_id = self.player_soul.player_id
            SoulSpawnEvent(soul_id, self.player_soul.target_node).execute(
                self.purgatory.world
            )
            await self.player_soul.handle_act("look")
            self.player_soul.target_node.user_id = self.user_id
            self.player_soul.target_node.context_id = self.context

    def is_alive(self):
        return self.socket.alive

    async def on_reap_soul(self, soul):
        action = SystemMessageEvent(
            soul.target_node,
            [],
            text_content=(
                "Your soul slips off into the ether, unbound by your previous character. "
                '"Oh no... this won\'t do", says the Dungeon Master, before peering over '
                'into the world to see what has happened. "I can try to find a new place '
                "for your soul, if you'd like?\" Send anything to respawn."
            ),
        )
        soul.target_node.user_id = None
        soul.target_node.context_id = None
        dat = action.to_frontend_form(soul.target_node)
        self.socket.safe_write_message(
            json.dumps({"command": "actions", "data": [dat]})
        )
        if self.user_id is not None:
            if self.user_db is not None and not isinstance(soul, TutorialPlayerSoul):
                # TODO refactor out from server logic
                target_node = soul.target_node
                gained_experience = target_node.xp - target_node._base_experience
                net_reward_points = (
                    target_node.reward_xp - target_node._base_reward_points
                )
                db_id = target_node.db_id if target_node.db_id is not None else ""
                self.user_db.update_agent_score(
                    player_id=self.user_id,
                    agent_name_id=db_id,
                    points=gained_experience,
                    num_turns=target_node._num_turns,
                    reward_change=net_reward_points,
                )
                target_node._num_turns = 0
                target_node._base_experience = target_node.xp
                target_node._base_reward_points = target_node.reward_xp
            self.app.user_node_map[self.user_id] = None


class TornadoPlayerFactory:
    """
    A player provider is an API for adding new players into the game. It
    will be given opportunities to check for new players and should return
    an array of new players during these calls
    """

    def __init__(
        self,
        registry,
        hostname=DEFAULT_HOSTNAME,
        port=DEFAULT_PORT,
        user_db=None,
        listening=False,
        given_tornado_settings=None,
    ):
        self.registry = registry
        self.app = None
        self.user_db = user_db

        def _run_server():
            nonlocal listening
            nonlocal self
            nonlocal hostname
            nonlocal port
            self.my_loop = ioloop.IOLoop()
            self.app = Application(
                given_tornado_settings=given_tornado_settings, user_db=self.user_db
            )
            self.app.registry = self.registry
            if listening:
                self.app.listen(port, max_buffer_size=1024 ** 3)
                print(
                    "\nYou can connect to the game at http://%s:%s/" % (hostname, port)
                )
                print(
                    "You can connect to the socket at http://%s:%s/game/socket/"
                    % (hostname, port)
                )
            logging.info("TornadoWebProvider Started")

            if "HOSTNAME" in os.environ and hostname == DEFAULT_HOSTNAME:
                hostname = os.environ["HOSTNAME"]
            else:
                hostname = hostname

        _run_server()
        while self.app is None:
            asyncio.sleep(0.3)


def main():
    import numpy
    import random

    parser = argparse.ArgumentParser(description="Start the tornado server.")
    parser.add_argument(
        "--hostname",
        metavar="hostname",
        type=str,
        default=DEFAULT_HOSTNAME,
        help="host to run the server on.",
    )
    parser.add_argument(
        "--light-model-root",
        type=str,
        default="/Users/jju/Desktop/LIGHT/",
        help="models path. For local setup, use: /checkpoint/jase/projects/light/dialog/",
    )
    parser.add_argument(
        "--no-game-instance",
        action="store_true",
        help="does not initialize game instance",
    )
    parser.add_argument(
        "-port",
        metavar="port",
        type=int,
        default=DEFAULT_PORT,
        help="port to run the server on.",
    )
    FLAGS = parser.parse_args()
    FLAGS.safety_classifier_path = os.path.expanduser(
        "~/data/safety/OffensiveLanguage.txt"
    )

    random.seed(6)
    numpy.random.seed(6)

    if FLAGS.no_game_instance:
        provider = TornadoPlayerFactory(
            None, FLAGS.hostname, FLAGS.port, listening=True
        )
    else:
        game = asyncio.run(GameInstance(game_id=0, ldb=ldb))
        graph = game.world
        provider = TornadoPlayerFactory(
            graph, FLAGS.hostname, FLAGS.port, db=ldb, listening=True
        )
        game.register_provider(provider)
        game.run_graph()


if __name__ == "__main__":
    main()
