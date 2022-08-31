# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from deploy.web.server.game_instance import (
    Player,
    GameInstance,
)
from light.data_model.light_database import LIGHTDatabase
from light.world.player_provider import PlayerProvider
from light.world.quest_loader import QuestLoader
from light.graph.events.graph_events import init_safety_classifier, RewardEvent
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
from zmq.eventloop import ioloop

ioloop.install()  # Needs to happen before any tornado imports!

import tornado.ioloop  # noqa E402: gotta install ioloop first
import tornado.web  # noqa E402: gotta install ioloop first
import tornado.auth  # noqa E402: gotta install ioloop first
import tornado.websocket  # noqa E402: gotta install ioloop first
import tornado.escape  # noqa E402: gotta install ioloop first
from light.graph.events.graph_events import (
    SoulSpawnEvent,
    SystemMessageEvent,
    DeathEvent,
)

from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.world.world import World

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
    def __init__(self, given_tornado_settings=None, db=None):
        global tornado_settings
        use_tornado_settings = tornado_settings
        if given_tornado_settings is not None:
            use_tornado_settings = given_tornado_settings
        self.subs = {}
        self.new_subs = defaultdict(list)
        self.db = db
        self.user_node_map: Dict[str, Optional["GraphAgent"]] = {}
        self.world: Optional["World"] = None
        super(Application, self).__init__(self.get_handlers(), **use_tornado_settings)

    def get_handlers(self):
        path_to_build = here + "/../build/"
        # NOTE: We choose to keep the StaticUIHandler, despite this handler never being
        #       hit in the top level RuleRouter from run_server.py in case this application
        #       is run standalone for some reason.
        return [
            (r"/game/api/(.*)", ApiHandler, {"app": self, "database": self.db}),
            (r"/game(.*)/socket", SocketHandler, {"app": self, "database": self.db}),
            (r"/play", GameHandler, {"app": self, "database": self.db}),
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
    def initialize(self, app, database):
        self.db = database
        self.app = app
        self.subs = app.subs
        self.new_subs = app.new_subs
        self.alive = True
        self.alive_sent = False
        self.actions = []
        self.player = None
        self.sid = get_rand_id()
        self.db = app.db

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
        with self.db as ldb:
            flags = ldb.get_user_flags(user_id)
            return not flags.completed_onboarding

    def launch_game_for_user(self, user_id, game_id):
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
                db=self.db,
                user=user_id,
            )
            new_player.init_soul()
            self.app.registry.game_instances[game_id].players.append(new_player)

    def open(self, game_id):
        """
        Open a websocket, validated either by a valid user cookie or
        by a validated preauth.
        """
        preauth_context = self.get_secure_cookie("preauth_context")
        user = None
        if preauth_context is not None:  # If there is any preauth
            preauth = self.get_secure_cookie("preauth")
            user = json.loads(preauth)

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
            if user_json is not None:
                user = json.loads(user_json)

        print("Requesting for user", user)
        if user is not None:
            logging.info("Opened new socket from ip: {}".format(self.request.remote_ip))
            logging.info("For game: {}".format(game_id))
            # First check for tutorials
            if self.user_should_do_tutorial(user):
                # Spawn a tutorial world for this user, or inject them into
                # their existing world
                if user in self.app.registry.tutorial_map:
                    game_id = self.app.registry.tutorial_map[user]
                else:
                    orig_game_id = game_id

                    def on_complete():
                        time.sleep(TRANSITION_AFTER_TUTORIAL)
                        self.launch_game_for_user(user, orig_game_id)

                    game_id = self.app.registry.run_tutorial(user, on_complete)
            self.launch_game_for_user(user, game_id)
        else:
            self.close()
            self.redirect("/#/login")

    def send_alive(self):
        self.safe_write_message(json.dumps({"command": "register", "data": self.sid}))
        self.alive_sent = True

    def on_message(self, message):
        logging.info("from web client: {}".format(message))
        msg = tornado.escape.json_decode(tornado.escape.to_basestring(message))
        cmd = msg.get("command")
        if self.player is None:
            return
        if cmd == "act":
            data = msg["data"]
            self.player.act(data["text"], data["event_id"])
        else:
            print("THESE COMMANDS HAVE BEEN DEPRICATED")

    def on_close(self):
        self.alive = False


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *request, **kwargs):
        self.include_host = False
        super(BaseHandler, self).__init__(*request, **kwargs)

    def initialize(self, database):
        self.db = database

    def get_login_url(self):
        return "/#/login"

    def get_current_user(self):
        user_json = self.get_secure_cookie(
            "user"
        )  # Need to refactor into 'get_identity', then have base and preauth handler implementations
        if user_json:
            user_decoded = tornado.escape.json_decode(user_json)
            if len(user_decoded) == 0:
                return None
            try:
                with self.db as ldb:
                    user_id = ldb.get_user_id(user_decoded)
            except Exception as e:
                # User id does not exist in the database, either
                # we've updated the user table or someone
                # is fishing :/
                # Also can be caused when auth is refreshed
                print(f"User {user_decoded} tried to log in, but was rejected.")
                return None
            print(f"User {user_decoded, user_id} logged in.")
            return user_decoded
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
    def initialize(self, app, database):
        self.db = database
        self.app = app

    @tornado.web.authenticated
    def get(self, *args):
        print("THE ARGS", *args)
        user_json = self.get_secure_cookie("user")
        if user_json:
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
        if user_json:
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
        database,
        hostname=DEFAULT_HOSTNAME,
        password="LetsPlay",
        given_tornado_settings=None,
    ):
        self.db = database
        global tornado_settings
        tornado_settings = given_tornado_settings
        super(LandingApplication, self).__init__(
            self.get_handlers(database, hostname, password), **tornado_settings
        )

    def get_handlers(self, database, hostname=DEFAULT_HOSTNAME, password="LetsPlay"):
        return [
            (r"/", LandingHandler, {"database": database}),
            (r"/#(.*)", LandingHandler, {"database": database}),
            (r"/#/login", LandingHandler, {"database": database}),
            (r"/#/error", NotFoundHandler, {"database": database}),
            (
                r"/preauth/(.*)/(.*)/(.*)/",
                PreauthGameHandler,
                {"database": database, "hostname": hostname},
            ),
            (r"/play", GameHandler, {"database": database}),
            (r"/play/?id=.*", GameHandler, {"database": database}),
            (r"/play/*", GameHandler, {"database": database}),
            (r"/build", BuildHandler, {"database": database}),
            (
                r"/login",
                LoginHandler,
                {"database": database, "hostname": hostname, "password": password},
            ),
            (
                r"/auth/fblogin",
                FacebookOAuth2LoginHandler,
                {"database": database, "hostname": hostname, "app": self},
            ),
            (r"/logout", LogoutHandler, {"database": database}),
            (
                r"/terms",
                StaticPageHandler,
                {"database": database, "target": "/html/terms.html"},
            ),
            (
                r"/#/bye",
                LandingHandler,
                {"database": database},
            ),
            (
                r"/about",
                StaticLoggedInPageHandler,
                {"database": database, "target": "/html/about.html"},
            ),
            (
                r"/profile",
                StaticLoggedInPageHandler,
                {"database": database, "target": "/html/profile.html"},
            ),
            (r"/report", ReportHandler, {"database": database}),
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
        database,
        hostname=DEFAULT_HOSTNAME,
    ):
        self.db = database
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
            with self.db as ldb:
                _ = ldb.create_user(hashed_user_id)
            self.set_secure_cookie(
                "preauth",
                tornado.escape.json_encode(hashed_user_id),
                expires_days=1,
                domain=self.hostname,
                httponly=True,
            )
            self.set_secure_cookie(
                "preauth_context",
                tornado.escape.json_encode(context_id),
                expires_days=1,
                domain=self.hostname,
                httponly=True,
            )
            self.set_secure_cookie(
                "context_token",
                tornado.escape.json_encode(context_hash),
                expires_days=1,
                domain=self.hostname,
                httponly=True,
            )
            self.render(here + "/../build/game.html")
        else:
            self.redirect("/#/error")


