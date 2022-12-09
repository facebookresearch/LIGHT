#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Application specifically for hosting a model for remote access

Examples:
python model_server.py model.opt_file=../../../light/registry/models/config/generic_act_model.opt
python model_server.py model.opt_file=../../../light/registry/models/config/baseline_adversarial_safety.opt
python model_server.py model._loader=ParlAIActingScore model.opt_file=../../../light/registry/models/config/baseline_roleplaying_scorer.opt
"""

import json
import logging
import os
import traceback
import asyncio
import gc
import hydra
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Optional, List

import tornado.escape
import tornado.ioloop
import tornado.web

from light import LIGHT_DIR
from light.registry.model_pool import ModelPool, ModelTypeName
from light.registry.parlai_model import ParlAIModelConfig
from light.registry.hydra_registry import register_script_config, ScriptConfig


if TYPE_CHECKING:
    from parlai.core.agents import Agent

tornado_settings = {
    "autoescape": None,
    "compiled_template_cache": False,
}
DEFAULT_HOSTNAME = "localhost"
DEFAULT_PORT = 40000

HYDRA_CONFIG_DIR = os.path.join(LIGHT_DIR, "hydra_configs")


class ModelServer(tornado.web.Application):
    def __init__(self, model: "Agent", given_tornado_settings=None):
        self.model = model

        super(ModelServer, self).__init__(self.get_handlers(), **given_tornado_settings)

    def get_handlers(self):
        return [
            (r"/model_request", ResponseHandler, {"model": self.model}),
            (r"/is_alive", AliveHandler, {}),
        ]


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *request, **kwargs):
        self.include_host = False
        super(BaseHandler, self).__init__(*request, **kwargs)

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")

    def write_error(self, status_code, **kwargs):
        logging.error("ERROR: %s: %s" % (status_code, kwargs))
        if "exc_info" in kwargs:
            logging.info(
                "Traceback: {}".format(traceback.format_exception(*kwargs["exc_info"]))
            )
            exc_info = kwargs["exc_info"]
            try:
                params = {
                    "error": str(exc_info[1]),
                    "trace_info": traceback.format_exception(*exc_info),
                    "request": str(self.request.__dict__),
                }
                self.write(json.dumps(params))
            except Exception as e:
                logging.error(e)


class ResponseHandler(BaseHandler):
    """
    Handler to pass a post response along to the model, then
    return a result
    """

    def initialize(self, model):
        self.model = model

    async def post(self):
        # Process the data to extract the act
        data = tornado.escape.json_decode(self.request.body)
        message = data["observation"]
        # Pass the act to the model
        self.model.observe(message)
        # return the response
        response = await self.model.act()
        if "metrics" in response:
            del response["metrics"]
        if "sorted_scores" in response and not isinstance(
            response["sorted_scored"], list
        ):
            response["sorted_scores"].force_set(response["sorted_scores"].tolist())
        try:
            self.write(json.dumps({"act": response}))
        except TypeError:
            print("JSON encoding failed:")
            print(response.keys())
            print(response)
            raise


class AliveHandler(BaseHandler):
    """
    Handler to pass a post response along to the model, then
    return a result
    """

    def initialize(self):
        pass

    def post(self):
        # Process the data to extract the act
        self.write(json.dumps({"alive": True}))


def _run_server(
    given_tornado_settings: Dict[str, Any], hostname: str, port: int, model: "Agent"
):
    """
    Run the model server with the given setup configuration
    """
    my_loop = tornado.ioloop.IOLoop()

    app = ModelServer(
        model=model,
        given_tornado_settings=given_tornado_settings,
    )
    app.listen(port, max_buffer_size=1024 ** 3)
    print("Model Server Started")

    try:
        my_loop.start()
    except KeyboardInterrupt:
        my_loop.stop()
    print("Exiting server")


def _init_model(cfg: ParlAIModelConfig) -> "Agent":
    """Initialize a model for serving"""
    pool = ModelPool()
    pool.register_model(cfg, [ModelTypeName.SERVED])
    model = pool.get_model(ModelTypeName.SERVED)
    # Try to clear up some memory
    del pool._model_loaders[ModelTypeName.SERVED.value]

    gc.collect()
    return model


@dataclass
class ModelServerConfig(ScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: ["_self_"])
    model: ParlAIModelConfig = ParlAIModelConfig()
    config_dif: str = os.path.join(LIGHT_DIR, "light/registry/models/config/")
    port: int = field(
        default=DEFAULT_PORT, metadata={"help": "Port to run the server on"}
    )
    hostname: str = field(
        default=DEFAULT_HOSTNAME, metadata={"help": "Host to run the server on"}
    )


register_script_config("scriptconfig", ModelServerConfig)


@hydra.main(
    config_path=HYDRA_CONFIG_DIR, config_name="scriptconfig", version_base="1.2"
)
def main(cfg: ModelServerConfig):
    os.environ["LIGHT_MODEL_ROOT"] = cfg.light.model_root
    model = _init_model(cfg.model)
    _run_server(tornado_settings, cfg.hostname, cfg.port, model)


if __name__ == "__main__":
    main()
