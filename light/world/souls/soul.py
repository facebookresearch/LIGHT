#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod

import threading
import time
from typing import TYPE_CHECKING, List

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
        self._observe_threads = []
        self.is_reaped = False

    def launch_observe_event_thread(self, event):
        """
        Souls will observe events in a background thread to ensure that 
        they can choose to act how they wish in response.
        """
        observe_thread = threading.Thread(
            target=self.observe_event,
            args=(event,),
            name=f"Node-{self.target_node.node_id}-observe-{time.time():.4f}",
        )
        self._observe_threads.append(observe_thread)
        observe_thread.start()

    @abstractmethod
    def observe_event(self, event: "GraphEvent"):
        """
        All souls should define some kind of behavior for when an event occurs,
        ensuring that they are able to handle it somehow. 
        
        The soul may choose to ask the world for possible actions it may take, and 
        then take one in response, or perhaps bide its time, launching a thread 
        to do something later. Maybe it just takes a note for itself. 
        
        This method will always be called in a separate thread, such that no Souls
        have the ability to prevent other Souls from observing.
        """
        pass

    def reap(self):
        """
        Free resources associated with this Soul, and ensure any pending events
        or threads are cancelled.

        It's possible that a Soul may be reaped, due to death or to make room for
        another Soul to inhabit the same GraphAgent. In any case, when a Soul
        is reaped, it should clean up after itself.
        """
        self.is_reaped = True
