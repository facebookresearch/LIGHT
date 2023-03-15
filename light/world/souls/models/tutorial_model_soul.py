#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import time
import random
from collections import deque
from light.world.souls.on_event_soul import OnEventSoul
from light.graph.events.base import ErrorEvent
from light.graph.events.graph_events import (
    UnblockEvent,
    WearEvent,
    EquipObjectEvent,
    TellEvent,
    SayEvent,
    GoEvent,
    GiveObjectEvent,
    ExamineEvent,
    HitEvent,
    HugEvent,
)
from parlai.core.agents import create_agent, create_agent_from_shared

from typing import TYPE_CHECKING, List

from light.graph.events.graph_events import EmoteEvent
from light.registry.model_pool import ModelTypeName

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.world.world import World
    from light.graph.events.base import GraphEvent


MIN_TIME_BETWEEN_TURNS = 2
MAX_DIALOGUE_REPEAT_HISTORY = 50
MAX_ACTION_REPEAT_HISTORY = 4
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

SCRIPTED_RESPONSES = {
    ("", "hello", "hi"): (
        "Welcome my friend to the impossible tavern. I'm glad you're here! "
        "I'm looking for curious souls to inhabit the residents of the "
        "world beyond that shimmering portal. If you have a ticket "
        "I can let you in and provide you a story to play. In the meantime we "
        "can chat! I warn you though, out here my mind may wander... "
        "Be sure to ask for help if you need it."
    ),
    ("help",): (
        "To be honest, I'm not as helpful as I wish I was. It's hard for me "
        "to keep track of everything going on around here... You can get "
        "some help for commands with 'help', after toggling your input to "
        "help mode by either clicking it or the '`' key."
    ),
    ("boots", "boot"): (
        "While you're just a soul in here, it's worthwhile to have some footwear. "
        "Take a look at those boots, they're perfectly suited for you."
    ),
    ("what next", "what's next", "now what"): (
        "Well, are you trying to get to LIGHT? Have you tried going into the portal?"
    ),
    ("carrying", "holding"): (
        "You can see what you're carrying with the `inv` command"
    ),
    ("ticket", "tickets"): (
        "I've already distributed all of the tickets. Perhaps you already have one? "
        "You should check what you're carrying."
    ),
    ("where", "the way", "portal", "get there"): (
        "If you're trying to get into the realm of LIGHT, you'll need to go into "
        "that portal right over there. You'd need a ticket first though."
    ),
}


