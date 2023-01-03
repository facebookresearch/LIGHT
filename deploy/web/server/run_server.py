#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
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
import inspect
import os
import asyncio
import hydra
from dataclasses import dataclass, field
from omegaconf import MISSING

from light.data_model.db.base import LightDBConfig, LightAWSDBConfig
from light.data_model.db.episodes import EpisodeDB
from light.data_model.db.users import UserDB
from light.world.world import WorldConfig
from light.graph.builders.base import GraphBuilderConfig
from light.graph.builders.map_json_builder import MapJsonBuilderConfig
from light.graph.builders.tutorial_builder import TutorialBuilderConfig
from light.registry.model_pool import ModelPool, ModelTypeName
from light.registry.hydra_registry import register_script_config, ScriptConfig

from typing import List, Any, Dict, Optional, TYPE_CHECKING

from light import LIGHT_DIR

CONFIG_DIR = os.path.join(LIGHT_DIR, "light/registry/models/config")
HYDRA_CONFIG_DIR = os.path.join(LIGHT_DIR, "hydra_configs")

DEFAULT_PORT = 35494
DEFAULT_HOSTNAME = "localhost"

@dataclass
class WorldServerConfig(ScriptConfig):
    defaults: List[Any] = field(
        default_factory=lambda: ["_self_", {"deploy": "local_no_models"}]
    )
    builder: GraphBuilderConfig = MapJsonBuilderConfig(
        load_map=os.path.expanduser("~/LIGHT/scripts/examples/complex_world.json")
    )
    tutorial_builder: Optional[GraphBuilderConfig] = TutorialBuilderConfig(load_map="")
    safety_classifier_path: str = field(
        default=os.path.expanduser("~/data/safety/OffensiveLanguage.txt"),
        metadata={"help": "Where to find the offensive language list."},
    )
    magic_db_path: str = ""
    cookie_secret: str = field(
        default="temp8000800080008000",  # can be any value, overridden by our configs
        metadata={"help": "Cookie secret for issueing cookies (SECRET!!!)"},
    )
    preauth_secret: str = field(
        default="temp8000800080008000",  # can be any value, overridden by our configs
        metadata={"help": "Secret for salting valid preauth keys"},
    )
    facebook_api_key: str = field(
        default=MISSING,
        metadata={"help": "FB API login key"},
    )
    facebook_api_secret: str = field(
        default=MISSING,
        metadata={"help": "FB API secret key"},
    )
    facebook_asid_salt: str = field(
        default=MISSING,
        metadata={"help": "String to salt the asid with"},
    )
    hostname: str = field(
        default=DEFAULT_HOSTNAME,
        metadata={"help": "host to run the server on."},
    )
    port: int = field(
        default=DEFAULT_PORT,
        metadata={"help": "port to run the server on."},
    )
    password: str = field(
        default="LetsPlay",
        metadata={"help": "password - leave blank to disable login with password"},
    )
    disable_builder: bool = field(
        default=True, metadata={"help": "Bool to disable launching the world builder"}
    )
    is_logging: bool = field(
        default=False,
        metadata={"help": "Whether to initialize writing episodes to the DB"},
    )


register_script_config("scriptconfig", WorldServerConfig)


def make_app(cfg: WorldServerConfig, model_pool: ModelPool):
    # Construct tornado settings for this app
    tornado_settings = {
        "autoescape": None,
        "cookie_secret": cfg.cookie_secret,
        "compiled_template_cache": False,
        "debug": "/dbg/" in __file__,
        "login_url": "/login",
        "preauth_secret": cfg.preauth_secret,
        "template_path": get_path("static"),
    }

    if cfg.get("facebook_api_key", None) is not None:
        tornado_settings["facebook_api_key"] = cfg.facebook_api_key
    if cfg.get("facebook_api_secret", None) is not None:
        tornado_settings["facebook_secret"] = cfg.facebook_api_secret
    if cfg.get("facebook_asid_salt", None) is not None:
        tornado_settings["facebook_asid_salt"] = cfg.facebook_asid_salt

    # TODO re-enable world builder once builder models are hydra-registered
    # worldBuilderApp = BuildApplication(get_handlers(ldb), tornado_settings)

    db_config = cfg.light.db
    episode_db = EpisodeDB(db_config)
    user_db = UserDB(db_config)
    landingApp = LandingApplication(
        user_db=user_db,
        hostname=cfg.hostname,
        password=cfg.password,
        given_tornado_settings=tornado_settings,
    )
    registryApp = RegistryApplication(
        cfg,
        model_pool,
        tornado_settings,
        episode_db=episode_db,
        user_db=user_db,
    )
    rules = []
    # TODO re-enable world builder once builder models are hydra-registered
    # if not cfg.disable_builder:
    #     rules.append(Rule(PathMatches("/builder.*"), worldBuilderApp))
    rules += [
        Rule(PathMatches("/game.*"), registryApp),
        Rule(PathMatches("/.*"), landingApp),
    ]

    router = RuleRouter(rules)
    server = HTTPServer(router)
    server.listen(cfg.port)
    return registryApp


async def _run_server(cfg: WorldServerConfig, model_pool: ModelPool):
    registry_app = make_app(cfg, model_pool)
    _ = await registry_app.run_new_game("")

    print("\nYou can connect to the game at http://%s:%s/" % (cfg.hostname, cfg.port))
    print(
        "You can connect to the worldbuilder at http://%s:%s/builder/ \n"
        % (cfg.hostname, cfg.port)
    )
    while True:
        await asyncio.sleep(30)

def get_path(filename):
    """Get the path to an asset."""
    cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    return os.path.join(cwd, filename)

@hydra.main(
    config_path=HYDRA_CONFIG_DIR, config_name="scriptconfig", version_base="1.2"
)
def main(cfg: WorldServerConfig):
    import numpy
    import random

    model_pool = ModelPool.get_from_config(cfg.light.model_pool)
    random.seed(6)
    numpy.random.seed(6)

    asyncio.run(_run_server(cfg, model_pool))


if __name__ == "__main__":
    main()
