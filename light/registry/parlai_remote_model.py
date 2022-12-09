#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig
import requests
import aiohttp
import asyncio
import logging
import json

from parlai.core.agents import Agent
from parlai.core.message import Message
from parlai.core.opt import Opt
from copy import deepcopy
import os

from typing import List, Any, Dict, Optional


DEFAULT_SERVER = "http://localhost:40000"
DEFAULT_SERVER_TIMEOUT = 600
DEFAULT_RETRIES = 3
DEFAULT_API_FAIL_TEXT = "MODEL RESPONSE FAILED"


def is_request_failed_response(resp):
    """
    Whether the requests to Metaseq worker have failed.
    It checks this based on the existences of the failure reasons as they get
    accumulated in `_make_request` functionn calls.
    """
    return len(resp.get("failures", [])) > 0


async def _make_request(
    session: aiohttp.ClientSession,
    server: str,
    act_message: Message,
    num_retry_on_api_exception=-1,
    request_delay: float = 0.5,
) -> Dict[str, Any]:
    data = {
        "observation": act_message,
    }
    init_request_delay = request_delay
    past_exceptions: List[Dict[str, Any]] = []
    while True:
        if (
            num_retry_on_api_exception >= 0
            and len(past_exceptions) > num_retry_on_api_exception
        ):
            logging.error("Reached maximum retries, returning failure message.")
            return {
                "failures": past_exceptions,
            }
        try:
            logging.debug(f"Making request: {data}")
            async with session.post(
                f"{server}/model_request",
                json=data,
            ) as resp:
                resp_text = await resp.text()
                obj = json.loads(resp_text)
                if "error" in obj:
                    request_delay *= 2
                    logging.warning(f"Error: {obj['error']}")
                    past_exceptions.append(obj["error"])
                    logging.debug(past_exceptions[-1])
                    continue
                debug = json.dumps(obj, sort_keys=True)
                logging.debug(f"Model Server response: {debug}")
                request_delay = init_request_delay
                return obj
        except asyncio.TimeoutError as e:
            error_text = f'Timout a response for {len(act_message["text"])}\n{e}'
        except aiohttp.client_exceptions.ClientOSError as e:
            error_text = f'Retrying a response for {len(act_message["text"])}\n{e}'
        except json.decoder.JSONDecodeError as e:
            error_text = f"Got a bad response, {resp_text}. Retrying.\n{e}"

        past_exceptions.append({"error": error_text})
        logging.warning(error_text)
        request_delay *= 2
        await asyncio.sleep(request_delay)


async def async_request_many(
    server: str,
    acts: List[Message],
    timeout: Optional[int] = None,
    max_num_tries: int = -1,
):
    connector = aiohttp.TCPConnector(limit=0)
    timeout_obj = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(
        timeout=timeout_obj, connector=connector
    ) as session:
        tasks = []
        for act in acts:
            tasks.append(
                asyncio.ensure_future(
                    _make_request(
                        session=session,
                        server=server,
                        act_message=act,
                        num_retry_on_api_exception=max_num_tries,
                    )
                )
            )
        results = await asyncio.gather(*tasks)
        return results


def server_is_alive(server: str) -> bool:
    """See if the specified server is alive"""
    try:
        alive_url = server + "/is_alive"
        is_alive_json = requests.post(alive_url, json.dumps({"alive": True}))
        is_alive = is_alive_json.json()
        return is_alive.get("alive", False)
    except Exception as e:
        print("Error Checking liveliness: ", e)
        return False


class ParlAIRemoteAgentWrapper(Agent):
    def __init__(self, opt: Opt):
        """Agent wrapper that actually just executes things remotely"""
        self.observed_act = Message({"text": "", "episode_done": True})
        self.server = opt["server"]
        self.retries = opt["retries"]
        self.timeout = opt["timeout"]

    async def act(self):
        resps = await async_request_many(
            server=self.server,
            acts=[self.observed_act],
            timeout=self.timeout,
            max_num_tries=self.retries,
        )
        resp = resps[0]
        if is_request_failed_response(resp):
            act = Message({"text": DEFAULT_API_FAIL_TEXT})
        else:
            act = Message(resp["act"])
        return act

    def observe(self, observation: Message):
        self.observed_act = observation


@dataclass
class ParlAIRemoteModelConfig:
    # As of now, ParlAI is the only model loader.
    # Eventually this could be split into more classes
    # as we incorporate other models.
    _loader: str = "ParlAIRemote"
    host: str = field(
        default=MISSING,
        metadata={"help": ("URL Hostname of the model server, with port.")},
    )
    retries: int = field(
        default=DEFAULT_RETRIES,
        metadata={"help": ("How many times to retry on error before giving up.")},
    )
    timeout: int = field(
        default=DEFAULT_SERVER_TIMEOUT,
        metadata={
            "help": ("How long to wait for a response before considering a timeout")
        },
    )

    def get(self, attr: str, default_val: Optional[Any] = None):
        """Wrapper to ensure interoperability with hydra DictConfig"""
        val = self.__dict__.get(attr, default_val)
        if val == MISSING:
            val = None
        return val


class ParlAIRemoteModelLoader:
    """
    Takes in the configuration for a ParlAIRemote model, and establishes the connection
    """

    def __init__(self, config: DictConfig):
        self.config = config
        self.load_model(config)

    async def force_load(self) -> None:
        """
        Force the model loader to connect to the remote service and ensure the
        connection is live.
        """
        self.load_model(self.config)

    def load_model(self, config: DictConfig) -> None:
        """Initialize the model from the given config"""
        remote_host = config.get("host", DEFAULT_SERVER)
        assert server_is_alive(remote_host), "Remote host failed alive check"
        self.remote_opt = Opt(
            {
                "server": remote_host,
                "retries": config.get("retries", DEFAULT_RETRIES),
                "timeout": config.get("timeout", DEFAULT_SERVER_TIMEOUT),
            }
        )

    def get_model(self, overrides: Optional[Dict[str, Any]] = None) -> Agent:
        """Get a copy of the model"""
        assert server_is_alive(
            self.remote_opt["server"]
        ), "Remote host failed alive check"
        return ParlAIRemoteAgentWrapper(self.remote_opt)
