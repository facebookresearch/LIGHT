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
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import os.path
from light.data_model.light_database import LIGHTDatabase
from light.world.souls.models.partner_heuristic_model_soul import (
    PartnerHeuristicModelSoul,
)

here = os.path.abspath(os.path.dirname(__file__))


def make_app(FLAGS, ldb, model_resources):
    worldBuilderApp = BuildApplication(get_handlers(ldb))
    landingApp = LandingApplication(ldb, FLAGS.hostname, FLAGS.password)
    registryApp = RegistryApplication(FLAGS, ldb, model_resources)
    router = RuleRouter(
        [
            Rule(PathMatches("/builder.*"), worldBuilderApp),
            Rule(PathMatches("/game.*"), registryApp),
            Rule(PathMatches("/.*"), landingApp),
        ]
    )
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


# Override this to be the model_resources needed for souls
def init_model_resources(light_model_root):
    shared_model_content = PartnerHeuristicModelSoul.load_models(
        light_model_root + "dialog_gen/model",
        light_model_root + "speech_train_cands.txt",
        light_model_root + "agent_to_utterance_trainset.txt",
        light_model_root + "main_act/model",
    )
    resources = {"shared_model_content": shared_model_content}
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
    FLAGS, _unknown = parser.parse_known_args()

    random.seed(6)
    numpy.random.seed(6)
    model_resources = init_model_resources(FLAGS.light_model_root)
    ldb = LIGHTDatabase(FLAGS.data_model_db)
    _run_server(FLAGS, ldb, model_resources)


if __name__ == "__main__":
    main()
