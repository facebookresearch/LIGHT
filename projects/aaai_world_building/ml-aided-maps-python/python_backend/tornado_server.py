# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from parlai.core.params import ParlaiParser
from parlai.core.agents import create_agent, create_agent_from_shared
from parlai_internal.tasks.light_maps.builder import load_world_db
from parlai_internal.projects.light.light_maps.html_map import generate_html_map
from parlai_internal.projects.light.light_maps.filler_rooms import build_filler_rooms
import parlai_internal.projects.light.v1.graph as graph

import argparse
import copy
import inspect
import json
import os
import logging
import threading
import time
import traceback
import uuid
import warnings
import random

import psycopg2

from zmq.eventloop import ioloop

ioloop.install()  # Needs to happen before any tornado imports!

import tornado.ioloop  # noqa E402: gotta install ioloop first
import tornado.web  # noqa E402: gotta install ioloop first
import tornado.websocket  # noqa E402: gotta install ioloop first
import tornado.escape  # noqa E402: gotta install ioloop first

DATABASE_URL = os.environ["DATABASE_URL"]
INSERT_NEW_ENTRY_SQL = """INSERT INTO entries(entry_data)
VALUES(%s) RETURNING entry_id;"""


class ModelProvider:
    def __init__(self):
        parser = ParlaiParser(True, True, "blah")
        parser.add_argument(
            "--light-model-root",
            type=str,
            default="/app/models/",
            # default="/Users/jju/Desktop/ml-aided-maps-python/models/",
            help="models path. For local setup, use: /checkpoint/jase/projects/light/dialog/",
        )
        parser.add_argument(
            "--light-db-file",
            type=str,
            default="",
            help="specific path for db pickle to override the path",
        )
        self.opt, _unknown = parser.parse_and_process_known_args()
        self.dpath = self.opt["datapath"] + "/light_maps"

        if self.opt.get("light_db_file", "") != "":
            env_file = self.opt.get("light_db_file")
            print("loading specified db: " + env_file)
            with open(env_file, "rb") as picklefile:
                self.db = pickle.load(picklefile)
        else:
            self.db = load_world_db(opt=self.opt)

        self.load_models()

    def load_models(self):
        # load model
        # TODO load from zoo
        print("loading models!")
        opt = copy.deepcopy(self.opt)
        LIGHT_MODEL_ROOT = opt["light_model_root"]
        mf = LIGHT_MODEL_ROOT + "angela_starspace/model4"
        opt["model_file"] = mf
        self.agents = {}
        opt["fixed_candidates_file"] = self.dpath + "/room_full_cands.txt"
        opt["override"] = {
            "fixed_candidates_file": opt["fixed_candidates_file"],
            #'dict_file': '/Users/jju/Desktop/LIGHT_maps/model.dict',
        }
        self.agents["room"] = create_agent(opt, requireModelExists=True)
        opt = self.agents["room"].opt.copy()
        opt["fixed_candidates_file"] = self.dpath + "/object_full_cands.txt"
        opt["override"] = {
            "fixed_candidates_file": opt["fixed_candidates_file"],
            #'dict_file': '/Users/jju/Desktop/LIGHT_maps/model.dict',
        }
        share_dict = self.agents["room"].share()
        share_dict["opt"] = opt
        self.agents["object"] = create_agent_from_shared(share_dict)
        opt = self.agents["room"].opt.copy()
        opt["fixed_candidates_file"] = self.dpath + "/character_full_cands.txt"
        opt["override"] = {
            "fixed_candidates_file": opt["fixed_candidates_file"],
            #'dict_file': '/Users/jju/Desktop/LIGHT_maps/model.dict',
        }
        share_dict = self.agents["room"].share()
        share_dict["opt"] = opt
        self.agents["character"] = create_agent_from_shared(share_dict)
        print("models loaded!")

    def get_neighbor_rooms(self, room_id, num_results=5, banned_rooms=None):
        # Get prediction from StarSpace model.
        if banned_rooms is None:
            banned_rooms = [room_id]
        db = self.db
        txt_feats = db["id_to_roomfeats"][room_id]
        self.agents["room"].reset()
        msg = {"text": txt_feats, "episode_done": True}
        self.agents["room"].observe(msg)
        response = self.agents["room"].act()
        ind = 0
        results = []
        while len(results) < num_results:
            key = response["text_candidates"][ind]
            if key in self.db["roomfeats_to_id"]:
                rind = self.db["roomfeats_to_id"][key]
                if rind not in banned_rooms:
                    results.append(self.db["rooms"][rind])
            ind = ind + 1
            if len(response["text_candidates"]) <= ind:
                if len(results) == 0:
                    return None
                else:
                    return results
        return results

    def get_contained_items(self, room_id, num_results=5, banned_items=[]):
        # Get prediction from StarSpace model.
        db = self.db
        txt_feats = db["id_to_roomfeats"][room_id]
        self.agents["object"].reset()
        msg = {"text": txt_feats, "episode_done": True}
        self.agents["object"].observe(msg)
        response = self.agents["object"].act()
        ind = 0
        results = []
        while len(results) < num_results:
            key = response["text_candidates"][ind]
            if "{{}}" in key:
                ind = ind + 1
                continue
            if key in self.db["objectfeats_to_id"]:
                oid = self.db["objectfeats_to_id"][key]
                if oid not in banned_items:
                    results.append(self.db["objects"][oid])
            ind = ind + 1
            if len(response["text_candidates"]) <= ind:
                if len(results) == 0:
                    return None
                else:
                    return results
        return results

    def get_contained_characters(self, room_id, num_results=5, banned_characters=[]):
        # Get prediction from StarSpace model.
        db = self.db
        txt_feats = db["id_to_roomfeats"][room_id]
        self.agents["character"].reset()
        msg = {"text": txt_feats, "episode_done": True}
        self.agents["character"].observe(msg)
        response = self.agents["character"].act()
        ind = 0
        results = []
        while len(results) < num_results:
            key = response["text_candidates"][ind]
            if "wench" in key:
                ind = ind + 1
                continue
            if key in self.db["characterfeats_to_id"]:
                cind = self.db["characterfeats_to_id"][key]
                if cind not in banned_characters:
                    results.append(self.db["characters"][cind])
            ind = ind + 1
            if len(response["text_candidates"]) <= ind:
                if len(results) == 0:
                    return None
                else:
                    return results
        return results