class NotFoundHandler(BaseHandler):
    def get(self):
        self.redirect("/#/error")


class StaticPageHandler(BaseHandler):
    def initialize(self, target, database):
        self.target_page = here + target
        self.db = database

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
        database,
        hostname,
        app,
    ):
        self.app = app
        self.db = database
        self.hostname = hostname

    async def get(self):
        redirect = "https://" + self.request.host + "/auth/fblogin"
        if self.get_argument("code", False):
            fb_user = await self.get_authenticated_user(
                redirect_uri=redirect,
                client_id=self.app.settings["facebook_api_key"],
                client_secret=self.app.settings["facebook_secret"],
                code=self.get_argument("code"),
            )
            self.set_current_user(fb_user["id"])
            self.redirect("/play/")
            return
        self.authorize_redirect(
            redirect_uri=redirect,
            client_id=self.app.settings["facebook_api_key"],
        )

    def set_current_user(self, user):
        if user:
            with self.db as ldb:
                _ = ldb.create_user(user)
            self.set_secure_cookie(
                "user",
                tornado.escape.json_encode(user),
                domain=self.hostname,
                secure=True,
                httponly=True,
            )
        else:
            self.clear_cookie("user")


class LoginHandler(BaseHandler):
    def initialize(
        self,
        database,
        hostname=DEFAULT_HOSTNAME,
        password="LetsPlay",
    ):
        self.db = database
        self.hostname = hostname
        self.password = password

    def get(self):
        self.render(here + "/build/index.html", next=self.get_argument("next", "/"))
        self.next = next

    def post(self):
        name = self.get_argument("name", "")
        password = self.get_argument("password", "")
        if password == self.password:
            with self.db as ldb:
                _ = ldb.create_user(name)
            self.set_current_user(name)
            # self.redirect(self.get_argument("next", "/"))
            self.redirect("/play/")
        else:
            error_msg = "?error=" + tornado.escape.url_escape("incorrect")
            self.redirect("/#/login" + error_msg)

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie(
                "user",
                tornado.escape.json_encode(user),
                domain=self.hostname,
                # secure=True, login handler is for local testing
                httponly=True,
            )
        else:
            self.clear_cookie("user")


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
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

    def __init__(self, socket, purgatory, db=None, user=None, context=None):
        self.socket = socket
        self.player_soul = None
        self.purgatory = purgatory
        if quest_loader is not None:
            self.quest_loader = quest_loader
        socket.set_player(self)
        socket.send_alive()
        self.db = db
        self.user = user
        self.context = context
        # TODO a TornadoPlayerProvider refactor is likely desired, combining
        # the APIs for socket and HTTP requests to use logged in user
        # and their state in the world at the same time.
        self.app = socket.app
        self.app.world = purgatory.world

    def register_soul(self, soul: "PlayerSoul"):
        """Save the soul as a local player soul"""
        self.player_soul = soul
        if self.user is not None:
            if self.db is not None:
                with self.db as ldb:
                    ldb.initialize_agent_score(soul.target_node, self.user)
            self.app.user_node_map[self.user] = soul.target_node

    def player_observe_event(self, soul: "PlayerSoul", event: "GraphEvent"):
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
            self.purgatory.clear_soul(soul.target_node)

    def act(self, action_data, event_id: Optional[str] = None):
        if self.player_soul is not None and self.player_soul.is_reaped:
            self.player_soul = None
        if self.player_soul is None:
            self.init_soul()
            return
        player_agent = self.player_soul.handle_act(action_data, event_id)

    def init_soul(self):
        self.purgatory.get_soul_for_player(self)
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
            self.player_soul.handle_act("look")
            self.player_soul.target_node.user_id = self.user
            self.player_soul.target_node.context_id = self.context

    def is_alive(self):
        return self.socket.alive

    def on_reap_soul(self, soul):
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
        if self.user is not None:
            if self.db is not None and not isinstance(soul, TutorialPlayerSoul):
                with self.db as ldb:
                    ldb.store_agent_score(soul.target_node, self.user)
            self.app.user_node_map[self.user] = None


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
        db=None,
        listening=False,
        given_tornado_settings=None,
    ):
        self.registry = registry
        self.app = None
        self.db = db

        def _run_server():
            nonlocal listening
            nonlocal self
            nonlocal hostname
            nonlocal port
            self.my_loop = ioloop.IOLoop()
            self.app = Application(
                given_tornado_settings=given_tornado_settings, db=self.db
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

    init_safety_classifier(os.path.expanduser("~/data/safety/OffensiveLanguage.txt"))

    random.seed(6)
    numpy.random.seed(6)

    if FLAGS.no_game_instance:
        provider = TornadoPlayerFactory(
            None, FLAGS.hostname, FLAGS.port, listening=True
        )
    else:
        game = GameInstance(game_id=0, ldb=ldb)
        graph = game.world
        provider = TornadoPlayerFactory(
            graph, FLAGS.hostname, FLAGS.port, db=ldb, listening=True
        )
        game.register_provider(provider)
        game.run_graph()


if __name__ == "__main__":
    main()
