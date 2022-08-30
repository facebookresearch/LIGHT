#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.world.souls.soul import Soul
from light.world.content_loggers import AgentInteractionLogger
from light.world.quest_loader import QuestCreator
from light.graph.events.magic import check_if_cast_magic_from_event
from typing import TYPE_CHECKING, Optional
import random
import time
from light.graph.events.graph_events import SystemMessageEvent

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.world.world import World
    from light.graph.events.base import GraphEvent


class TutorialPlayerSoul(Soul):
    """
    A TutorialPlayerSoul is responsible for interfacing with the players
    in a tutorial via a PlayerProvider.
    """

    def __init__(
        self,
        target_node: "GraphAgent",
        world: "World",
        player_id: str,
        provider=None,
        shared_model_content=None,
    ):
        """
        TutorialPlayerSouls register to a GraphAgent in a World, but also keep track of the
        current player. They interface with the human through the provider
        """
        super().__init__(target_node, world)
        assert not target_node.is_player, "Cannot have two players in the same agent!"
        target_node.is_player = True
        target_node._last_action_time = time.time()
        self.player_id = player_id
        self.provider = provider  # TODO link with real provider
        self.agent_logger = AgentInteractionLogger(world.oo_graph, target_node)
        provider.register_soul(self)
        self.world.oo_graph.room_id_to_loggers[
            self.target_node.get_room().node_id
        ]._add_player()

    def handle_act(self, act_text, event_id: Optional[str] = None):
        """
        PlayerSouls must process act text sent from players and enact them on the world.
        This method is called by the player provider when an action is taken.
        """
        actor = self.target_node
        actor._last_action_time = time.time()
        self.world.parse_exec(self.target_node, act_text, event_id=event_id)

    async def observe_event(self, event: "GraphEvent"):
        """
        PlayerSouls pass their observation along to the provider, who will handle
        getting the correct format to send to the view.
        """
        self.provider.player_observe_event(self, event)
        self.agent_logger.observe_event(event)

    def reap(self):
        """
        PlayerSouls must remove the player flag from their target GraphAgent when
        removed, and notify the logger
        """
        super().reap()
        self.target_node.is_player = False
        self.world.oo_graph.room_id_to_loggers[
            self.target_node.get_room().node_id
        ]._remove_player()
        if self.agent_logger._logging_intialized:
            self.agent_logger._end_meta_episode()
        self.provider.on_reap_soul(self)
