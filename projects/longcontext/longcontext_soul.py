#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.graph.events.graph_events import EmoteEvent, SayEvent
from light.world.souls.soul import Soul
from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.graph.world.world import World
    from light.graph.events.base import GraphEvent


class LongcontextSoul(Soul):
    """
    The simplest of Souls, it responds to all events by saying what it saw
    """
    
    def __init__(self, target_node: "GraphAgent", world: "World"):
        """
        LongcontextSouls (currently) just initialize normally on a node and world
        """
        super().__init__(target_node, world)
        
    def take_timestep(self):
        agent = self.target_node
        agent_id = agent.node_id

        # random movement for npcs..
        if random.randint(0, 100) < 50:
            go_events = self.world.get_possible_events(agent_id, use_actions=["go"])
            if len(go_events) > 0:
                go_event = random.choice(go_events)
                if hasattr(self, 'is_viewed'):
                    view_txt = 'You go towards the ' + go_event._canonical_targets[0]
                    print(view_txt)
                go_event.execute(self.world)
                return

        #do_event = EmoteEvent.construct_from_args(
        #    self.target_node, targets=[], text="grin"
        #)
        #do_event.execute(self.world)
    
    def observe_event(self, event: "GraphEvent"):
        """
        LongcontextSouls check for specific events, that trigger specific actions.
        """

        if not hasattr(self, 'is_viewed'):
            return
        
        if event.actor == self.target_node:
            class_name = event.__class__.__name__
            if class_name == 'LeaveEvent' or class_name == 'ArriveEvent':
                return
        
        view_txt = event.view_as(self.target_node)
        if view_txt == None:
            class_name = event.__class__.__name__
            #if class_name == 'ArriveEvent':
            #    view_txt = 'You arrived from the ' + event.text_content
            #elif class_name == 'LeaveEvent':
            #    view_txt = 'You left from the ' + event.text_content
            #else:
            #    import pdb; pdb.set_trace()
            #print(view_txt)
        else:
            print(view_txt)



