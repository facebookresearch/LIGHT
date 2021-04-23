#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.world.souls.base_soul import BaseSoul
from light.world.content_loggers import AgentInteractionLogger
from light.world.quest_loader import QuestCreator
from light.graph.events.magic import check_if_cast_magic_from_event
from typing import TYPE_CHECKING, Optional
import random
import time

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.world.world import World
    from light.graph.events.base import GraphEvent

QUESTS_ACTIVE = True
QUEST_TEXT = "\nYour Mission: "


class PlayerSoul(BaseSoul):
    """
    A PlayerSoul is responsible for interfacing with the players in the
    game via a PlayerProvider, and will handle incoming messages
    from there and forward observations out.
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
        PlayerSouls register to a GraphAgent in a World, but also keep track of the
        current player. They interface with the human through the provider
        """
        super().__init__(target_node, world)
        assert not target_node.is_player, "Cannot have two players in the same agent!"
        # TODO merge these flags across LIGHT
        target_node.is_player = True
        target_node._human = True
        target_node._last_action_time = time.time()
        self.player_id = player_id
        self.provider = provider  # TODO link with real provider
        if hasattr(target_node, "mission") and target_node.mission != "":
            goal = target_node.mission
            target_node.persona += QUEST_TEXT + goal
        else:
            if hasattr(self.provider, "quest_loader"):
                target_quest = self.provider.quest_loader.get_random_quest()
                goal = random.choice(
                    ["short_motivation", "mid_motivation", "long_motivation"]
                )
                target_node.persona += QUEST_TEXT + target_quest[goal]
        if "rpg_model" in shared_model_content:
            self.roleplaying_score_model = shared_model_content["rpg_model"].clone()
        if "generic_act_model" in shared_model_content:
            self.generic_act_model = shared_model_content["generic_act_model"].clone()
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

    def new_quest(self):
        if random.random() > 0.01:
            # Turn these mostly off for now.
            return

        graph = self.world.oo_graph
        actor = self.target_node

        if hasattr(self, "generic_act_model"):
            quest = QuestCreator.create_quest(actor, graph, self.generic_act_model)
        else:
            # no model for generating quests
            quest = QuestCreator.create_quest(actor, graph)
        if quest is not None:
            self.world.send_msg(actor, "New Quest: " + quest["text"])

    def quest_events(self, event):
        # Possibly create quest if we don't have one.
        self.new_quest()
        actor = self.target_node
        quests_left = []
        if actor.quests is None:
            actor.quests = []
        for q in actor.quests:
            if QuestCreator.quest_matches_event(self.world, q, event):
                QuestCreator.quest_complete(self.world, actor, q, event)
            else:
                quests_left.append(q)
        actor.quests = quests_left

    async def observe_event(self, event: "GraphEvent"):
        """
        PlayerSouls pass their observation along to the provider, who will handle
        getting the correct format to send to the view.
        """
        self.set_interaction_partners_from_event(event)
        self.log_interaction_from_event(event)
        self.role_playing_score_events(event)
        check_if_cast_magic_from_event(self, event)
        self.quest_events(event)
        self.provider.player_observe_event(self, event)
        self.agent_logger.observe_event(event)

    def reap(self):
        """
        PlayerSouls must remove the player flag from their target GraphAgent when
        removed, and notify the logger
        """
        super().reap()
        self.target_node.is_player = False
        self.target_node._human = False
        self.target_node.persona = self.target_node.persona.split(QUEST_TEXT)[0]
        self.world.oo_graph.room_id_to_loggers[
            self.target_node.get_room().node_id
        ]._remove_player()
        if self.agent_logger._logging_intialized:
            self.agent_logger._end_meta_episode()
        self.provider.on_reap_soul(self)