DEFAULT_PORT = 35496
DEFAULT_HOSTNAME = "localhost"

here = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
save_path = os.path.join(here, "saved_data")

_seen_warnings = set()


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


ensure_dir_exists(save_path)


def get_path(filename):
    """Get the path to an asset."""
    cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    return os.path.join(cwd, filename)


tornado_settings = {
    "autoescape": None,
    "debug": "/dbg/" in __file__,
    "static_path": get_path("static"),
    "template_path": get_path("static"),
    "compiled_template_cache": False,
}


class Application(tornado.web.Application):
    def __init__(self, port):
        self.port = port
        self.model_wrapper = ModelProvider()
        tornado_settings["static_url_prefix"] = "/static/"
        handlers = [
            (r"/query", QueryModelHandler, {"app": self}),
            (r"/submit", SubmitMapHandler, {"app": self}),
        ]
        super(Application, self).__init__(handlers, **tornado_settings)


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *request, **kwargs):
        self.include_host = False
        super(BaseHandler, self).__init__(*request, **kwargs)

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

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


class QueryModelHandler(BaseHandler):
    """Handler that initializes models to respond to queries, then responds to
    queries in the form of get requests"""

    def initialize(self, app):
        self.app = app
        self.model_wrapper = app.model_wrapper

    def guess_rooms(self, state, walls):
        """Fill in missing rooms in a grid with guesses"""

        rooms = {
            "1": {"given": state[0][0], "guesses": [], "check_rooms": []},
            "2": {"given": state[0][1], "guesses": [], "check_rooms": []},
            "3": {"given": state[0][2], "guesses": [], "check_rooms": []},
            "4": {"given": state[1][0], "guesses": [], "check_rooms": []},
            "5": {"given": state[1][1], "guesses": [], "check_rooms": []},
            "6": {"given": state[1][2], "guesses": [], "check_rooms": []},
            "7": {"given": state[2][0], "guesses": [], "check_rooms": []},
            "8": {"given": state[2][1], "guesses": [], "check_rooms": []},
            "9": {"given": state[2][2], "guesses": [], "check_rooms": []},
        }
        WALL_PAIRS = [
            ("1", "2"),
            ("2", "3"),
            ("1", "4"),
            ("2", "5"),
            ("3", "6"),
            ("4", "5"),
            ("5", "6"),
            ("4", "7"),
            ("5", "8"),
            ("6", "9"),
            ("7", "8"),
            ("8", "9"),
        ]
        # Construct the rooms to check connections between based on given walls
        for wall_num, wall in enumerate(walls):
            if not wall:
                wall_pair = WALL_PAIRS[wall_num]
                rooms[wall_pair[0]]["check_rooms"].append(wall_pair[1])
                rooms[wall_pair[1]]["check_rooms"].append(wall_pair[0])

        max_attempts = 10
        all_done = False
        while max_attempts > 0 and not all_done:
            max_attempts -= 1
            all_done = True
            for room in rooms.values():
                if room["given"] is not None:
                    continue
                elif room["given"] is None and len(room["guesses"]) == 0:
                    this_done = len(room["check_rooms"]) == 0
                    for check_room_cand in room["check_rooms"]:
                        check_room = rooms[check_room_cand]
                        if check_room["given"] is not None:
                            guesses = self.model_wrapper.get_neighbor_rooms(
                                check_room["given"]
                            )
                            if guesses is not None:
                                room["guesses"] += guesses
                                this_done = True
                        elif len(check_room["guesses"]) != 0:
                            guesses = self.model_wrapper.get_neighbor_rooms(
                                random.choice(check_room["guesses"])["room_id"]
                            )
                            if guesses is not None:
                                room["guesses"] += guesses
                                this_done = True
                    if not this_done:
                        all_done = False

        if max_attempts == 0:
            print("something happened, resetting models")
            self.model_wrapper = ModelProvider()

        for room in rooms.values():
            del room["check_rooms"]
            room["rooms"] = list(
                set([r["room_id"] for r in room["guesses"] if r["room_id"] != 305])
            )[:6]
            del room["guesses"]

        return rooms

    def guess_contents(self, room_guesses):
        for room in room_guesses.values():
            use_room = room["given"]
            del room["given"]
            if use_room is None:
                continue
            room["characters"] = self.model_wrapper.get_contained_characters(use_room)
            room["objects"] = self.model_wrapper.get_contained_items(use_room)
            room["characters"] = list(
                set(c["character_id"] for c in room["characters"])
            )
            room["objects"] = list(set(c["object_id"] for c in room["objects"]))
        return room_guesses

    def get(self):
        """Return a set of model queries for the given """
        state = self.get_argument("state", None)
        if state is None:
            self.write(
                json.dumps(
                    {
                        "1": {"rooms": []},
                        "2": {"rooms": []},
                        "3": {"rooms": []},
                        "4": {"rooms": []},
                        "5": {"rooms": []},
                        "6": {"rooms": []},
                        "7": {"rooms": []},
                        "8": {"rooms": []},
                        "9": {"rooms": []},
                    }
                )
            )
            return
        state = json.loads(state)
        walls = self.get_argument("connections", "[0,0,0,0,0,0,0,0,0,0,0,0]")
        walls = json.loads(walls)
        room_guesses = self.guess_rooms(state, walls)
        content_guesses = self.guess_contents(room_guesses)
        final_guesses = {"suggestions": content_guesses}
        self.write(json.dumps(final_guesses))


