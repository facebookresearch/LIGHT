#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.world.souls.base_soul import BaseSoul
import os
import asyncio
from typing import TYPE_CHECKING, Any
from concurrent.futures import CancelledError

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.graph.world.world import World


class ModelSoul(BaseSoul):
    """
    A ModelSoul is responsible for passing it's observations back to
    a model that decides what to do. This class should be initialized with a
    `models` parameter that can be used for the main operations.
    """

    HAS_MAIN_LOOP = False
    MAIN_LOOP_STEP_TIMEOUT = 5  # seconds between loop actions

    def __init__(self, target_node: "GraphAgent", world: "World", models: Any):
        """
        All Souls should be attached to a target_node, which is the agent that
        this soul will be inhabiting. It also takes the world in which that
        agent exists.
        """
        super().__init__(target_node, world)
        self._init_with_models(models)
        self._main_loop = None
        if self.HAS_MAIN_LOOP:
            self._run_timesteps()

    def _init_with_models(self, models) -> None:
        """
        If this model soul requires additional configuration of the models,
        or setting of attributes depending on these models, handle that here.
        """
        pass

    async def _take_timestep(self) -> None:
        """
        If this model intends to take actions periodically, those steps should
        be defined in this method. The method _run_timesteps will call this
        periodically.
        """
        pass

    def _run_timesteps(self) -> None:
        """
        Call _take_timestep every MAIN_LOOP_STEP_TIMEOUT period
        """

        async def _run_main_logic_forever():
            try:
                while not self.is_reaped:
                    await self._take_timestep()
                    await asyncio.sleep(self.MAIN_LOOP_STEP_TIMEOUT)
            except CancelledError:
                return
            except Exception as e:
                print(f"Unhandled model soul exception in {self}: {e}")
                import traceback

                traceback.print_exc()
                print("Reaping...")
                self.reap()

        self._main_loop = asyncio.create_task(_run_main_logic_forever())

    def reap(self):
        """
        Clear the main loop, and free any model resources
        """
        super().reap()
        if self._main_loop is not None:
            self._main_loop.cancel()
