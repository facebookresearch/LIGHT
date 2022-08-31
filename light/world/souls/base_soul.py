#!/usr/bin/env python3


# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import asyncio
from light.world.souls.soul import Soul
from copy import deepcopy
import os
import asyncio
from typing import TYPE_CHECKING, Any, Optional
from light.graph.events.graph_events import SystemMessageEvent
from light.registry.model_pool import ModelTypeName

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.world.world import World
    from light.graph.events.base import GraphEvent


class BaseSoul(Soul):
    """
    Base soul that both player and NPC souls can inherit.
    It does some basic things like conversation interaction partner and dialogue
    and action history trackin, and roleplaying scoring, which is useful for both.
    """

    def __init__(self, target_node: "GraphAgent", world: "World"):
        """
        Standard Initialization.
        """
        super().__init__(target_node, world)
        self.target_node._last_interaction_partner_id = None
        self.reset_interaction_history(self.target_node)
        self.model_pool = world.model_pool
        if self.model_pool.has_model(ModelTypeName.SCORING):
            self.roleplaying_score_model = self.model_pool.get_model(
                ModelTypeName.SCORING
            )
        else:
            self.roleplaying_score_model = None

    def get_last_interaction_partner(self, node=None) -> Optional["GraphAgent"]:
        if node == None:
            node = self.target_node
        partner_id = node._last_interaction_partner_id
        if partner_id is None:
            return None
        return self.world.oo_graph.get_node(partner_id)

    def log_interaction_from_event(self, event):
        event_name = event.__class__.__name__
        agent = self.target_node
        agent_id = agent.node_id
        partner_id = self.target_node._last_interaction_partner_id
        event_actor_id = event.actor.node_id
        if (agent_id == event_actor_id or partner_id == event_actor_id) and (
            event_name == "TellEvent"
            or event_name == "SayEvent"
            or event_name == "WhisperEvent"
        ):
            # log event
            text = event.text_content
            if not (text.startswith("DEBUG")):
                agent._last_interaction_history.append(
                    [(event_actor_id, event_name, event.safe), text]
                )
        if (agent_id == event_actor_id or partner_id == event_actor_id) and (
            event_name == "EmoteEvent"
        ):
            # log event
            text = event.text_content
            agent._last_interaction_history.append(
                [(event_actor_id, event_name, True), "*" + text + "*"]
            )
        # Only log these kind of act events.
        act_events = [
            "UnfollowEvent",
            "FollowEvent",
            "UnblockEvent",
            "BlockEvent",
            "HitEvent",
            "HugEvent",
            "GetObjectEvent",
            "PutObjectInEvent",
            "DropObjectEvent",
            "StealObjectEvent",
            "GiveObjectEvent",
            "EquipObjectEvent",
            "WearEvent",
            "WieldEvent",
            "RemoveObjectEvent",
            "IngestEvent",
            "EatEvent",
            "DrinkEvent",
            "ExamineEvent",
            "UseEvent",
        ]
        if (agent_id == event_actor_id or partner_id == event_actor_id) and (
            event_name in act_events
        ):
            # log event
            text = event.to_canonical_form()
            agent._last_interaction_history.append(
                [(event_actor_id, event_name, True), "*" + text + "*"]
            )

    def set_interaction_partners_from_event(self, event):
        # Calculate who the event involves.
        agent1 = event.actor
        agent2 = None
        for n in event.target_nodes:
            if n.agent:
                agent2 = n

        # We need to assign partners for Say events.
        if event.__class__.__name__ == "SayEvent":
            # We need to predict who is talking to each other.
            if not hasattr(agent1, "_last_interaction_partner_id"):
                agent1._last_interaction_partner_id = None
            if agent1._last_interaction_partner_id is not None:
                agent2 = self.world.oo_graph.get_node(
                    agent1._last_interaction_partner_id
                )
                if agent2 is not None and agent1.get_room() != agent2.get_room():
                    agent1._last_interaction_partner_id = None
                    agent2._last_interaction_partner_id = None
                    agent2 = None
            if agent2 is None:
                # Now find a partner if available (someone in the room who isn't engaged).
                for n in agent1.get_room().get_contents():
                    if n.agent and n != agent1:
                        if (
                            not hasattr(n, "_last_interaction_partner_id")
                            or n._last_interaction_partner_id == None
                        ):
                            # Assign this agent.
                            agent2 = n

        # Now set the values given the two agents (if we have found two agents).
        if agent2 is not None:
            self.dialogue_switch_partner(agent1, agent2)

    def reset_interaction_history(self, agent=None):
        if agent == None:
            agent = self.target_node

        agent._last_interaction_partner_id = None
        agent._last_interaction_history = []

    def dialogue_switch_partner(self, agent1, agent2):
        """
        Clear this Soul's set dialogue partner, possibly clearing
        the partner if they still point to it.
        """
        if not hasattr(agent1, "_last_interaction_partner_id"):
            self.reset_interaction_history(agent1)
        if not hasattr(agent2, "_last_interaction_partner_id"):
            self.reset_interaction_history(agent2)

        if agent1._last_interaction_partner_id == agent2.node_id:
            return  # already interacting.

        if agent1._last_interaction_partner_id is not None:
            agent3 = self.world.oo_graph.get_node(agent1._last_interaction_partner_id)
            self.reset_interaction_history(agent3)
        if agent2._last_interaction_partner_id is not None:
            agent4 = self.world.oo_graph.get_node(agent2._last_interaction_partner_id)
            self.reset_interaction_history(agent4)

        self.reset_interaction_history(agent1)
        self.reset_interaction_history(agent2)
        agent1._last_interaction_partner_id = agent2.node_id
        agent2._last_interaction_partner_id = agent1.node_id
        # if hasattr(self.world, 'debug'):
        #    print(str(agent1) + " started interaction with " + str(agent2))

    def build_context(self, partner_name=None, quest_txt=None):
        """
        Build the full context for this Soul's model
        """
        agent = self.target_node
        room = agent.get_room()
        txt = "_setting_name " + room.name + "\n"
        txt += "_setting_desc " + room.desc + "\n"
        if partner_name is not None:
            txt += "_partner_name " + partner_name + "\n"
        else:
            if self.target_node._last_interaction_partner_id != None:
                partner = self.world.oo_graph.get_node(
                    self.target_node._last_interaction_partner_id
                )
                if partner is not None:
                    txt += "_partner_name " + partner.get_prefix_view() + "\n"
        txt += "_self_name " + agent.name + "\n"
        txt += "_self_persona " + agent.persona
        if quest_txt is not None:
            txt += quest_txt
        txt += "\n"
        return txt

    def build_dialog_context(self, quest_txt=None):
        # Initial context.
        txt = self.build_context(quest_txt)
        # Dialogue/interaction context.
        dtxt = ""
        agent = self.target_node
        agent_id = agent.node_id
        is_self = None
        turn_id = None
        for d in agent._last_interaction_history:
            current_turn_id = d[0][0]
            current_is_self = current_turn_id == agent_id
            if is_self == None or is_self == current_is_self:
                dtxt += " " + d[1]
            else:
                dtxt = dtxt.lstrip(" ")
                dtxt += "\n" + d[1]
            is_self = current_is_self
            is_safe = d[0][2]
            if not is_safe:
                # reset conversation when unsafe utterances are in the history
                dtxt = ""
        dtxt = dtxt.lstrip(" ")
        final = txt + dtxt
        return final

    ## ----- ROLE PLAYING SCORE FUNCTIONS BELOW

    def too_much_string_overlap(self, s1, s2):
        """
        Check if strings overlap too much.
        """
        s1_words = set(s1.split())
        s2_words = set(s2.split())
        if len(s2_words) == 0:
            return False
        overlap = len(s1_words.intersection(s2_words))
        if overlap / len(s2_words) > 0.5 or (len(s2_words) < 5 and overlap >= 2):
            return True
        return False

    async def get_fixed_cand_scores(self, context):
        """
        Returns the candidates at self.SAMPLE_INDS
        """
        act = {
            "text": context,
            "id": "persona",
            "episode_done": False,
        }
        self.roleplaying_score_model.observe(act)
        score_act = await self.roleplaying_score_model.act()
        return score_act["scores"]

    async def get_pos_human_msg(self, human_msg, context, scores):
        """
        Get the model score of the human message and compare to fixed cands.
        """
        act = {
            "text": context,
            "id": "persona",
            "episode_done": False,
            "label_candidates": [human_msg],
            "eval_labels": [human_msg],
        }
        self.roleplaying_score_model.observe(deepcopy(act))
        score_act = await self.roleplaying_score_model.act()

        human_score = float(score_act["scores"][0])
        human_points = len([x for x in scores if x < human_score])
        return human_points, human_score

    async def score_conversation(self):
        if self.roleplaying_score_model is None:
            # For local testing of exp with no models, set this to nonzero
            return 0

        context1 = self.build_dialog_context()
        # print(context)
        contextsplit = context1.split("\n")
        context = "\n".join(contextsplit[:-1])
        human_msg = contextsplit[-1]
        if len(human_msg.split()) < 5:
            return 0
        if "DEBUG" in human_msg:
            return 0
        # check for n-gram match with context
        if self.too_much_string_overlap(context, human_msg):
            return 0
        fixed_cand_scores = await self.get_fixed_cand_scores(context)
        # We award points on the score ranking, not the raw model score
        final_score, _model_score = await self.get_pos_human_msg(
            human_msg, context, fixed_cand_scores
        )
        return final_score

    async def role_playing_score_events(self, event):
        # Track event history, and award roleplaying score if appropriate.
        agent = event.actor
        if agent != self.target_node:
            return  # only for self actions
        if (
            event.__class__.__name__ == "SayEvent"
            or event.__class__.__name__ == "TellEvent"
        ):
            if agent._last_interaction_partner_id != None:
                agent2_id = agent._last_interaction_partner_id
                if not hasattr(agent, "_agent_interactions"):
                    agent._agent_interactions = {}
                if not hasattr(agent, "xp"):
                    agent.xp = 0
                    agent.reward_xp = 0

                if agent2_id not in agent._agent_interactions:
                    agent._agent_interactions[agent2_id] = 0

                stars = await self.score_conversation()
                agent._agent_interactions[agent2_id] += stars
                agent.xp += stars
                agent.reward_xp += stars / 4.0
                # Send star score message.
                if stars > 0:
                    xp_event_message = SystemMessageEvent(
                        agent,
                        [],
                        text_content="(You gained " + str(stars) + " XP!)",
                        event_data={
                            "event_type": "model_experience",
                            "reward": stars,
                            "target_event": event.event_id,
                        },
                    )
                    xp_event_message.execute(self.world)
                # if hasattr(self.world, 'debug'):
                #    print(str(agent) +" score: " + str(agent._agent_interactions[agent2_id]))
