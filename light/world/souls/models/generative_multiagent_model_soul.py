#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import time
import random
import asyncio
import requests
import json
from collections import deque
from light.world.souls.on_event_soul import OnEventSoul
from light.graph.events.base import ErrorEvent
from light.graph.events.graph_events import (
    TellEvent,
    SayEvent,
    WhisperEvent,
    SpeechEvent,
)
from light.graph.elements.graph_nodes import GraphAgent, GraphRoom

from typing import TYPE_CHECKING, List, TypedDict, Dict, Set, Any, Optional

from light.graph.events.graph_events import EmoteEvent
from light.registry.model_pool import ModelTypeName

if TYPE_CHECKING:
    from light.registry.model_pool import ModelPool
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


MAX_DIALOGUE_HISTORY = 30


class SharedRoomAgentEntry(TypedDict):
    room_id: str
    last_request_time: float
    last_response_time: float
    last_response: Optional[Dict[str, Any]]
    observed_times: Set[float]
    dialogue_history: List[Dict[str, Any]]


room_agent_mapper: Dict[str, SharedRoomAgentEntry] = {}


class GenerativeMultiagentModelSoul(OnEventSoul):
    """
    The PartnerMultiagentModelSoul is a ModelSoul that uses two different
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
        self.reset_interaction_history(self.target_node)

    def log_interaction_to_room(self, event: "GraphEvent"):
        room = event.room
        room_details = room_agent_mapper[room.node_id]

        if event.event_time in room_details["observed_times"]:
            return
        room_details["observed_times"].add(event.event_time)
        evt = {
            "actor": event.actor.name,
            "actor_id": event.actor.node_id,
            "event_time": event.event_time,
        }

        if isinstance(event, SpeechEvent) and not event.safe:
            evt["action"] = f"*Mumbles something incomprehensible*"
            room_details["dialogue_history"].append(evt)
        elif isinstance(event, TellEvent):
            assert event.text_content is not None
            evt["action"] = f"*Tells {event.target_nodes[0].name}* {event.text_content}"
            room_details["dialogue_history"].append(evt)
        elif isinstance(event, SayEvent):
            assert event.text_content is not None
            evt["action"] = event.text_content
            room_details["dialogue_history"].append(evt)
        elif isinstance(event, WhisperEvent):
            assert event.text_content is not None
            evt[
                "action"
            ] = f"*Whispers to {event.target_nodes[0].name}* {event.text_content}"
            room_details["dialogue_history"].append(evt)

        if True:  # log events
            act_events = [
                "EmoteEvent",
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
            if event.__class__.__name__ in act_events:
                text = event.to_canonical_form()
                evt["action"] = f"*{text}*"
                room_details["dialogue_history"].append(evt)
        room_details["dialogue_history"] = room_details["dialogue_history"][
            -MAX_DIALOGUE_HISTORY:
        ]

    async def observe_event(self, event: "GraphEvent"):
        """
        On an observe event, the agent should append the event to the pending observations,
        and take a timestep (to ensure we respond in a timely manner)
        """
        if isinstance(event, ErrorEvent):
            return

        room = event.room

        if event is not None and event.text_content.strip() == "DEBUG":
            # print debug information instead
            new_event = SayEvent(
                self.target_node,
                target_nodes=[],
                text_content="DEBUG: " + self.get_multi_context(room),
            )
            new_event.skip_safety = True
            new_event.execute(self.world)
            return

        if room.node_id not in room_agent_mapper:
            room_agent_mapper[room.node_id] = {
                "dialogue_history": [],
                "last_request_time": 0,
                "last_response": None,
                "last_response_time": 0,
                "room_id": room.node_id,
                "observed_times": set(),
            }

        self.log_interaction_to_room(event)

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

    def dialogue_pick_non_repeating_response(self, act, history):
        """
        Produce an act that is not in the dialogue history for this given
        agent.
        """

        # Default to the top text, then try to find one that isn't in anyone's history
        found_utterance = act["text"]
        if "text_candidates" in act:  # Retrieval models can pick different candidates
            for t in act["text_candidates"]:
                if t not in history:
                    found_utterance = t
                    break

        # This is the utterance selected to be said, append it to the
        # history for each partner
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
        scores["emote"] *= 0.4
        scores["act"] *= 0.6
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
            if not isinstance(do_event, ErrorEvent):
                do_event.execute(self.world)
            # self.log_act_history(act_text, is_self=True)
            return True
        return False

    def flatten_personas(
        self,
        agents: List[GraphAgent],
        delim: str = "\n",
    ) -> str:
        persona_str = []
        persona_str.append("__personas__")
        persona_str.extend([f"{a.name}: {a.persona}" for a in agents])
        persona_str.append("__end-personas__")
        return delim.join(persona_str)

    def flatten_location(self, location: GraphRoom, delim: str = "\n") -> str:
        location_str_parts = [
            "__location__",
            f"{location.name}: {location.desc}",
            "__end-location__",
        ]
        return delim.join(location_str_parts)

    def get_multi_context(self, room: GraphRoom, delim: str = "\n"):
        context = room_agent_mapper[room.node_id]["dialogue_history"]
        agents = [a for a in room.get_contents() if isinstance(a, GraphAgent)]
        context_chunks = [
            self.flatten_personas(agents),
            self.flatten_location(room),
        ]
        context_chunks.extend([f"{c['actor']}: {c['action']}" for c in context])
        return delim.join(context_chunks)

    async def make_request(self, act):
        TARGET = "18.217.17.25"
        PORT = 6010
        address = f"http://{TARGET}:{PORT}/completions"
        data = {
            "prompt": [act.strip() + "\n"],
            "min_tokens": 1,
            "max_tokens": 80,
            "top_p": 0.9,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": "'Bearer chatbot'",
        }
        r = requests.post(address, data=json.dumps(data), headers=headers)
        return {"text": r.json()["choices"][0]["text"]}

    async def request_dialogue(self, room):
        """Request dialogue from the multiagent model for this agent"""
        mapper = room_agent_mapper[room.node_id]
        last_submit_time = mapper["dialogue_history"][-1]["event_time"]
        if mapper["last_request_time"] < last_submit_time:
            # We are the submitting thread, let's make a request
            act = await self.make_request(self.get_multi_context(room))
            actor, res = act["text"].strip().split(":", 1)
            act["text"] = res.strip()
            mapper["last_response"] = {"actor": actor.strip(), "action": act}
        else:
            while mapper["last_response_time"] < last_submit_time:
                await asyncio.sleep(0.1)

        if mapper["last_request_time"] > last_submit_time:
            return  # a new message got in before we could respond

        last_response = mapper["last_response"]
        if last_response is None:
            return None  # someone already consumed this
        elif last_response["actor"].lower() == self.target_node.name.lower():
            # We are the agent, return
            mapper["last_response"] = None  # consume the response
            return last_response["action"]
        return None  # we are not the speaker

    async def npc_dialogue(self, obs=None):
        """
        Attempt to take a dialogue turn
        """
        agent = self.target_node
        room = agent.get_room()
        agent_id = agent.node_id

        act = await self.request_dialogue(room)
        if act is None:
            return

        # Send to model to process
        act_text = self.dialogue_pick_non_repeating_response(act, partner)

        is_safe = await self.world.safety_classifier.is_safe(act_text)
        reply_event = SayEvent(agent, text_content=act_text, safe=is_safe)
        reply_event.execute(self.world)

    async def _take_timestep(self) -> None:
        """
        Attempt to take some actions based on any observations in the pending list
        """
        if self.get_last_turn_too_recent():
            return

        agent = self.target_node
        agent.get_text()  # Clear the buffer, we use _pending_observations
        room = agent.get_room()

        # possibly respond to talk requests, if any players
        if any(
            [isinstance(l, GraphAgent) and l.is_player for l in room.get_contents()]
        ):
            await self.npc_dialogue()

        # NPC heuristics: attack, random movement
        acted = super().timestep_actions()

        # Possibly act according to the transformer model
        if not acted:
            await self.npc_action()
