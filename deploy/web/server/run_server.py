#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from deploy.web.server.tornado_server import LandingApplication
from deploy.web.server.builder_server import (
    BuildApplication,
    get_handlers,
)
from deploy.web.server.registry import RegistryApplication
from tornado.routing import (
    PathMatches,
    Rule,
    RuleRouter,
)
from light.world.souls.base_soul import BaseSoul
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import inspect
import os.path
from light.data_model.light_database import LIGHTDatabase
from light.graph.events.graph_events import init_safety_classifier
from light.world.souls.models.generative_heuristic_model_soul import (
    GenerativeHeuristicModelSoul,
)

here = os.path.abspath(os.path.dirname(__file__))


def get_path(filename):
    """Get the path to an asset."""
    cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    return os.path.join(cwd, filename)


def read_secrets():
    """
    Reads the secrets from a secret text file, located outside the repo.
    The secrets should have the facebook api key, secret, and the cookie secret.
    """
    loc = here + "/../../../../secrets.txt"
    secrets = {}
    if not os.path.exists(loc):
        return {
            "cookie_secret": "0123456789",
        }
    with open(loc, "r") as secret_file:
        for line in secret_file:
            items = line.split(" ")
            if len(items) == 2:
                secrets[items[0]] = items[1].strip()
    return secrets


SECRETS = read_secrets()

tornado_settings = {
    "autoescape": None,
    "cookie_secret": SECRETS["cookie_secret"],
    "compiled_template_cache": False,
    "debug": "/dbg/" in __file__,
    "login_url": "/login",
    "template_path": get_path("static"),
}

if "facebook_api_key" in SECRETS:
    tornado_settings["facebook_api_key"] = SECRETS["facebook_api_key"]
if "facebook_secret" in SECRETS:
    tornado_settings["facebook_secret"] = SECRETS["facebook_secret"]


def make_app(FLAGS, ldb, model_resources):
    worldBuilderApp = BuildApplication(get_handlers(ldb), tornado_settings)
    landingApp = LandingApplication(
        ldb, FLAGS.hostname, FLAGS.password, tornado_settings
    )
    registryApp = RegistryApplication(FLAGS, ldb, model_resources, tornado_settings)
    rules = []
    if FLAGS.disable_builder is None:
        rules.append(Rule(PathMatches("/builder.*"), worldBuilderApp))
    rules += [
        Rule(PathMatches("/game.*"), registryApp),
        Rule(PathMatches("/.*"), landingApp),
    ]

    router = RuleRouter(rules)
    server = HTTPServer(router)
    server.listen(FLAGS.port)
    return registryApp


def start_default_game(ldb, registryApp):
    _ = registryApp.run_new_game("", ldb)


def _run_server(FLAGS, ldb, model_resources):
    my_loop = IOLoop.current()
    registry_app = make_app(FLAGS, ldb, model_resources)
    my_loop.call_later(1, start_default_game, ldb, registry_app)

    print(
        "\nYou can connect to the game at http://%s:%s/" % (FLAGS.hostname, FLAGS.port)
    )
    print(
        "You can connect to the worldbuilder at http://%s:%s/builder/ \n"
        % (FLAGS.hostname, FLAGS.port)
    )
    try:
        my_loop.start()
    except KeyboardInterrupt:
        my_loop.stop()


# Update this to load _all_ models for the full game, fix "shared_model_content"
def init_model_resources(FLAGS):
    light_model_root = FLAGS.light_model_root
    dialog_model = FLAGS.dialog_model
    act_model = FLAGS.acting_model
    scoring_model = FLAGS.roleplaying_score_model_file
    generic_act_model = FLAGS.generic_act_model_file

    if dialog_model is None:
        return {"shared_model_content": {}}

    # dialog gen is at `dialog_gen`, other is at `game_speech1`?
    shared_model_content = GenerativeHeuristicModelSoul.load_models(
        light_model_root + dialog_model,
    )
    resources = {"shared_model_content": shared_model_content}

    if scoring_model is not None:
        resources["rpg_model"] = BaseSoul.load_roleplaying_score_model(scoring_model)
        shared_model_content["rpg_model"] = resources["rpg_model"]

    if generic_act_model is not None:
        generic_act_model_content = BaseSoul.load_generic_act_model(generic_act_model)
        resources["generic_act_model"] = generic_act_model_content.share()
        shared_model_content["shared_action_model"] = resources["generic_act_model"]

    init_safety_classifier(FLAGS.safety_list)

    return resources


def main():
    import argparse
    import numpy
    import random

    DEFAULT_PORT = 35494
    DEFAULT_HOSTNAME = "localhost"

    parser = argparse.ArgumentParser(
        description="Start the game server.", fromfile_prefix_chars="@"
    )
    parser.add_argument(
        "--cookie-secret",
        type=str,
        default="0123456789",
        help="Cookie secret for issueing cookies (SECRET!!!)",
    )
    parser.add_argument(
        "--data-model-db",
        type=str,
        default=here + "/../../../light/data_model/database.db",
        help="Databse path for the datamodel",
    )
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
        default="/checkpoint/light/models/",
        help="Models path",
    )
    parser.add_argument(
        "--password",
        type=str,
        default="LetsPlay",
        help="password for users to access the game.",
    )
    parser.add_argument(
        "--port",
        metavar="port",
        type=int,
        default=DEFAULT_PORT,
        help="port to run the server on.",
    )
    parser.add_argument(
        "--safety-list",
        metavar="safety_list",
        type=str,
        default=os.path.expanduser("~/data/safety/OffensiveLanguage.txt"),
        help="Where to find the offensive language list.",
    )
    parser.add_argument(
        "--builder-model",
        metavar="builder_model",
        type=str,
        default=None,
        help="Builder model to be loading",
    )
    parser.add_argument(
        "--dialog-model",
        metavar="dialog_model",
        type=str,
        default=None,
        help="dialog model to be loading",
    )
    parser.add_argument(
        "--acting-model",
        metavar="acting_model",
        type=str,
        default=None,
        help="acting model to be loading",
    )
    parser.add_argument(
        "--disable-builder",
        metavar="disable_builder",
        type=str,
        default=None,
        help="flag to disable the builder, omit to enable",
    )
    parser.add_argument(
        "--parser-model-file",
        type=str,
        default="",
    )
    parser.add_argument(
        "--roleplaying-score-model-file",
        type=str,
        default="",
    )
    parser.add_argument(
        "--generic-act-model-file",
        type=str,
        default="",
    )
    FLAGS, _unknown = parser.parse_known_args()

    print(FLAGS)

    random.seed(6)
    numpy.random.seed(6)
    model_resources = init_model_resources(FLAGS)
    ldb = LIGHTDatabase(FLAGS.data_model_db)
    _run_server(FLAGS, ldb, model_resources)


if __name__ == "__main__":
    main()
