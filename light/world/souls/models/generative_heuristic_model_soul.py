#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import time
import random
import asyncio
from collections import deque
from light.world.souls.on_event_soul import OnEventSoul
from light.graph.events.base import ErrorEvent
from light.graph.events.graph_events import TellEvent, SayEvent

from typing import TYPE_CHECKING, List

from light.graph.events.graph_events import EmoteEvent
from light.registry.model_pool import ModelTypeName

if TYPE_CHECKING:
    from light.registry.model_pool import ModelPool
    from light.graph.elements.graph_nodes import GraphAgent
    from light.world.world import World
    from light.graph.events.base import GraphEvent


MIN_TIME_BETWEEN_TURNS = 5
MAX_DIALOGUE_REPEAT_HISTORY = 50
MAX_ACTION_REPEAT_HISTORY = 4
ALLOW_INTERBOT_CHAT = False  # Only allow bots to answer humans
JITTER_TIME_AROUND_TURNS = 2
CHAT_DISENGAGE_CHANCE = 0.0 / 100.0
TAKE_ACTION_CHANCE = 1.0 / 5.0
SAFE_PHRASES = [
    "Let's talk about something else?",
    "Tell me something you don't know anything about.",
    "I'd like to talk about something different.",
    "Would you like to talk about something different.",
    "Can we change topics?",
    "How about a new conversation?",
]


