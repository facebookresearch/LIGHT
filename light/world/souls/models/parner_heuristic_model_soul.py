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