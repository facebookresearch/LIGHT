#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

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
import os
import asyncio
from light.data_model.light_database import LIGHTDatabase
from light.data_model.db.base import LightDBConfig, LightAWSDBConfig
from light.data_model.db.episodes import EpisodeDB
from light.data_model.db.users import UserDB
from light.world.world import WorldConfig
from light.registry.model_pool import ModelPool, ModelTypeName
from light.registry.parlai_model import ParlAIModelConfig
from light.registry.parlai_remote_model import ParlAIRemoteModelConfig
from light.registry.models.acting_score_model import (
    ParlAIPolyencoderActingScoreModelConfig,
)
from light.data_model.db.base import LightDBConfig
from light.data_model.db.episodes import EpisodeDB
from light.data_model.db.users import UserDB
from light.world.world import WorldConfig
from light.registry.model_pool import ModelPool, ModelTypeName
from light.registry.parlai_model import ParlAIModelConfig
from light.registry.models.acting_score_model import (
    ParlAIPolyencoderActingScoreModelConfig,
)

from light import LIGHT_DIR

CONFIG_DIR = os.path.join(LIGHT_DIR, "light/registry/models/config")

from light import LIGHT_DIR

CONFIG_DIR = os.path.join(LIGHT_DIR, "light/registry/models/config")

from light import LIGHT_DIR

CONFIG_DIR = os.path.join(LIGHT_DIR, "light/registry/models/config")

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
            "preauth_secret": "0123456789",
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
    "preauth_secret": SECRETS["preauth_secret"],
    "template_path": get_path("static"),
}

if "facebook_api_key" in SECRETS:
    tornado_settings["facebook_api_key"] = SECRETS["facebook_api_key"]
if "facebook_secret" in SECRETS:
    tornado_settings["facebook_secret"] = SECRETS["facebook_secret"]


def make_app(FLAGS, ldb, model_pool: ModelPool):
    worldBuilderApp = BuildApplication(get_handlers(ldb), tornado_settings)
    db_config = LightDBConfig(backend=FLAGS.db_backend, file_root=FLAGS.db_root)
    episode_db = EpisodeDB(db_config)
    user_db = UserDB(db_config)
    landingApp = LandingApplication(
        user_db=user_db,
        hostname=FLAGS.hostname,
        password=FLAGS.password,
        given_tornado_settings=tornado_settings,
    )
    registryApp = RegistryApplication(
        FLAGS,
        ldb,
        model_pool,
        tornado_settings,
        episode_db=episode_db,
        user_db=user_db,
    )
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


async def _run_server(FLAGS, ldb, model_resources):
    registry_app = make_app(FLAGS, ldb, model_resources)
    _ = await registry_app.run_new_game("", ldb)

    print(
        "\nYou can connect to the game at http://%s:%s/" % (FLAGS.hostname, FLAGS.port)
    )
    print(
        "You can connect to the worldbuilder at http://%s:%s/builder/ \n"
        % (FLAGS.hostname, FLAGS.port)
    )
    while True:
        await asyncio.sleep(30)


