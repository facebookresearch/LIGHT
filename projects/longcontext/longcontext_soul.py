#!/usr/bin/env python3


# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.graph.events.graph_events import EmoteEvent, SayEvent, TellEvent
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

    def provide_task(self):
        # STEP 1: in same room as viewing agent?
        agent = self.target_node
        my_room = self.target_node.get_room()
        viewer_room = self.world.view_soul.target_node.get_room()
        if my_room != viewer_room:
            return
        if random.randint(0, 100) < 75:
            return False
        partner = self.world.view_soul.target_node
        # find an open task
        for task, taken in self.world.tasks.items():
            if taken == False and task != agent and my_room != task.get_room():
                act_text = (
                    "can you tell the "
                    + task.name
                    + " that the "
                    + self.target_node.name
                    + " wants to see them?"
                )
                self.world.tasks[task] = agent
                tell_event = TellEvent(
                    agent, target_nodes=[partner], text_content=act_text
                )
                tell_event.execute(self.world)
                # import pdb; pdb.set_trace()
                return True
        return False

    def complete_task(self):
        # is anything in the same room a task?
        contents = self.target_node.get_room().get_contents()
        task = None
        for c in contents:
            if c in self.world.tasks and self.world.tasks[c] != False:
                task = c
        if task is None:
            return
        task_contents = self.world.tasks[task]  # person who assigned the task
        agent = self.target_node
        partner = task
        act_text = task_contents.name + " wants to see you!"
        tell_event = TellEvent(agent, target_nodes=[partner], text_content=act_text)
        tell_event.execute(self.world)
        view_txt = "You tell the " + partner.name + ' "' + act_text + '"'
        print(view_txt)

        # Clear task
        self.world.tasks[task] = False
        return True

    def take_timestep(self):
        agent = self.target_node
        agent_id = agent.node_id

        if hasattr(self, "is_viewed"):
            # "player"
            if self.complete_task():
                return
        else:
            # random agent that provides a task
            if self.provide_task():
                return

        # random movement for npcs..
        if random.randint(0, 100) < 50:
            go_events = self.world.get_possible_events(agent_id, use_actions=["go"])
            if len(go_events) > 0:
                go_event = random.choice(go_events)
                if hasattr(self, "is_viewed"):
                    view_txt = "You go towards the " + go_event._canonical_targets[0]
                    print(view_txt)
                go_event.execute(self.world)
                return

        # do_event = EmoteEvent.construct_from_args(
        #    self.target_node, targets=[], text="grin"
        # )
        # do_event.execute(self.world)

    def observe_event(self, event: "GraphEvent"):
        """
        LongcontextSouls check for specific events, that trigger specific actions.
        """

        if not hasattr(self, "is_viewed"):
            return

        if event.actor == self.target_node:
            class_name = event.__class__.__name__
            if class_name == "LeaveEvent" or class_name == "ArriveEvent":
                return

        view_txt = event.view_as(self.target_node)
        if view_txt == None:
            class_name = event.__class__.__name__
            # if class_name == 'ArriveEvent':
            #    view_txt = 'You arrived from the ' + event.text_content
            # elif class_name == 'LeaveEvent':
            #    view_txt = 'You left from the ' + event.text_content
            # else:
            #    import pdb; pdb.set_trace()
            # print(view_txt)
        else:
            print(view_txt)
