#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import time
from collections import deque
from light.world.souls.model_soul import ModelSoul
from light.graph.events.graph_events import TellEvent, SayEvent
from parlai.core.agents import create_agent_from_shared

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.graph.world.world import World
    from light.graph.events.base import GraphEvent


MIN_TIME_BETWEEN_TURNS = 5
ALLOW_INTERBOT_CHAT = False  # Only allow bots to answer humans

class PartnerHeuristicModelSoul(ModelSoul):
    """
    A ModelSoul is responsible for passing it's observations back to
    a model that decides what to do. This class will likely have utility
    methods for loading shared models and some shared behavior between
    classes, for now is a stub.
    """

    HAS_MAIN_LOOP = True

    @staticmethod
    def load_models(
        speech_model_path, 
        speech_cands_path, 
        agent_to_utterance_path, 
        act_model_path,
    ):
        """
        Load up and create possible shared models for use with this class
        """
        from parlai.core.params import ParlaiParser
        from parlai.core.agents import create_agent

        parser = ParlaiParser(True, True, '')

        # Load speech model
        speech_args = [
            '-mf',
            speech_model_path,
            '-ecands',
            'fixed',
            '--ignore-bad-candidates',
            'True',
            '-fcp',
            speech_cands_path,
        ]
        speech_opt, _unknown = parser.parse_and_process_known_args(args=speech_args)
        speech_opt['override'] = {
            'eval_candidates': 'fixed',
            'fixed_candidates_path': speech_cands_path,
        }
        speech_opt['interactive_mode'] = True
        speech_model = create_agent(speech_opt, requireModelExists=True)

        # Load speaker stop list
        fname = LIGHT_MODEL_ROOT + 'agent_to_utterance_trainset.txt'
        with open(agent_to_utterance_path, "r") as map_file:
            utt_map_lines = map_file.readlines()

        utterance_to_speaker_map = {}
        for d in utt_map_lines:
            i1 = d.find(':')
            name = d[1:i1]
            utt = d[i1 + 1 : -1]
            utterance_to_speaker_map[utt] = name

        # Load action model
        args = [
            '-mf',
            act_model_path,
            '-ecands',
            'inline',
            '--ignore-bad-candidates',
            'True',
        ]
        act_opt, _unknown = parser.parse_and_process_known_args(args=args)
        act_opt['override'] = {'eval_candidates': 'inline', 'ignore_bad_candidates': 'True'}
        act_opt['interactive_mode'] = True
        act_opt['ignore_bad_candidates'] = True
        action_model = create_agent(act_opt, requireModelExists=True)

        return = {
            'utterance_to_speaker_name': utterance_to_speaker_map,
            'shared_dialog_model': speech_model.share(),
            'shared_action_model': action_model.share(),
        }

    def _init_with_models(self, models) -> None:
        """
        Initialize required members of this soul for tracking the 
        model and interactions with it.
        """
        self._pending_observations = []
        self._last_action_time = time.time() + random.random() * 2
        self._dialogue_history = {}
        self._utterance_to_speaker_name = models['utterance_to_speaker_name']
        self.npc_model = create_agent_from_shared(models['shared_dialog_model'])
        self.npc_act_model = create_agent_from_shared(models['shared_action_model'])

    async def observe_event(self, event: "GraphEvent"):
        """
        On an observe event, the agent should append the event to the pending observations,
        and take a timestep (to ensure we respond in a timely manner)
        """
        if event.actor == self.target_node:
            self._last_action_time = time.time() + random.random() * 2
            return
        
        self._pending_observations.append(event)

        # The model may choose to do something in response to this action, 
        # so don't wait for the timeout.
        await self._take_timestep()

    def _ensure_agent_has_utterance_history(self, agent):
        """Create the _utterance_history attribute for a GraphAgent if it doesn't exist"""
        if not hasattr(agent, '_utterance_history'):
            agent._utterance_history = deque(maxlen=50)

    def _ensure_agent_has_action_history(self, agent):
        """Create the _action_history attribute for a GraphAgent if it doesn't exist"""
        if not hasattr(agent, '_action_history'):
            agent._action_history = deque(maxlen=4)

    def dialogue_clear_partner(self):
        """
        Clear this Soul's set dialogue partner, possibly clearing
        the partner if they still point to it.
        """
        # how a dialogue agent deals with moving location
        self._dialogue_history = {}

        # remove interaction partner links:
        agent = self.target_node
        partner_id = self.get_last_interaction_partner(agent)
        agent._last_interaction_partner_id = None
        if partner_id is None:
            continue

        # If the partner node is still focused here, clear
        partner = self.world.oo_graph.get_node(partner_id)
        if self.get_last_interaction_partner(partner) == agent.node_id:
            partner._last_interaction_partner_id = None

    def npc_pick_non_repeating_action(self, act):
        """
        Only return an actual action if it's either hit or hasn't been done in
        the last 4 turns
        """
        self._ensure_agent_has_dialogue_history(self.target_node)
        t = act['text_candidates'][0]
        if t not in self.target_node._action_history or t.startswith('hit'):
            self.target_node._action_history.append(t)
            return t
        # If the top action was too recent, let's do nothing.
        return 'wait'

    def dialogue_pick_non_repeating_response(self, act, partner):
        """
        Produce an act that is not in the dialogue history for this given
        agent.
        """
        self._ensure_agent_has_utterance_history(self.target_node)
        self._ensure_agent_has_utterance_history(partner)
        for t in act['text_candidates']:
            if (
                t not in self.target_node._utterance_history
                and t not in partner._utterance_history
                and self._utterance_to_speaker_name.get(t, 'anon') != partner.name
            ):
                # This is the utterance selected to be said, append it to the
                # history for each partner
                self.target_node._utterance_history.append(t)
                partner._utterance_history.append(t)
                return t

        # couldn't find a valid response, so just return the top one.
        return act['text']

    def npc_build_context(self, partner_name=None):
        """
        Build the full context for this Soul's model
        """
        agent = self.target_node
        room = agent.get_room()
        txt = "_setting_name " + room.name + '\\n'
        txt += (
            "_setting_desc " + room.desc + '\\n'
        )
        if partner_name is not None:
            txt += "_partner_name " + partner_name + '\\n'
        txt += "_self_name " + agent.name + '\\n'
        txt += '_self_persona ' + agent.persona + '\\n'
        return txt

    def get_last_turn_too_recent(self):
        return time.time() - self._last_action_time < MIN_TIME_BETWEEN_TURNS

    def npc_action(self):
        """
        Agent attempt to take an action
        """
        if self.get_last_turn_too_recent() or (random.randint(0, 100) > 20):
            return

        agent = self.target_node
        partner_id = self.get_last_interaction_partner(agent)
        if partner_id != None:
            partner_name = self.world.oo_graph.get_prop(partner_id, 'names')[0]
        else:
            partner_name = None
       
        hist = self._dialogue_history
        if partner_id not in hist:
            hist[partner_id] = []
        if agent_id not in hist:
            hist[agent_id] = []

        txt = self.npc_build_context(partner_name)
        for d in hist[agent_id]:
            txt += d
        cands = self.world.get_possible_actions(agent_id)
        if len(cands) == 0:
            # nothing to do here.
            return

        msg = {
            'text': txt,
            'episode_done': True,
            'label_candidates': cands,
            'eval_labels': [cands[0]],
        }
        self.npc_act_model.observe(msg)
        act = self.npc_act_model.act()
        act_text = self.npc_pick_non_repeating_action(act)
        reply_action = act_text + '\n'
        # add action to history
        hist[agent_id].append('_self_act ' + act_text + '\\n')
        self.world.parse_exec(agent_id, reply_action)

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

        hist = self._dialog_history
        if agent_id not in hist:
            hist[agent_id] = []

        if not ALLOW_INTERBOT_CHAT and not partner._human:
            return

        partner_name = partner.name
        txt = self.npc_build_context(partner_name)
        for d in hist[agent_id]:
            txt += d

        if obs is not None and obs.text_content == 'DEBUG':
            # print debug information instead
            event = SayEvent(agent, target_nodes=[], text_content=txt)
            event.execute(self.world)
            return

        # add dialogue to history
        if obs is not None:
            last_msg = '_partner_say ' + obs.text_content + '\\n'
            hist[agent_id].append(last_msg)
            txt += last_msg
        
        # Send to model to process
        msg = {'text': txt, 'episode_done': True}
        self.npc_model.observe(msg)
        act = self.npc_model.act()
        act_text = self.dialogue_pick_non_repeating_response(act, partner)

        reply_event = TellEvent(agent, target_nodes=[partner], text_content=act_text)
        reply_event.execute(self.world)

        # add dialogue to history
        hist[agent_id].append('_self_say ' + act_text + '\\n')

    def get_last_interaction_partner(self, node: "GraphAgent"):
        """
        Get the last interaction partner labelled for the given node, if it exists
        """
        if hasattr(node, "_last_interaction_partner_id"):
            return node._last_interaction_partner_id
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
        for obs in self._pending_observations:
            if (
                isinstance(obs, SayEvent) or 
                (isinstance(obs, TellEvent) and obs.target_nodes[0] == agent)
            ):
                self.npc_dialogue(obs)
                return

        # possibly initiate talk request to someone in the room
        if self.get_last_interaction_partner(agent) is None:
            self._dialogue_history = {}
            room = agent.get_room()
            agents = [x for x in room.get_contents() if x.agent]
            partner = random.choice(agents)
            partner_id = partner.node_id
            if (
                partner.node_id != agent_id
                and partner.get_prop('speed', 0) > 0
                and self.get_last_interaction_partner(partner) is None
            ):
                self.set_interaction_partner(partner)
                # TODO handle dialogue with no observation
                self.npc_dialogue(None)
                return
        else:
            # possibly end interaction with existing interaction partner (if any)?
            if random.randint(0, 100) < 5:
                self.dialogue_clear_partner()

        room = agent.get_room()
        # TODO refactor attacking
        # possible_agents = [x for x in room.get_contents() if x.agent]
        # for other_agent in possible_agents:
        #     if other_agent.get_prop('is_player'):
        #         aggression = agent.get_prop('aggression', 0)
        #         if random.randint(0, 100) < aggression:
        #             act = 'hit {}'.format(other_agent.get_view())
        #             self.g.parse_exec(agent_id, act)
        #             return

        # random movement for npcs..
        if random.randint(0, 1000) < agent.speed:
            move_actions = self.world.get_possible_actions(agent_id, possible_actions=['go'])
            if len(move_actions) > 0:
                move_action = random.choice(move_actions)
                move_action.execute(self.world)
                return

        # possibly act according to the bert model
        self.npc_action(agent_id)