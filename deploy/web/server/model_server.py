#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

"""Application specifically for hosting a model for remote access"""


import argparse
import json
import logging
import os
import traceback
import asyncio
from typing import TYPE_CHECKING, Any, Dict, Optional

import tornado.auth
import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.websocket

from light import LIGHT_DIR
from light.registry.model_pool import ALL_LOADERS, ModelPool
from light.registry.models.acting_score_model import (
    ParlAIPolyencoderActingScoreModelConfig,
)

# Temporary imports pre Hydra
from light.registry.parlai_model import ParlAIModelConfig


if TYPE_CHECKING:
    from parlai.core.agents import Agent

tornado_settings = {
    "autoescape": None,
    "compiled_template_cache": False,
}
DEFAULT_HOSTNAME = "localhost"
DEFAULT_PORT = 40000


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


def _init_model(model_opt_file: str, model_loader: str) -> "Agent":
    """Initialize a model for serving"""

    pool = ModelPool()
    # Temporary mapping that allows us to get things running before Hydra
    cfg = None
    if model_loader == "ParlAI":
        cfg = ParlAIModelConfig(opt_file=model_opt_file)
    elif model_loader == "ParlAIActingScore":
        cfg = ParlAIPolyencoderActingScoreModelConfig(opt_file=model_opt_file)
    else:
        raise NotImplementedError(f"Unsupported model loader {model_loader}")

    pool.register_model(cfg, ["target"])
    model = pool.get_model("target")
    # Try to clear up some memory
    del pool._model_loaders["target"]
    import gc

    gc.collect()
    return model


def main():
    import random
    import numpy

    parser = argparse.ArgumentParser(description="Start the model server.")
    parser.add_argument(
        "--light-model-root",
        type=str,
        default=os.path.join(LIGHT_DIR, "models/"),
        help="Path to the models",
    )
    parser.add_argument(
        "--model-opt-file",
        type=str,
        default=os.path.join(
            LIGHT_DIR, "light/registry/models/config/baseline_generative.opt"
        ),
        help="Opt file to load a model from",
    )
    parser.add_argument(
        "--model-loader",
        type=str,
        default="ParlAI",
        help="ModelConfig to load alongside the given opt file",
    )
    parser.add_argument(
        "--port",
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

    os.environ["LIGHT_MODEL_ROOT"] = FLAGS.light_model_root
    model = _init_model(FLAGS.model_opt_file, FLAGS.model_loader)
    _run_server(tornado_settings, FLAGS.hostname, FLAGS.port, model)


if __name__ == "__main__":
    main()
