#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict
import asyncio
import time

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.graph.world.world import World
    from light.graph.events.base import GraphEvent


class Soul(ABC):
    """
    Gives GraphAgents the ability to observe and act. Without a Soul, GraphAgents
    are merely a husk of a GraphNode that act as a body, but with no intent
    or capability. The Soul takes in observations from what occurs in the world,
    and is responsible for handling how an GraphAgent will react in response.
    """

    def __init__(self, target_node: "GraphAgent", world: "World"):
        """
        All Souls should be attached to a target_node, which is the agent that
        this soul will be inhabiting. It also takes the world in which that
        agent exists.
        """
        self.target_node = target_node
        self.world = world
        self._observe_futures: Dict[str, asyncio.Future] = {}
        self.is_reaped = False

    def wrap_observe_event(self, event):
        """
        Souls will observe events in a future, such that it can be cancelled
        during a reap.
        """
        future_id = f"Node-{self.target_node.node_id}-obs-{time.time():.10f}"
        _observe_future = self.observe_event(event)

        async def _await_observe_then_cleanup():
            try:
                await _observe_future
                del self._observe_futures[future_id]
            except Exception as e:
                print(f"Error when running observe for soul {self}: {repr(e)}")
                import traceback
                traceback.print_exc()

        loop = asyncio.get_running_loop()
        self._observe_futures[future_id] = asyncio.ensure_future(
            _await_observe_then_cleanup(), loop=loop
        )

    @abstractmethod
    async def observe_event(self, event: "GraphEvent"):
        """
        All souls should define some kind of behavior for when an event occurs,
        ensuring that they are able to handle it somehow.

        The soul may choose to ask the world for possible actions it may take, and
        then take one in response, or perhaps bide its time, launching a thread
        to do something later. Maybe it just takes a note for itself.

        This method will always be called asyncronously, such that it can be
        cancelled and won't block execution of the world.
        """
        pass

    def reap(self):
        """
        Free resources associated with this Soul, and ensure any pending futures
        are cancelled.

        It's possible that a Soul may be reaped, due to death or to make room for
        another Soul to inhabit the same GraphAgent. In any case, when a Soul
        is reaped, it should clean up after itself.
        """
        self.is_reaped = True
        outstanding_future_ids = list(self._observe_futures.keys())
        for future_id in outstanding_future_ids:
            future = self._observe_futures.get(future_id)
            if future is not None:
                future.cancel()