class SubmitMapHandler(BaseHandler):
    """Handler that initializes models to respond to queries, then responds to
    queries in the form of get requests"""

    def initialize(self, app):
        self.app = app

    def post(self):
        req = tornado.escape.json_decode(
            tornado.escape.to_basestring(self.request.body)
        )
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        cur = conn.cursor()
        cur.execute(INSERT_NEW_ENTRY_SQL, (json.dumps(req),))
        conn.commit()
        cur.close()
        conn.close()
        file_name = f'{req.get("rand_id", "testing")}.json'
        path_name = os.path.join(save_path, file_name)
        with open(path_name, "w+") as json_file:
            json.dump(req, json_file)
        self.write(json.dumps({"success": True}))


def start_server(port=DEFAULT_PORT, hostname=DEFAULT_HOSTNAME):
    print("It's Alive!")
    app = Application(port=port)
    app.listen(port, max_buffer_size=1024 ** 3)
    logging.info("Application Started")

    if "HOSTNAME" in os.environ and hostname == DEFAULT_HOSTNAME:
        hostname = os.environ["HOSTNAME"]
    else:
        hostname = hostname
    print("You can send requests to http://%s:%s" % (hostname, port))
    ioloop.IOLoop.instance().start()


def main():
    import numpy
    import random

    parser = argparse.ArgumentParser(description="Start the tornado server.")
    parser.add_argument(
        "--light-model-root",
        type=str,
        default="/Users/jju/Desktop/LIGHT/LIGHT_models",
        help="models path. For local setup, use: /checkpoint/jase/projects/light/dialog/",
    )
    parser.add_argument(
        "-port",
        metavar="port",
        type=int,
        default=DEFAULT_PORT,
        help="port to run the server on.",
    )
    parser.add_argument(
        "--hostname",
        metavar="hostname",
        type=str,
        default=DEFAULT_HOSTNAME,
        help="host to run the server on.",
    )
    FLAGS = parser.parse_args()

    random.seed(6)
    numpy.random.seed(6)

    start_server(port=FLAGS.port, hostname=FLAGS.hostname)


if __name__ == "__main__":
    main()
