#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.world.souls.model_soul import ModelSoul

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.graph.world.world import World
    from light.graph.events.base import GraphEvent


class PartnerHeuristicModelSoul(ModelSoul):
    """
    A ModelSoul is responsible for passing it's observations back to
    a model that decides what to do. This class will likely have utility
    methods for loading shared models and some shared behavior between
    classes, for now is a stub.
    """

    HAS_MAIN_LOOP = True

    def _init_with_models(self, models) -> None:
        """
        Initialize required members of this soul for tracking the 
        model and interactions with it.
        """
        self._pending_observations = []
        self._node_to_dialog_history = {}
        self._no_npc_models = False
        self._last_action_time = {}
        self._timer = Timer()
        self._last_interaction_partner = {}
        self._last_dialogs = {}
        self._last_actions = {}

    async def observe_event(self, event: "GraphEvent"):
        """
        On an observe event, the agent 
        """
        if event.actor == self.target_node:
            return
        
        self._pending_observations.append(event)

        # The model may choose to do something in response to this action, 
        # so don't wait for the timeout.
        await self._take_timestep()

    # check if utterance <txt> was said by <agent> recently, or not (so we don't repeat).
    def dialogue_utterance_not_too_recent(self, txt, agent):
        # heuristic: only say something that hasn't been mentioned in the last 50 turns.
        if agent not in self._last_dialogs:
            self._last_dialogs[agent] = [[], set()]
        hist = self._last_dialogs[agent]
        if len(hist[0]) > 50:
            # pop oldest utterance from the list
            hist[1].remove(hist[0][0])
            hist[0].pop(0)
        if txt not in hist[1]:
            hist[1].add(txt)
            hist[0].append(txt)
            return True
        return False

    # check if utterance <txt> was said by <agent> recently, or not (so we don't repeat).
    def action_not_too_recent(self, txt, agent):
        # heuristic: only say something that hasn't been mentioned in the last 50 turns.
        if agent not in self._last_actions:
            self._last_actions[agent] = [[], set()]
        hist = self._last_actions[agent]
        if len(hist[0]) > 4:
            # pop oldest utterance from the list
            hist[1].remove(hist[0][0])
            hist[0].pop(0)
        if txt not in hist[1]:
            hist[1].add(txt)
            hist[0].append(txt)
            return True
        return False

    def dialogue_clear_partner(self, agent_id):
        # how a dialogue agent deals with moving location
        # TODO: bake this into the callback later.
        # reset dialogue history when move:
        self._node_to_dialog_history[agent_id] = {}
        # remove interaction partner links:
        partner_id = self._last_interaction_partner.get(agent_id, 'none')
        self._last_interaction_partner[agent_id] = 'none'
        if (
            partner_id != 'none'
            and self._last_interaction_partner.get(partner_id, 'none') == agent_id
        ):
            self._last_interaction_partner[partner_id] = 'none'
            self._node_to_dialog_history[partner_id] = {}

    # check if utterance <txt> was said by <agent> recently, or not (so we don't repeat).
    def dialogue_utterance_not_too_recent(self, txt, agent):
        # heuristic: only say something that hasn't been mentioned in the last 50 turns.
        if agent not in self._last_dialogs:
            self._last_dialogs[agent] = [[], set()]
        hist = self._last_dialogs[agent]
        if len(hist[0]) > 50:
            # pop oldest utterance from the list
            hist[1].remove(hist[0][0])
            hist[0].pop(0)
        if txt not in hist[1]:
            hist[1].add(txt)
            hist[0].append(txt)
            return True
        return False

    # check if utterance <txt> was said by <agent> recently, or not (so we don't repeat).
    def action_not_too_recent(self, txt, agent):
        # heuristic: only say something that hasn't been mentioned in the last 50 turns.
        if agent not in self._last_actions:
            self._last_actions[agent] = [[], set()]
        hist = self._last_actions[agent]
        if len(hist[0]) > 4:
            # pop oldest utterance from the list
            hist[1].remove(hist[0][0])
            hist[0].pop(0)
        if txt not in hist[1]:
            hist[1].add(txt)
            hist[0].append(txt)
            return True
        return False

    def npc_pick_non_repeating_action(self, act, agent1):
        # for t in act['text_candidates']:
        t = act['text_candidates'][0]
        if self.action_not_too_recent(t, agent1) or t.startswith('hit'):
            return t
        # couldn't find a valid response, so just return the top one.
        return 'wait'

    def dialogue_pick_non_repeating_response(self, act, agent1, agent2):
        agent1_name = agent1[: agent1.find('_')]
        agent2_name = agent2[: agent2.find('_')]
        for t in act['text_candidates']:
            if (
                self.dialogue_utterance_not_too_recent(t, agent1)
                and self.dialogue_utterance_not_too_recent(t, agent2)
                and self._utt_to_name.get(t, 'anon') != agent2_name
            ):
                return t
            # + " [" + self._utt_to_name.get(t, 'anon') + "-vs-" + agent2_name + "|" + agent1_name  + "]"
        # couldn't find a valid response, so just return the top one.
        return act['text']

    def npc_build_context(self, agent_id, partner_name=None):
        # Build context for model.
        room_id = self.g.node_contained_in(agent_id)
        txt = "_setting_name " + self.g.get_prop(room_id, 'names')[0] + '\\n'
        txt += (
            "_setting_desc " + self.g.get_prop(room_id, 'desc').replace('*', '') + '\\n'
        )
        if partner_name is not None:
            txt += "_partner_name " + partner_name + '\\n'
        txt += "_self_name " + self.g.get_prop(agent_id, 'names')[0] + '\\n'
        txt += '_self_persona ' + self.g.get_prop(agent_id, 'persona') + '\\n'
        return txt

    # log that an agent acted
    def log_agent_acted(self, agent_id):
        self._last_action_time[agent_id] = self._timer.time() + random.random() * 0.1
        # log in the location they are in, too
        room_id = self.g.room(agent_id)
        self._last_action_time[room_id] = self._timer.time() + random.random() * 0.1

    # last time agent acted, according to its own log
    def last_agent_action(self, agent_id):
        curr_time = self._timer.time()
        if agent_id not in self._last_action_time:
            self._last_action_time[agent_id] = curr_time - 10
        room_id = self.g.room(agent_id)
        if room_id not in self._last_action_time:
            self._last_action_time[room_id] = curr_time - 10
        tim1 = curr_time - self._last_action_time[agent_id]
        tim2 = curr_time - self._last_action_time[room_id]
        return min(tim1, tim2)

    def last_agent_action_too_recent(self, agent_id):
        return self.last_agent_action(agent_id) < 5

    def npc_action(self, agent_id):
        if (
            True
        ):  # self._no_npc_models: #Skipped entirely for now amidst npc refactoring
            return
        if (random.randint(0, 100) < 20) and not self.last_agent_action_too_recent(
            agent_id
        ):
            pass
        else:
            return

        partner_id = self._last_interaction_partner.get(agent_id, 'none')
        if partner_id != 'none':
            partner_name = self.g.get_prop(partner_id, 'names')[0]
        else:
            partner_name = None
        if not hasattr(self, 'npc_act_model'):
            # load the bert model up:
            self.load_npc_act_model()
        if agent_id not in self._node_to_dialog_history:
            self._node_to_dialog_history[agent_id] = {}
        hist = self._node_to_dialog_history[agent_id]
        if partner_id not in hist:
            hist[partner_id] = []
        if agent_id not in hist:
            hist[agent_id] = []
        txt = self.npc_build_context(agent_id, partner_name)
        for d in hist[agent_id]:
            txt += d
        cands = self.g.get_possible_actions(agent_id)
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
        act_text = self.npc_pick_non_repeating_action(act, agent_id)
        reply_action = act_text + '\n'
        # add action to history
        hist[agent_id].append('_self_act ' + act_text + '\\n')
        self.g.parse_exec(agent_id, reply_action)
        self.log_agent_acted(agent_id)

    def npc_dialogue(self, agent_id, obs):
        if True:  # self._no_npc_models: #Skipped during NPC refactoring
            return
        partner_id = obs['actors'][0]
        partner_name = self.g.get_prop(partner_id, 'names')[0]
        partner_interactor_id = self._last_interaction_partner.get(partner_id, 'none')
        if (
            obs['caller'] == 'say'
            and partner_interactor_id != 'none'
            and partner_interactor_id != agent_id
        ):
            # partner said something, but is interacting with someone else, so we don't reply.
            return
        # we are going to reply, so point both agents as having this as their last interaction.
        last_partner_id = self._last_interaction_partner.get(agent_id, 'none')
        if last_partner_id != 'none':
            self._last_interaction_partner[last_partner_id] = 'none'
        if partner_interactor_id != 'none':
            self._last_interaction_partner[partner_interactor_id] = 'none'
        self._last_interaction_partner[agent_id] = partner_id
        self._last_interaction_partner[partner_id] = agent_id

        if not hasattr(self, 'npc_model'):
            # load the bert model up:
            self.load_npc_model()
        if agent_id not in self._node_to_dialog_history:
            self._node_to_dialog_history[agent_id] = {}
        hist = self._node_to_dialog_history[agent_id]
        if agent_id not in hist:
            hist[agent_id] = []

        # uncomment if you don't want npcs to talk to each other
        if not self.g.get_prop(partner_id, 'human'):
            return

        txt = self.npc_build_context(agent_id, partner_name)
        for d in hist[agent_id]:
            txt += d

        if obs.get('content', 'none') == 'analysis':
            # print debug information instead
            reply_action = "say " + txt + '\n'
            self.g.parse_exec(agent_id, reply_action)
            return

        # add dialogue to history
        if 'content' in obs:
            last_msg = '_partner_say ' + obs['content'] + '\\n'
            hist[agent_id].append(last_msg)
            txt += last_msg
        msg = {'text': txt, 'episode_done': True}
        self.npc_model.observe(msg)
        act = self.npc_model.act()
        act_text = self.dialogue_pick_non_repeating_response(act, agent_id, partner_id)
        # p self._node_to_prop[agent_id]
        # p self.g.get_prop(agent_id, 'persona')[0]
        reply_action = "tell " + partner_name + ' "' + act_text + '"\n'
        # add dialogue to history
        hist[agent_id].append('_self_say ' + act_text + '\\n')
        self.g.parse_exec(agent_id, reply_action)
        # TODO: possibly move this to parse_exec?
        self.log_agent_acted(agent_id)
        self.log_agent_acted(partner_id)

    async def _take_timestep(self) -> None:
        """
        If this model intends to take actions periodically, those steps should
        be defined in this method. The method _run_timesteps will call this periodically.
        """
        if self.last_agent_action_too_recent(agent_id):
            return

        # possibly respond to talk requests
        graph = self.world.oo_graph
        agent = graph.get_node(agent_id)
        for obs in agent._observations:
            # TODO handle updating dialogue for actions
            # if (
            #     obs['caller'] == 'say'
            #     or (obs['caller'] == 'tell' and obs['target_agent'] == agent_id)
            # ) and not self.last_agent_action_too_recent(agent_id):
            #     self.npc_dialogue(agent_id, obs)
            #     agent.get_text()
            #     return
            pass
        # possibly initiate talk request to someone in the room
        if self._last_interaction_partner.get(agent_id, 'none') == 'none':
            room = agent.get_room()
            agents = [x for x in room.get_contents() if x.agent]
            partner = random.choice(agents)
            partner_id = partner.node_id
            if (
                partner.node_id != agent_id
                and partner.get_prop('speed', 0) > 0
                and self._last_interaction_partner.get(partner_id, 'none') == 'none'
            ):
                obs = {'caller': 'say', 'actors': [partner_id]}
                self.npc_dialogue(agent_id, obs)
                agent.get_text()
                return
        else:
            # possibly end interaction with existing interaction partner (if any)?
            if random.randint(0, 100) < 5:
                self.dialogue_clear_partner(agent_id)

        agent.get_text(agent_id)
        did_hit = False
        room = agent.get_room()
        possible_agents = [x for x in room.get_contents() if x.agent]
        # TODO refactor
        for other_agent in possible_agents:
            if other_agent.get_prop('is_player'):
                aggression = agent.get_prop('aggression', 0)
                if random.randint(0, 100) < aggression:
                    act = 'hit {}'.format(other_agent.get_view())
                    self.g.parse_exec(agent_id, act)
                    self.log_agent_acted(agent_id)
                    did_hit = True

        if not did_hit:
            # random movement for npcs..
            if random.randint(0, 1000) < self.g.get_prop(agent_id, 'speed', 0):
                cur_loc = self.g.room(agent_id)
                locs = self.g.node_path_to(cur_loc)
                if len(locs) > 0:
                    loc = locs[random.randint(0, len(locs) - 1)]
                    act = 'go ' + self.g.node_to_desc_raw(loc, from_id=cur_loc)
                    self.g.parse_exec(agent_id, act)
                    self.log_agent_acted(agent_id)

        # possibly act according to the bert model
        self.npc_action(agent_id)