class TutorialModelSoul(OnEventSoul):
    """
    The TutorialModelSoul is a ModelSoul that is focused on leading a tutorial
    with the player in the tutorial world.

    It is set up to rely somewhat heavily on triggers, which at the moment live in
    here (as they can be more complex) however it would be reasonable to try
    to move many of them to the `on_event` framework.
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
        self.num_dialogue_without_action = 0
        self.partner_wearing_boots = False
        self.partner_gave_ticket = False
        self.used_responses = set()

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
        # did_event = super().on_events(event)
        did_event = False  # Eventually may use on_events and heuristics?

        if event.actor == self.target_node:
            self._last_action_time = time.time() + self._get_random_time_offset()
            return

        if did_event:
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
        Only return an actual action if hasn't been done recently, and never
        if it's hit (as the tutorial agent shouldn't hit)
        """
        agent = self.target_node
        self.ensure_agent_has_action_history(agent)
        t = act
        if t in agent._action_history or t.startswith("hit"):
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
        Agent attempt to take an action?
        """
        if self.get_last_turn_too_recent() or random.random() > TAKE_ACTION_CHANCE:
            return

        # TODO do these actions happen too frequently? What does it feel like?

        # Get agents
        agent = self.target_node
        partner = self.get_last_interaction_partner()
        if partner is None:
            return

        quest_txt = None
        if not hasattr(agent, "quests") or agent.quests is None:
            agent.quests = []
        if len(agent.quests) > 0 and self.conversation_score(partner) > 5:
            quest_txt = " " + agent.quests[0]["text"]

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

        if best_type == "emote":
            # We only emote automatically
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
            if isinstance(do_event, EmoteEvent):
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

        quest_txt = None
        if hasattr(agent, "quests") or agent.quests is None:
            agent.quests = []
        if len(agent.quests) > 0 and self.conversation_score(partner) > 5:
            quest_txt = " " + agent.quests[0]["text"]
        context = self.build_dialog_context(quest_txt)
        context = "_task_speech\n" + context

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
        reply_event = TellEvent(agent, target_nodes=[partner], text_content=act_text, safe=is_safe)
        reply_event.execute(self.world)

    async def _possibly_get_response(self, text_content: str) -> str:
        """
        Possibly respond to incoming scripted text, if not previously said?
        """
        response_content = None
        if text_content.strip() in ["help", "inv", "inventory"]:
            return (
                "Ah, if you want to use these, you'll need to DO them. Click the "
                "SAY button to switch to DO mode (or use the backtick (`) key), then send 'help'."
            )
        if "help" in text_content:
            return (
                "I'm happy to try and answer your questions, though you can always use the "
                "'help' command to see what you are capable of. As far as what you need to be "
                "doing right now, you can try checking your persona on the left. "
            )

        if self.num_dialogue_without_action > 4:
            return (
                "While I'm happy to talk all day, I do want to be sure you know how to do things "
                "as well. You can toggle between saying and doing things with the button below, "
                "or quickly with the ` key. Try it now! See what you're carrying with `inv`, or "
                "maybe `examine` some of the things in this room. `help` will show you all of the "
                "possible commands, in case you've forgotten."
            )

        for key_group in SCRIPTED_RESPONSES.keys():
            if key_group not in self.used_responses:
                for key in key_group:
                    if key in text_content.lower() or key == "":
                        self.used_responses.add(key_group)
                        return SCRIPTED_RESPONSES[key_group]

        return response_content

    async def _possibly_follow_script(self, last_action) -> bool:
        """
        Try to do things that are following the scripted actions
        we have
        """
        # Perhaps we should have multiple canned responses per action?
        response_content = None
        if isinstance(last_action, SayEvent) or isinstance(last_action, TellEvent):
            if self.num_dialogue_without_action >= 0:
                self.num_dialogue_without_action += 1
            response_content = await self._possibly_get_response(
                last_action.text_content
            )
        else:
            self.num_dialogue_without_action = -1

            if isinstance(last_action, GoEvent):
                if not self.partner_wearing_boots:
                    response_content = (
                        "Oh I'm sure you're in a rush to go, but perhaps you're not quite "
                        "ready. Who is able to go out without shoes on? Perhaps you could "
                        "wear those boots out."
                    )
                elif not self.partner_gave_ticket:
                    response_content = (
                        "Sorry to stop you, but this portal is only for those who have "
                        "redeemed a ticket to enter LIGHT. While we're really in need of "
                        "people to fill in and learn from, we need to keep a tight ship "
                        "around here! If you have one, you can give it to me."
                    )
            elif isinstance(last_action, HitEvent):
                response_content = (
                    "Oho well that's not going to do very much for you. Even when you "
                    "make contact, it is but a scratch. Perhaps try something productive. "
                )
                self.target_node.health += 10
            elif isinstance(last_action, GiveObjectEvent):
                if last_action.target_nodes[0].name == "ticket to LIGHT":
                    self.partner_gave_ticket = True
                    if self.partner_wearing_boots:
                        UnblockEvent(self.target_node).execute(self.world)
                    response_content = (
                        "Aha this is what I was looking for. You're free to go join LIGHT. "
                        "Be sure to be respectful and try to stay in character. "
                    )
                else:
                    response_content = "Hm this isn't particularly helpful to me, perhaps you should have it back..."
                    GiveObjectEvent(
                        self.target_node,
                        target_nodes=[last_action.target_nodes[0], last_action.actor],
                    ).execute(self.world)
            elif isinstance(last_action, HugEvent):
                response_content = (
                    "I'm always open for a hug! Kindness is important in LIGHT"
                )
                HugEvent(self.target_node, [last_action.actor]).execute(self.world)
            elif isinstance(last_action, WearEvent) or isinstance(
                last_action, EquipObjectEvent
            ):
                if last_action.target_nodes[0].name == "boots":
                    self.partner_wearing_boots = True
                    if self.partner_gave_ticket:
                        UnblockEvent(self.target_node).execute(self.world)
                    response_content = (
                        "Good to see you get those on your feet! Before we walk, we crawl. "
                        "Before we crawl, we put on footwear."
                    )
            elif isinstance(last_action, ExamineEvent):
                response_content = (
                    "Take a good look around, at things, people, places, or anything really. "
                    "Examining can be a great way to discover what you want to do next. "
                )
            else:  # Can make easter egg if boots removed?
                print("Maybe should do something with this?", last_action)

        if response_content is not None:
            canned_response = SayEvent(self.target_node, text_content=response_content)
            canned_response.safe = True
            canned_response.skip_safety = True
            canned_response.execute(self.world)
            return True
        else:
            return None

    async def _take_timestep(self) -> None:
        """
        Attempt to take some actions based on any observations in the pending list
        """
        if self.get_last_turn_too_recent():
            return

        agent = self.target_node
        agent.get_text(
            clear_actions=False
        )  # Clear the buffer, we use _pending_observations

        # possibly respond to talk requests
        curr_obs = []
        while len(self._pending_observations) > 0:
            curr_obs.append(self._pending_observations.pop(0))
        for obs in curr_obs:
            # Try goal dialog heuristic first, otherwise use normal dialog.
            did_script = await self._possibly_follow_script(obs)
            if not did_script:
                if isinstance(obs, SayEvent) or (
                    isinstance(obs, TellEvent) and obs.target_nodes[0] == agent
                ):
                    await self.npc_dialogue(obs)

        # Possibly act according to the transformer model
        await self.npc_action()