def init_model_pool(FLAGS) -> "ModelPool":
    light_model_root = FLAGS.light_model_root
    if light_model_root.endswith("/"):
        light_model_root = os.path.expanduser(light_model_root[:-1])
    os.environ["LIGHT_MODEL_ROOT"] = light_model_root

    safety_model_opt_file = FLAGS.safety_model_opt_file.replace(
        "LIGHT_MODEL_ROOT", light_model_root
    )
    dialog_model_opt_file = FLAGS.dialog_model_opt_file.replace(
        "LIGHT_MODEL_ROOT", light_model_root
    )
    action_model_opt_file = FLAGS.action_model_opt_file.replace(
        "LIGHT_MODEL_ROOT", light_model_root
    )
    roleplaying_score_opt_file = FLAGS.roleplaying_score_opt_file.replace(
        "LIGHT_MODEL_ROOT", light_model_root
    )
    generic_act_opt_file = FLAGS.generic_act_opt_file.replace(
        "LIGHT_MODEL_ROOT", light_model_root
    )
    parser_opt_file = FLAGS.parser_opt_file.replace(
        "LIGHT_MODEL_ROOT", light_model_root
    )

    model_pool = ModelPool()

    # Register Models

    if len(safety_model_opt_file) > 3:
        model_pool.register_model(
            ParlAIModelConfig(opt_file=safety_model_opt_file),
            [ModelTypeName.SAFETY],
        )
    if len(dialog_model_opt_file) > 3:
        model_pool.register_model(
            ParlAIModelConfig(opt_file=dialog_model_opt_file),
            [ModelTypeName.DIALOG],
        )
    if len(roleplaying_score_opt_file) > 3:
        model_pool.register_model(
            ParlAIPolyencoderActingScoreModelConfig(
                opt_file=roleplaying_score_opt_file
            ),
            [ModelTypeName.SCORING],
        )
    if len(action_model_opt_file) > 3:
        model_pool.register_model(
            ParlAIModelConfig(opt_file=action_model_opt_file),
            [ModelTypeName.ACTION],
        )
    if len(generic_act_opt_file) > 3:
        model_pool.register_model(
            ParlAIModelConfig(opt_file=generic_act_opt_file),
            [ModelTypeName.GENERIC_ACTS],
        )
    if len(parser_opt_file) > 3:
        model_pool.register_model(
            ParlAIModelConfig(opt_file=parser_opt_file),
            [ModelTypeName.PARSER],
        )
    FLAGS.safety_classifier_path = FLAGS.safety_list

    return model_pool


def main():
    import argparse
    import numpy
    import random

    DEFAULT_PORT = 35494
    DEFAULT_HOSTNAME = "localhost"

    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif v.lower() in ("no", "false", "f", "n", "0"):
            return False
        else:
            raise argparse.ArgumentTypeError("Boolean value expected.")

    parser = argparse.ArgumentParser(
        description="Start the game server.", fromfile_prefix_chars="@"
    )
    parser.add_argument(
        "--cookie-secret",
        type=str,
        default="temp8000800080008000",
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
        "--db-root",
        type=str,
        default=here + "/../../../logs/db_root",
    )
    parser.add_argument(
        "--disable-builder",
        metavar="disable_builder",
        type=str,
        default=None,
        help="flag to disable the builder, omit to enable",
    )
    parser.add_argument(
        "--builder-model",
        metavar="builder_model",
        type=str,
        default=None,
        help="Builder model to be loading",
    )
    parser.add_argument(
        "--safety-list",
        type=str,
        default=os.path.expanduser("~/data/safety/OffensiveLanguage.txt"),
        help="Where to find the offensive language list.",
    )
    parser.add_argument(
        "--safety-model-opt-file",
        type=str,
        default=os.path.join(CONFIG_DIR, "baseline_adversarial_safety.opt"),
        help="Where to find the offensive language list.",
    )
    parser.add_argument(
        "--dialog-model-opt-file",
        type=str,
        default=os.path.join(CONFIG_DIR, "baseline_generative.opt"),
        help="dialog model to be loading",
    )
    parser.add_argument(
        "--roleplaying-score-opt-file",
        type=str,
        default=os.path.join(CONFIG_DIR, "baseline_roleplaying_scorer.opt"),
    )
    parser.add_argument(
        "--action-model-opt-file",
        type=str,
        default=os.path.join(CONFIG_DIR, "baseline_main_act_model.opt"),
    )
    parser.add_argument(
        "--generic-act-opt-file",
        type=str,
        default=os.path.join(CONFIG_DIR, "generic_act_model.opt"),
    )
    parser.add_argument(
        "--parser-opt-file",
        type=str,
        default=os.path.join(CONFIG_DIR, "baseline_parser.opt"),
    )
    parser.add_argument(
        "--is-logging",
        type=str2bool,
        default=False,
        help="flag to enable storing logs of interactions",
    )
    parser.add_argument(
        "--db-backend",
        type=str,
        default="test",
    )
    FLAGS, _unknown = parser.parse_known_args()

    print(FLAGS)

    random.seed(6)
    numpy.random.seed(6)
    model_pool = init_model_pool(FLAGS)
    ldb = LIGHTDatabase(FLAGS.data_model_db)
    asyncio.run(_run_server(FLAGS, ldb, model_pool))


if __name__ == "__main__":
    main()