class GenerativeHeuristicModelSoul(OnEventSoul):
    """
    The PartnerHeuristicModelSoul is a ModelSoul that uses two different
    models for acting and dialogue, and uses a heuristic for keeping track
    of the partner of a given agent (to prevent responding out of turn).

    This class represents a port of the initial implementation of a model
    in the LIGHT world, that used to be guided by the npc_models in the days
    before the OOGraph and GraphEvents
    """

    HAS_MAIN_LOOP = True

    def _init_with_models(self, model_pool) -> None:
        """
        Initialize required members of this soul for tracking the
        model and interactions with it.
        """
        self._pending_observations = []
        self._last_action_time = time.time() + self._get_random_time_offset()
        self.npc_dialog_model = model_pool.get_model(ModelTypeName.DIALOG)
        self.npc_act_model = model_pool.get_model(ModelTypeName.ACTION)
        self.reset_interaction_history(self.target_node)

    async def observe_event(self, event: "GraphEvent"):
        """
        On an observe event, the agent should append the event to the pending observations,
        and take a timestep (to ensure we respond in a timely manner)
        """
        if isinstance(event, ErrorEvent):
            return

        # NPC on_events + heuristics.
        super().set_interaction_partners_from_event(event)
        super().log_interaction_from_event(event)
        if self.target_node._dying:
            return
        await super().quest_events(event)
        did_event = super().on_events(event)
        did_trade = super().trade_event_heuristics(event)

        if event.actor == self.target_node:
            self._last_action_time = time.time() + self._get_random_time_offset()
            return

        if did_event or did_trade:
            # Already did a heuristic-based action
            return

        self._pending_observations.append(event)

        # The model may choose to do something in response to this action,
        # so don't wait for the timeout.
        await self._take_timestep()

    def _get_random_time_offset(self):
        """
        Produce a time offset based on JITTER_TIME_AROUND_TURNS to prevent
        model responses from being exactly periodic.
        """
        return random.random() * JITTER_TIME_AROUND_TURNS

    def npc_pick_non_repeating_action(self, act):
        """
        Only return an actual action if it's either hit or hasn't been done in
        the last turn
        """
        agent = self.target_node
        self.ensure_agent_has_action_history(agent)
        t = act
        if t in agent._action_history and not t.startswith("hit"):
            return None
        agent._action_history = [t]
        return t

    def ensure_agent_has_action_history(self, agent):
        if not hasattr(agent, "_action_history"):
            agent._action_history = []

    def ensure_agent_has_utterance_history(self, agent):
        if not hasattr(agent, "_utterance_history"):
            agent._utterance_history = []

    def dialogue_pick_non_repeating_response(self, act, partner):
        """
        Produce an act that is not in the dialogue history for this given
        agent.
        """
        self.ensure_agent_has_utterance_history(self.target_node)
        self.ensure_agent_has_utterance_history(partner)

        # Default to the top text, then try to find one that isn't in anyone's history
        found_utterance = act["text"]
        if "text_candidates" in act:  # Retrieval models can pick different candidates
            for t in act["text_candidates"]:
                if (
                    t not in self.target_node._utterance_history
                    and t not in partner._utterance_history
                    and self._utterance_to_speaker_name.get(t, "anon") != partner.name
                ):
                    found_utterance = t
                    break

        # This is the utterance selected to be said, append it to the
        # history for each partner
        self.target_node._utterance_history.append(found_utterance)
        partner._utterance_history.append(found_utterance)
        return found_utterance

    def get_last_turn_too_recent(self):
        return time.time() - self._last_action_time < MIN_TIME_BETWEEN_TURNS

    async def npc_action(self):
        """
        Agent attempt to take an action
        """
        if self.get_last_turn_too_recent() or random.random() > TAKE_ACTION_CHANCE:
            return

        # Get agents
        agent = self.target_node
        agent_id = agent.node_id
        partner = self.get_last_interaction_partner()
        if partner is None:
            return
        partner_name = None
        if partner != None:
            partner_name = partner.name

        quest_txt = None
        if not hasattr(agent, "quests") or agent.quests is None:
            agent.quests = []
        if len(agent.quests) > 0 and self.conversation_score(partner) > 5:
            quest_text = " " + agent.quests[0]["text"]

        context = self.build_dialog_context(quest_txt)

        context = "_task_typepicker\n" + context
        cands = ["dialog", "act", "emote"]
        msg = {
            "text": context,
            "episode_done": True,
            "label_candidates": cands,
            "eval_labels": [cands[0]],
        }
        self.npc_act_model.observe(msg)
        act = await self.npc_act_model.act()
        scores = {}
        for i in range(0, 3):
            scores[act["text_candidates"][i]] = float(act["sorted_scores"][i])
        # Heuristic modifiers to make it more reasonable:  dialog*0.9, act*1.0, emote*1.1
        scores["dialog"] *= 0.9
        scores["emote"] *= 1.1
        scores["act"] *= 1.04
        best_score = -1000
        best_type = "dialog"
        for k, v in scores.items():
            if v > best_score:
                best_score = v
                best_type = k

        if best_type == "act":
            context.replace("_task_typepicker", "_task_act")
            cands_set = self.world.get_possible_actions(agent_id)
            cands = []
            if len(cands_set) == 0:
                # nothing to do here.
                return False
            # remove some actions
            for c in cands_set:
                if (
                    c.startswith("get")
                    or c.startswith("give")
                    or c.startswith("drop")
                    or c.startswith("hug")
                    or c.startswith("equip")
                    or c.startswith("wield")
                    # c.startswith('examine') or
                    # c.startswith('look')
                    # c.startswith('folllow') or
                ):
                    cands.append(c)
            if len(cands) == 0:
                # nothing to do here.
                return False
            msg = {
                "text": context,
                "episode_done": True,
                "label_candidates": cands,
                "eval_labels": [cands[0]],
            }
            self.npc_act_model.observe(msg)
            act = await self.npc_act_model.act()
            act_text = act["text"]
            act_text = self.npc_pick_non_repeating_action(act_text)
            if act_text is None:
                return
            await self.world.parse_exec(agent_id, act_text)
            return True

        if best_type == "emote":
            context.replace("_task_typepicker", "_task_emote")
            cands = "ponder|nod|sigh|grin|frown|shrug|blush|smile|gasp|cry|groan|laugh|scream|dance|growl|stare|wink|nudge|pout|applaud|wave|yawn"
            cands = cands.split("|")
            msg = {
                "text": context,
                "episode_done": True,
                "label_candidates": cands,
                "eval_labels": [cands[0]],
            }
            self.npc_act_model.observe(msg)
            act = await self.npc_act_model.act()
            act_text = act["text"]
            act_text = self.npc_pick_non_repeating_action(act_text)
            if act_text is None:
                return
            do_event = EmoteEvent.construct_from_args(agent, targets=[], text=act_text)
            if do_event.__class__.__name__ != "ErrorEvent":
                do_event.execute(self.world)
            # self.log_act_history(act_text, is_self=True)
            return True
        return False

    async def npc_dialogue(self, obs=None):
        """
        Attempt to take a dialogue turn
        """
        agent = self.target_node
        agent_id = agent.node_id

        if obs is None:
            partner = self.get_last_interaction_partner(agent)
        else:
            partner = obs.actor
            partner_interactor_id = partner._last_interaction_partner_id
            if (
                isinstance(obs, SayEvent)
                and partner_interactor_id is not None
                and partner_interactor_id != agent_id
            ):
                # partner said something, but is interacting with someone else, so we don't reply.
                return
            # we are going to reply, so point both agents as having this as their last interaction.
            self.dialogue_switch_partner(agent, partner)

        # TODO refactor with is_human when human flag is refactored
        if not ALLOW_INTERBOT_CHAT and not partner.is_player:
            return

        quest_txt = None
        if hasattr(agent, "quests") or agent.quests is None:
            agent.quests = []
        if len(agent.quests) > 0 and self.conversation_score(partner) > 5:
            quest_text = " " + agent.quests[0]["text"]
        context = self.build_dialog_context(quest_txt)
        context = "_task_speech\n" + context

        # Add knowledge test (commented for now, as it didn't seem to work well)
        # contexts = context.split('\n')
        # contexts[-2] += " The milkman is to the south."
        # context = '\n'.join(contexts); print(context)
        # context = context.replace('_self_persona ', "_self_persona I believe the milk man is south of here. ")

        if obs is not None and obs.text_content.strip() == "DEBUG":
            # print debug information instead
            event = SayEvent(agent, target_nodes=[], text_content="DEBUG: " + context)
            event.skip_safety = True
            event.execute(self.world)
            return

        # Send to model to process
        msg = {"text": context, "episode_done": True}
        self.npc_dialog_model.observe(msg)
        act = await self.npc_dialog_model.act()

        act_text = self.dialogue_pick_non_repeating_response(act, partner)

        is_safe = await self.world.safety_classifier.is_safe(act_text)
        reply_event = TellEvent(agent, target_nodes=[partner], text_content=act_text, is_safe=is_safe)
        reply_event.execute(self.world)

    async def _take_timestep(self) -> None:
        """
        Attempt to take some actions based on any observations in the pending list
        """
        if self.get_last_turn_too_recent():
            return

        graph = self.world.oo_graph
        agent = self.target_node
        agent_id = agent.node_id
        agent.get_text()  # Clear the buffer, we use _pending_observations

        # possibly respond to talk requests
        curr_obs = []
        while len(self._pending_observations) > 0:
            curr_obs.append(self._pending_observations.pop(0))
        for obs in curr_obs:

            if isinstance(obs, SayEvent) or (
                isinstance(obs, TellEvent) and obs.target_nodes[0] == agent
            ):
                # Try goal dialog heuristic first, otherwise use normal dialog.
                if not self.tell_goal_heuristics(obs):
                    await self.npc_dialogue(obs)

        # possibly initiate talk request to someone in the room
        if self.get_last_interaction_partner(agent) is None:
            self.reset_interaction_history(agent)
            room = agent.get_room()
            agents = [x for x in room.get_contents() if x.agent]
            partner = random.choice(agents)
            partner_id = partner.node_id
            if (
                partner_id != agent_id
                and partner.get_prop("speed", 0) > 0
                and self.get_last_interaction_partner(partner) is None
            ):
                self.dialogue_switch_partner(agent, partner)
                try:
                    await self.npc_dialogue(None)
                except Exception as e:
                    print(f"Hit exception {e}")
                    import traceback

                    traceback.print_exc()
                return
        else:
            pass
            # possibly end interaction with existing interaction partner (if any)?
            # if random.random() < CHAT_DISENGAGE_CHANCE:
            # TODO: would need to reset both partners.
            # self.reset_interaction_history()

        # NPC heuristics: attack, random movement
        acted = super().timestep_actions()

        # Possibly act according to the transformer model
        if not acted:
            await self.npc_action()
