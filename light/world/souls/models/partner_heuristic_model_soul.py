#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import time
import random
from collections import deque
from light.world.souls.on_event_soul import OnEventSoul
from light.graph.events.base import ErrorEvent
from light.graph.events.graph_events import TellEvent, SayEvent
from parlai.core.agents import create_agent_from_shared

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.graph.world.world import World
    from light.graph.events.base import GraphEvent


MIN_TIME_BETWEEN_TURNS = 5
MAX_DIALOGUE_REPEAT_HISTORY = 50
MAX_ACTION_REPEAT_HISTORY = 4
ALLOW_INTERBOT_CHAT = False  # Only allow bots to answer humans
JITTER_TIME_AROUND_TURNS = 2
CHAT_DISENGAGE_CHANCE = 5.0 / 100.0
TAKE_ACTION_CHANCE = 1.0 / 5.0
SAFE_PHRASES = [
  "Let's talk about something else?",
  "Tell me something you don't know anything about.",
  "I'd like to talk about something different.",
  "Would you like to talk about something different.",
  "Can we change topics?",
  "How about a new conversation?",
]


class PartnerHeuristicModelSoul(OnEventSoul):
    """
    The PartnerHeuristicModelSoul is a ModelSoul that uses two different
    models for acting and dialogue, and uses a heuristic for keeping track
    of the partner of a given agent (to prevent responding out of turn).
    
    This class represents a port of the initial implementation of a model
    in the LIGHT world, that used to be guided by the npc_models in the days
    before the OOGraph and GraphEvents
    """

    HAS_MAIN_LOOP = True

    @classmethod
    def load_speech_model(
        cls, parser, speech_model_path, speech_cands_path, agent_to_utterance_path,
    ):
        """
        Load up the speech model for use with this class
        """
        # Load speech model
        speech_args = [
            "-mf",
            speech_model_path,
            "-ecands",
            "fixed",
            "--ignore-bad-candidates",
            "True",
            "-fcp",
            speech_cands_path,
        ]
        speech_opt, _unknown = parser.parse_and_process_known_args(args=speech_args)
        speech_opt["override"] = {
            "eval_candidates": "fixed",
            "fixed_candidates_path": speech_cands_path,
        }
        speech_opt["interactive_mode"] = True
        return create_agent(speech_opt, requireModelExists=True)

    @classmethod
    def load_models(
        cls, speech_model_path, speech_cands_path, agent_to_utterance_path, act_model_path,
    ):
        """
        Load up and create possible shared models for use with this class
        """
        # TODO refactor with some kind of model-loading standard for model souls?
        from parlai.core.params import ParlaiParser
        from parlai.core.agents import create_agent

        parser = ParlaiParser(True, True, "")

        speech_model = cls.load_speech_model(
            parser, speech_model_path, speech_cands_path, agent_to_utterance_path,
        )

        # Load speaker stop list
        with open(agent_to_utterance_path, "r") as map_file:
            utt_map_lines = map_file.readlines()

        utterance_to_speaker_map = {}
        for d in utt_map_lines:
            i1 = d.find(":")
            name = d[1:i1]
            utt = d[i1 + 1 : -1]
            utterance_to_speaker_map[utt] = name

        # Load action model
        args = [
            "-mf",
            act_model_path,
            "-ecands",
            "inline",
            "--ignore-bad-candidates",
            "True",
        ]
        act_opt, _unknown = parser.parse_and_process_known_args(args=args)

        act_opt['override'] = {'eval_candidates': 'inline', 'ignore_bad_candidates': 'True'}
        act_opt["interactive_mode"] = True
        act_opt["ignore_bad_candidates"] = True
        action_model = create_agent(act_opt, requireModelExists=True)

        return {
            "utterance_to_speaker_name": utterance_to_speaker_map,
            "shared_dialog_model": speech_model.share(),
            "shared_action_model": action_model.share(),
        }

    def log_act_history(self, act_text, is_self):
        """Log an act to the act histories"""
        act_hist = self._dialogue_history['act']
        speech_act_hist = self._dialogue_history['speech+act']
        pre_token = "_self_act" if is_self else "_partner_act"
        act_turn = f"{pre_token} {act_text}\n"
        act_hist.append(act_turn)
        speech_act_hist.append(act_turn)
    
    def log_speech_history(self, act_text, is_self):
        """Log a speech turn to the act histories"""
        speech_hist = self._dialogue_history['speech']
        speech_act_hist = self._dialogue_history['speech+act']
        pre_token = "_self_say" if is_self else "_partner_say"
        act_turn = f"{pre_token} {act_text}\n"
        speech_hist.append(act_text + '\n')
        speech_act_hist.append(act_turn)

    def _clear_dialogue_history(self) -> None:
        """Empty the dialogue history for both speech and act models"""
        # Note - at the moment the current format is that the speech dict is 
        # newline seperated history turns just containing the text, while
        # both act and speech and act add 
        self._dialogue_history = {'speech': [], 'act': [], 'speech+act': []}

    def _init_with_models(self, models) -> None:
        """
        Initialize required members of this soul for tracking the 
        model and interactions with it.
        """
        self._pending_observations = []
        self._last_action_time = time.time() + self._get_random_time_offset()
        self._utterance_to_speaker_name = models['utterance_to_speaker_name']
        self.npc_model = create_agent_from_shared(models['shared_dialog_model'])
        self.npc_act_model = create_agent_from_shared(models['shared_action_model'])
        self._clear_dialogue_history()

    async def observe_event(self, event: "GraphEvent"):
        """
        On an observe event, the agent should append the event to the pending observations,
        and take a timestep (to ensure we respond in a timely manner)
        """
        if isinstance(event, ErrorEvent):
           return

        # NPC on_events + heuristics.
        super().on_events(event)

        if event.actor == self.target_node:
            self._last_action_time = time.time() + self._get_random_time_offset()
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

    def _ensure_agent_has_utterance_history(self, agent):
        """Create the _utterance_history attribute for a GraphAgent if it doesn't exist"""
        if not hasattr(agent, "_utterance_history"):
            agent._utterance_history = deque(maxlen=MAX_DIALOGUE_REPEAT_HISTORY)

    def _ensure_agent_has_action_history(self, agent):
        """Create the _action_history attribute for a GraphAgent if it doesn't exist"""
        if not hasattr(agent, "_action_history"):
            agent._action_history = deque(maxlen=MAX_ACTION_REPEAT_HISTORY)

    def dialogue_clear_partner(self):
        """
        Clear this Soul's set dialogue partner, possibly clearing
        the partner if they still point to it.
        """
        # how a dialogue agent deals with moving location
        self._clear_dialogue_history()

        # remove interaction partner links:
        agent = self.target_node
        partner_id = self.get_last_interaction_partner(agent)
        agent._last_interaction_partner_id = None
        if partner_id is None:
            return

        # If the partner node is still focused here, clear
        partner = self.world.oo_graph.get_node(partner_id)
        if self.get_last_interaction_partner(partner) == agent.node_id:
            partner._last_interaction_partner_id = None

    def npc_pick_non_repeating_action(self, act):
        """
        Only return an actual action if it's either hit or hasn't been done in
        the last 4 turns
        """
        self._ensure_agent_has_action_history(self.target_node)
        t = act["text_candidates"][0]

        # Hit actions are allowed to repeat because we expect such
        # behavior in a combat setting
        if t not in self.target_node._action_history or t.startswith("hit"):
            self.target_node._action_history.append(t)
            return t
        # If the top action was too recent, let's do nothing.
        return None

    def dialogue_pick_non_repeating_response(self, act, partner):
        """
        Produce an act that is not in the dialogue history for this given
        agent.
        """
        self._ensure_agent_has_utterance_history(self.target_node)
        self._ensure_agent_has_utterance_history(partner)

        # Default to the top text, then try to find one that isn't in anyone's history
        found_utterance = act['text']
        if 'text_candidates' in act:  # Retrieval models can pick different candidates
            for t in act['text_candidates']:
                if (
                    t not in self.target_node._utterance_history
                    and t not in partner._utterance_history
                    and self._utterance_to_speaker_name.get(t, 'anon') != partner.name
                ):
                    found_utterance = t

        # This is the utterance selected to be said, append it to the
        # history for each partner
        self.target_node._utterance_history.append(found_utterance)
        partner._utterance_history.append(found_utterance)
        return found_utterance

    def npc_build_context(self, partner_name=None):
        """
        Build the full context for this Soul's model
        """
        agent = self.target_node
        room = agent.get_room()
        txt = "_setting_name " + room.name + "\\n"
        txt += "_setting_desc " + room.desc + "\\n"
        if partner_name is not None:
            txt += "_partner_name " + partner_name + "\\n"
        txt += "_self_name " + agent.name + "\\n"
        txt += "_self_persona " + agent.persona + "\\n"
        return txt

    def get_last_turn_too_recent(self):
        return time.time() - self._last_action_time < MIN_TIME_BETWEEN_TURNS

    def npc_action(self):
        """
        Agent attempt to take an action
        """
        if self.get_last_turn_too_recent() or random.random() > TAKE_ACTION_CHANCE:
            return

        # Self action history
        speech_act_hist = self._dialogue_history['speech+act']

        # Get agents
        agent = self.target_node
        agent_id = agent.node_id
        partner_id = self.get_last_interaction_partner(agent)
        if partner_id != None:
            partner = self.world.oo_graph.get_node(partner_id)
            partner_name = partner.name
        else:
            partner_name = None

        txt = self.npc_build_context(partner_name)
        for d in speech_act_hist:
            txt += d
        cands = self.world.get_possible_actions(agent_id)
        if len(cands) == 0:
            # nothing to do here.
            return
        msg = {
            "text": txt,
            "episode_done": True,
            'label_candidates': cands,
            'eval_labels': [cands[0]],
        }
        self.npc_act_model.observe(msg)
        act = self.npc_act_model.act()
        act_text = self.npc_pick_non_repeating_action(act)
        if act_text is None:
            return

        self.log_act_history(act_text, is_self=True)
        self.world.parse_exec(agent_id, act_text)

    def npc_dialogue(self, obs=None):
        """
        Attempt to take a dialogue turn
        """
        agent = self.target_node
        agent_id = agent.node_id

        if obs is None:
            partner_id = self.get_last_interaction_partner(agent)
            if partner_id is None:
                return
            partner = self.world.oo_graph.get_node(partner_id)
        else:
            partner = obs.actor
            partner_id = partner.node_id
            partner_interactor_id = self.get_last_interaction_partner(partner)
            if (
                isinstance(obs, SayEvent)
                and partner_interactor_id is not None
                and partner_interactor_id != agent_id
            ):
                # partner said something, but is interacting with someone else, so we don't reply.
                return
            # we are going to reply, so point both agents as having this as their last interaction.
            self.set_interaction_partner(partner)


        # TODO refactor with is_human when human flag is refactored
        if not ALLOW_INTERBOT_CHAT and not partner._human:
            return

        if obs is not None and obs.text_content == "DEBUG":
            # print debug information instead
            event = SayEvent(agent, target_nodes=[], text_content=txt)
            event.execute(self.world)
            return

        # add dialogue to history
        if obs is not None and obs.is_dialogue_safe(obs.text_content):
            self.log_speech_history(obs.text_content, is_self=False)
        elif obs is not None:
            # text content was not safe
            last_msg = random.choice(SAFE_PHRASES)
            self.log_speech_history(last_msg, is_self=False)

        speech_hist = self._dialogue_history['speech']

        partner_name = partner.name
        txt = self.npc_build_context(partner_name)
        for d in speech_hist:
            txt += d

        # Send to model to process
        msg = {"text": txt, "episode_done": True}
        self.npc_model.observe(msg)
        act = self.npc_model.act()

        print("Got model speech act", act)

        act_text = self.dialogue_pick_non_repeating_response(act, partner)

        reply_event = TellEvent(agent, target_nodes=[partner], text_content=act_text)
        reply_event.execute(self.world)

        self.log_speech_history(act_text)

    def get_last_interaction_partner(self, node: "GraphAgent"):
        """
        Get the last interaction partner labelled for the given node, if it exists
        """
        if hasattr(node, "_last_interaction_partner_id"):
            last_partner_id = node._last_interaction_partner_id
            if last_partner_id is None:
                return None
            last_partner_node = self.world.oo_graph.get_node(last_partner_id)
            if last_partner_node is None or last_partner_node.get_room() != node.get_room():
                return None  # last partner is no longer present.
            return last_partner_id
        else:
            return None

    def set_interaction_partner(self, partner_node: "GraphAgent"):
        """
        Set the last interaction partner for this agent and the
        partner, clearing previous partners if they are set
        """
        for node in [self.target_node, partner_node]:
            un_partner_id = self.get_last_interaction_partner(node)
            if un_partner_id is not None:
                un_partner_node = self.world.oo_graph.get_node(un_partner_id)
                if un_partner_node is not None:
                    un_partner_node._last_interaction_partner_id = None
        self.target_node._last_interaction_partner_id = partner_node.node_id
        partner_node._last_interaction_partner_id = self.target_node.node_id

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
                try:
                    self.npc_dialogue(obs)
                except e:
                    print(f"Hit exception {e}")
                    import traceback
                    traceback.print_exc()
                return

        # possibly initiate talk request to someone in the room
        if self.get_last_interaction_partner(agent) is None:
            self._clear_dialogue_history()
            room = agent.get_room()
            agents = [x for x in room.get_contents() if x.agent]
            partner = random.choice(agents)
            partner_id = partner.node_id
            if (
                partner.node_id != agent_id
                and partner.get_prop("speed", 0) > 0
                and self.get_last_interaction_partner(partner) is None
            ):
                self.set_interaction_partner(partner)
                self.npc_dialogue(None)
                return
        else:
            # possibly end interaction with existing interaction partner (if any)?
            if random.random() < CHAT_DISENGAGE_CHANCE:
                self.dialogue_clear_partner()


        # NPC heuristics, etc.
        super().timestep_actions()

        if False:
            # random movement for npcs..
            if random.randint(0, 1000) < agent.speed:
                go_events = self.world.get_possible_events(agent_id, use_actions=["go"])
                if len(go_events) > 0:
                    go_event = random.choice(go_events)
                    go_event.execute(self.world)
                    return

            # possibly act according to the bert model
            self.npc_action()
