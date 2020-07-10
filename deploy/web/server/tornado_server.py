#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from deploy.web.server.game_instance import (
    Player,
    PlayerProvider,
    GameInstance,
)
from light.data_model.light_database import LIGHTDatabase

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

from zmq.eventloop import ioloop
ioloop.install()  # Needs to happen before any tornado imports!

import tornado.ioloop     # noqa E402: gotta install ioloop first
import tornado.web        # noqa E402: gotta install ioloop first
import tornado.websocket  # noqa E402: gotta install ioloop first
import tornado.escape     # noqa E402: gotta install ioloop first

DEFAULT_PORT = 35496
DEFAULT_HOSTNAME = "localhost"
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
    cwd = os.path.dirname(
        os.path.abspath(inspect.getfile(inspect.currentframe())))
    return os.path.join(cwd, filename)

tornado_settings = {
    "autoescape": None,
    "cookie_secret": "0123456789", #TODO: Placeholder, do not include in repo when deploy!!!
    "compiled_template_cache": False,
    "debug": "/dbg/" in __file__,
    "login_url": "/login",
    "template_path": get_path('static'),
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
            (r"/game/socket", SocketHandler, {'app': self}),
            (r"/", MainHandler),
            (r"/(.*)", StaticUIHandler, {'path': path_to_build}),
        ]

'''
class WorldHandler(BaseHandler):
    'Load a world given the player id and world id'

    def initialize(self, dbpath):
        self.dbpath = dbpath

    @tornado.web.authenticated
    def get(self):
        with LIGHTDatabase(self.dbpath) as db:
            id = int(self.get_argument('id'))
            player = self.get_argument("player", None, True)
            # TODO: Implement this method - load the world for the wordlbuilder
            world = db.get_world(id=id, player_id=player)
            # Want to write the world name and ids.  Then, load it into game instance somehow...
            self.write(json.dumps(world))
'''

# StaticUIHandler serves static front end, defaulting to index.html served
# If the file is unspecified.
class StaticUIHandler(tornado.web.StaticFileHandler):
    def parse_url_path(self, url_path):
        PRIMARY_PAGE='index.html'
        if not url_path or url_path.endswith('/'):
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

    def open(self):
        user_json = self.get_secure_cookie("user")
        if user_json:
            if self not in list(self.subs.values()):
                self.subs[self.sid] = self
            logging.info(
                'Opened new socket from ip: {}'.format(self.request.remote_ip))
            self.new_subs.append(self.sid)
        else:
            self.close()
            self.redirect(u"/login")
        
        
    def send_alive(self):
        self.safe_write_message(
            json.dumps({'command': 'register', 'data': self.sid}))
        self.alive_sent = True


    def on_message(self, message):
        logging.info('from web client: {}'.format(message))
        msg = tornado.escape.json_decode(tornado.escape.to_basestring(message))
        cmd = msg.get('command')
        if self.player is None:
            return
        if cmd == 'act':
            # self.actions.append(msg['data'])
            self.player.g.parse_exec(self.player.get_agent_id(), msg['data'])
            self.player.observe()
        elif cmd == 'descs':
            self.safe_write_message(
                json.dumps({'command': 'descs', 'data': self.g._node_to_desc})
            )
        elif cmd == 'contains':
            queries = msg['data']
            self.safe_write_message(
                json.dumps({
                    'command': 'contains',
                    'data': {q : list(self.g.node_contains) for q in queries}
                })
            )
        elif cmd == 'attributes':
            queries = msg['data']
            self.safe_write_message(
                json.dumps({
                    'command': 'contains',
                    # TODO expose a way in graph to get all props for a node
                    'data': {q : list(self.g._node_to_props) for q in queries}
                })
            )

    def on_close(self):
        if self.player is not None:
            self.player.g.clear_message_callback(self.player.get_player_id())
        self.alive = False


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *request, **kwargs):
        self.include_host = False
        super(BaseHandler, self).__init__(*request, **kwargs)
    
    def get_login_url(self):
        return u"/login"

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if user_json:
            return tornado.escape.json_decode(user_json)
        else:
            return None

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')

    # TODO maybe use cookies to restore previous game state?
    def write_error(self, status_code, **kwargs):
        logging.error("ERROR: %s: %s" % (status_code, kwargs))
        if "exc_info" in kwargs:
            logging.info('Traceback: {}'.format(
                traceback.format_exception(*kwargs["exc_info"])))
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
                    'error': exc_info[1],
                    'trace_info': traceback.format_exception(*exc_info),
                    'request': self.request.__dict__
                }

                self.render("error.html", **params)
                logging.error("rendering complete")
            except Exception as e:
                logging.error(e)

class LandingApplication(tornado.web.Application):
    def __init__(self, dbpath, hostname=DEFAULT_HOSTNAME, password="LetsPlay"):
        super(LandingApplication, self).__init__(self.get_handlers(dbpath, hostname, password), **tornado_settings)

    def get_handlers(self, dbpath, hostname=DEFAULT_HOSTNAME, password="LetsPlay"):
        return [
            (r"/", MainHandler),
            (r"/login", LoginHandler, {'dbpath': dbpath, 'hostname' : hostname, 'password': password}),
            (r"/logout", LogoutHandler),
            (r"/(.*)", StaticUIHandler, {'path' : here + "/../build/"})
        ]

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render(here + "/../build/index.html")

       
class LoginHandler(BaseHandler):
    def initialize(self, dbpath, hostname=DEFAULT_HOSTNAME, password="LetsPlay", ):
        self.dbpath = dbpath
        self.hostname = hostname
        self.password = password

    def get(self):
        self.render(here + "/login.html", next=self.get_argument("next", u"/"))
        self.next = next

    def post(self):
        name = self.get_argument("name", "")
        password = self.get_argument("password", "")
        if password == self.password:
            with LIGHTDatabase(self.dbpath) as db:
                _ = db.create_user(name)
            self.set_current_user(name)
            self.redirect(self.get_argument("next", u"/"))
        else:
            error_msg = u"?error=" + tornado.escape.url_escape("Login incorrect.")
            self.redirect(u"/login" + error_msg)

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", tornado.escape.json_encode(user), domain=self.hostname)
        else:
            self.clear_cookie("user")

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(u"/login")

