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
from light.data_model.light_database import LIGHTDatabase
from light.world.player_provider import PlayerProvider
from light.world.quest_loader import QuestLoader
from light.graph.events.graph_events import init_safety_classifier

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
from collections import defaultdict
from zmq.eventloop import ioloop

ioloop.install()  # Needs to happen before any tornado imports!

import tornado.ioloop  # noqa E402: gotta install ioloop first
import tornado.web  # noqa E402: gotta install ioloop first
import tornado.auth  # noqa E402: gotta install ioloop first
import tornado.websocket  # noqa E402: gotta install ioloop first
import tornado.escape  # noqa E402: gotta install ioloop first
from light.graph.events.graph_events import SoulSpawnEvent

DEFAULT_PORT = 35496
DEFAULT_HOSTNAME = "localhost"
QUESTS_LOCATION = "/home/ubuntu/data/quests"
if QUESTS_LOCATION is not None and os.path.exists(QUESTS_LOCATION):
    quest_loader = QuestLoader(QUESTS_LOCATION)
else:
    quest_loader = None
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
    def __init__(self, given_tornado_settings=None):
        global tornado_settings
        use_tornado_settings = tornado_settings
        if given_tornado_settings is not None:
            use_tornado_settings = given_tornado_settings
        self.subs = {}
        self.new_subs = defaultdict(list)
        super(Application, self).__init__(self.get_handlers(), **use_tornado_settings)

    def get_handlers(self):
        path_to_build = here + "/../build/"
        # NOTE: We choose to keep the StaticUIHandler, despite this handler never being
        #       hit in the top level RuleRouter from run_server.py in case this application
        #       is run standalone for some reason.
        return [
            (r"/game(.*)/socket", SocketHandler, {"app": self}),
            (r"/", MainHandler),
            (r"/(.*)", StaticUIHandler, {"path": path_to_build}),
        ]


# StaticUIHandler serves static front end, defaulting to index.html served
# If the file is unspecified.
class StaticUIHandler(tornado.web.StaticFileHandler):
    def parse_url_path(self, url_path):
        PRIMARY_PAGE = "index.html"
        if not url_path or url_path.endswith("/"):
            url_path = url_path + PRIMARY_PAGE
        return url_path


class SocketHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, app):
        self.app = app
        self.subs = app.subs
        self.new_subs = app.new_subs
        self.alive = True
        self.alive_sent = False
        self.actions = []
        self.player = None
        self.sid = get_rand_id()

    def safe_write_message(self, msg):
        try:
            self.write_message(msg)
        except tornado.websocket.WebSocketClosedError:
            self.alive = False

    def check_origin(self, origin):
        return True

    def set_player(self, player):
        self.player = player

    def open(self, game_id):
        user_json = self.get_secure_cookie("user")
        if user_json:
            logging.info("Opened new socket from ip: {}".format(self.request.remote_ip))
            logging.info("For game: {}".format(game_id))
            if game_id not in self.app.graphs:
                self.close()
                # TODO: Have an error page about game deleted
                self.redirect("/game/")
            graph_purgatory = self.app.graphs[game_id].g.purgatory
            if self.alive:
                new_player = TornadoPlayerProvider(
                    self,
                    graph_purgatory,
                )
                new_player.init_soul()
                self.app.graphs[game_id].players.append(new_player)
        else:
            self.close()
            self.redirect("/login")

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
            self.player.act(msg["data"])
        else:
            print("THESE COMMANDS HAVE BEEN DEPRICATED")

    def on_close(self):
        self.alive = False


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *request, **kwargs):
        self.include_host = False
        super(BaseHandler, self).__init__(*request, **kwargs)

    def get_login_url(self):
        return "/login"

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if user_json:
            return tornado.escape.json_decode(user_json)
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
            import traceback

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


class LandingApplication(tornado.web.Application):
    def __init__(
        self,
        database,
        hostname=DEFAULT_HOSTNAME,
        password="LetsPlay",
        given_tornado_settings=None,
    ):
        global tornado_settings
        tornado_settings = given_tornado_settings
        super(LandingApplication, self).__init__(
            self.get_handlers(database, hostname, password), **tornado_settings
        )

    def get_handlers(self, database, hostname=DEFAULT_HOSTNAME, password="LetsPlay"):
        return [
            (r"/", MainHandler),
            (r"/?id=.*", MainHandler),
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
            (r"/logout", LogoutHandler),
            (r"/report", ReportHandler),
            (r"/(.*)", StaticUIHandler, {"path": here + "/../build/"}),
        ]


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render(here + "/../build/index.html")


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
            self.redirect("/")
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
                "user", tornado.escape.json_encode(user), domain=self.hostname
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
        self.render(here + "/login.html", next=self.get_argument("next", "/"))
        self.next = next

    def post(self):
        name = self.get_argument("name", "")
        password = self.get_argument("password", "")
        if password == self.password:
            with self.db as ldb:
                _ = ldb.create_user(name)
            self.set_current_user(name)
            self.redirect(self.get_argument("next", "/"))
        else:
            error_msg = "?error=" + tornado.escape.url_escape("Login incorrect.")
            self.redirect("/login" + error_msg)

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie(
                "user", tornado.escape.json_encode(user), domain=self.hostname
            )
        else:
            self.clear_cookie("user")


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect("/login")


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

    def __init__(self, socket, purgatory):
        self.socket = socket
        self.player_soul = None
        self.purgatory = purgatory
        if quest_loader is not None:
            self.quest_loader = quest_loader
        socket.set_player(self)
        socket.send_alive()

    def register_soul(self, soul: "PlayerSoul"):
        """Save the soul as a local player soul"""
        self.player_soul = soul

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

    def act(self, action_data):
        if self.player_soul is not None and self.player_soul.is_reaped:
            self.player_soul = None
        if self.player_soul is None:
            self.init_soul()
            return
        player_agent = self.player_soul.handle_act(action_data)

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

    def is_alive(self):
        return self.socket.alive

    def on_reap_soul(self, soul):
        pass


class TornadoPlayerFactory:
    """
    A player provider is an API for adding new players into the game. It
    will be given opportunities to check for new players and should return
    an array of new players during these calls
    """

    def __init__(
        self,
        graphs,
        hostname=DEFAULT_HOSTNAME,
        port=DEFAULT_PORT,
        listening=False,
        given_tornado_settings=None,
    ):
        self.graphs = graphs
        self.app = None

        def _run_server():
            nonlocal listening
            nonlocal self
            nonlocal hostname
            nonlocal port
            self.my_loop = ioloop.IOLoop()
            self.app = Application(given_tornado_settings=given_tornado_settings)
            self.app.graphs = self.graphs
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
        game = GameInstance()
        graph = game.g
        provider = TornadoPlayerFactory(
            graph, FLAGS.hostname, FLAGS.port, listening=True
        )
        game.register_provider(provider)
        game.run_graph()


if __name__ == "__main__":
    main()