class TornadoWebappPlayer(Player):
    """
    A player in an instance of the light game. Maintains any required
    connections and IO such that the game doesn't need to worry about
    that stuff
    """

    def __init__(self, graph, player_id, socket):
        self.socket = socket
        socket.set_player(self)
        socket.send_alive()
        super().__init__(graph, player_id)
        graph.add_message_callback(player_id, self.observe)

    def act(self):
        """
        Get an action to take on the graph if one exists
        """
        if len(self.socket.actions) > 0:
            action = self.socket.actions.pop()
            print('returning action', action)
            return action
        return ''

    def observe(self, graph=None, action=None):
        """
        Get all of the discrete actions that have occurred, send them
        to the frontend with as much context as possible
        """
        if not self.socket.alive_sent:
            return  # the socket isn't alive yet, let's wait
        if graph is None:
            graph = self.g
        actions = graph.get_action_history(self.get_agent_id())
        extra_text = graph.get_text(self.get_agent_id())
        # TODO update extract_action to be more standard
        # across multiple actions?
        obs_list = [graph.extract_action(self.get_agent_id(), a) for a in actions]
        filtered_obs = [obs for obs in obs_list if obs['text'] is not None and len(obs['text'].strip())]
        if extra_text != '':
            # obs_list.append({'caller': 'text', 'text': extra_text})
            pass  # extra text is gotten through regular actions as well
        if len(filtered_obs) > 0:
            self.socket.safe_write_message(
                json.dumps({'command': 'actions', 'data': filtered_obs})
            )

    def init_observe(self):
        # TODO send own character name?
        self.g.parse_exec(self.get_agent_id(), 'look')
        self.observe()

    def is_alive(self):
        return self.socket.alive


class TornadoWebappPlayerProvider(PlayerProvider):
    """
    A player provider is an API for adding new players into the game. It
    will be given opportunities to check for new players and should return
    an array of new players during these calls
    """
    def __init__(self, graph, hostname=DEFAULT_HOSTNAME, port=DEFAULT_PORT, listening=False):
        super().__init__(graph)
        self.app = None

        def _run_server():
            nonlocal listening
            nonlocal self
            nonlocal hostname
            nonlocal port
            self.my_loop = ioloop.IOLoop()
            self.app = Application()
            if listening:
                self.app.listen(port, max_buffer_size=1024 ** 3)
                print("\nYou can connect to the game at http://%s:%s/" % (hostname, port))
                print("You can connect to the socket at http://%s:%s/game/socket/" % (hostname, port))
            logging.info("TornadoWebProvider Started")

            if "HOSTNAME" in os.environ and hostname == DEFAULT_HOSTNAME:
                hostname = os.environ["HOSTNAME"]
            else:
                hostname = hostname
            self.my_loop.start()

        self.t = threading.Thread(
            target=_run_server, name='TornadoProviderThread', daemon=True
        )
        self.t.start()
        while self.app is None:
            time.sleep(0.3)

    def get_new_players(self):
        """
        Should check the potential source of players for new players. If
        a player exists, this should instantiate a relevant Player object
        for each potential new player and return them.
        """
        new_connections = []
        while len(self.app.new_subs) > 0:
            new_connections.append(self.app.new_subs.pop())
        players = []

        for conn_name in new_connections:
            conn = self.app.subs[conn_name]
            if conn.alive:
                player_id = self.g.spawn_player()
                print("added a subscriber!: " + str(player_id))
                if player_id == -1:
                    conn.safe_write_message(
                        json.dumps({
                            'command': 'reject',
                            'data': 'Sorry, too many players are on right now!'
                        })
                    )
                else:
                    new_player = TornadoWebappPlayer(
                        self.g,
                        player_id,
                        conn,
                    )
                    players.append(new_player)
        return players


def main():
    import numpy
    import random

    parser = argparse.ArgumentParser(description='Start the tornado server.')
    parser.add_argument('--hostname', metavar='hostname', type=str,
                        default=DEFAULT_HOSTNAME,
                        help='host to run the server on.')
    parser.add_argument('--light-model-root', type=str,
                        default="/Users/jju/Desktop/LIGHT/",
                        help='models path. For local setup, use: /checkpoint/jase/projects/light/dialog/')
    parser.add_argument('--no-game-instance', action='store_true',
                        help='does not initialize game instance')
    parser.add_argument('-port', metavar='port', type=int,
                        default=DEFAULT_PORT,
                        help='port to run the server on.')
    FLAGS = parser.parse_args()

    random.seed(6)
    numpy.random.seed(6)

    if FLAGS.no_game_instance:
        provider = TornadoWebappPlayerProvider(None, FLAGS.hostname, FLAGS.port, listening=True)
    else:
        game = GameInstance()
        graph = game.g
        provider = TornadoWebappPlayerProvider(graph, FLAGS.hostname, FLAGS.port, listening=True)
        game.register_provider(provider)
        game.run_graph()


if __name__ == "__main__":
    main()
