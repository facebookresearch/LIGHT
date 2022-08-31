#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from parlai.crowdsourcing.utils.worlds import CrowdOnboardWorld, CrowdTaskWorld
from parlai.core.worlds import validate
import random
from mephisto.abstractions.blueprint import AgentState
import time
from joblib import Parallel, delayed


SHORT_FORCED_TIMEOUT_TIME = 0.0001


class LIGHTMultiAgentDialogOnboardWorld(CrowdOnboardWorld):
    def __init__(self, opt, agent):
        super().__init__(opt, agent)
        self.opt = opt

    def parley(self):
        self.agent.agent_id = "Onboarding Agent"
        self.agent.observe(
            {
                "id": "System",
                "text": "Welcome onboard! In this task you will be given a fantasy "
                "character to play, and will have a conversation with two "
                "other workers who are also playing characters. Try to "
                "remain in character while talking about your character's "
                "motivations, or the given setting, or anything that seems "
                "appropriate. Send anything to continue.",
            }
        )
        x = self.agent.act(timeout=self.opt["turn_timeout"])
        self.agent.observe(
            {
                "id": "System",
                "text": "You will be able to take turns freely, and the conversation "
                "will end after everyone has taken the minimum number of turns. "
                "Please try to pace the conversation appropriately, rather than "
                "just sending multiple messages in rapid succession. Those found "
                "not having natural conversations will be blocked from working "
                "on future tasks. Send anything to continue. ",
            }
        )
        x = self.agent.act(timeout=self.opt["turn_timeout"])
        self.agent.observe(
            {
                "id": "System",
                "text": "Thanks for reading. Please wait while "
                "we match you with other workers...",
                "episode_done": True,
            }
        )
        self.episodeDone = True


class LIGHTMultiAgentDialogWorld(CrowdTaskWorld):
    """
    Basic world where each agent gets a turn in a round-robin fashion, receiving as
    input the actions of all other agents since that agent last acted.
    """

    def __init__(self, opt, agents=None, shared=None):
        # Add passed in agents directly.
        self.agents = agents
        self.graph, self.world = opt["builder"].get_constrained_graph(num_partners=2)
        self.graph_json = self.graph.to_json()
        self.last_act_times = [time.time()] * len(agents)
        self.act_counts = [0] * len(agents)
        self.episodeDone = False
        self.max_turns = opt.get("num_turns", 2)
        self.opt = opt
        self.assign_identities()

    def assign_identities(self):
        """Find three of the characters, and send them to the agents"""
        available_players = list(self.graph.agents.values())

        self.identities = [
            {
                "id": player.node_id,
                "name": player.name,
                "persona": player.persona,
                "db_id": player.db_id,
            }
            for player in available_players
        ]

        location = available_players[0].get_room()
        self.location_details = {
            "id": location.node_id,
            "name": location.name,
            "description": location.desc,
            "db_id": location.db_id,
        }

        for idx, agent in enumerate(self.agents):
            agent.agent_id = self.identities[idx]["name"]
            p0, p1 = [[1, 2], [2, 0], [0, 1]][idx]
            partners = (
                f"{self.identities[p0]['name']} and {self.identities[p1]['name']}"
            )
            agent.observe(
                {
                    "id": "Coordinator",
                    "text": "Welcome! You've been assigned the character "
                    f"'{self.identities[idx]['name']}' and are in the "
                    f"location '{self.location_details['name']}'. "
                    "(If your character is plural, pretend to be one). "
                    f"Your chat partners are {partners}. More details "
                    "on your persona and location are available to the left.",
                    "task_data": {
                        "persona": self.identities[idx],
                        "location": self.location_details,
                    },
                }
            )

    def try_agent_timeouts(self):
        """
        Check each agent to see that they've responded within the timeout
        updating to timeout status if they have exceeded the timeout
        """
        for index, agent in enumerate(self.agents):
            if time.time() - self.last_act_times[index] > self.opt["turn_timeout"]:
                # Forced timeout loop even catches if someone sends a message right after the timeout
                # without breaking
                while agent.act(timeout=SHORT_FORCED_TIMEOUT_TIME) is not None:
                    pass

    def is_done(self):
        """Check to see if all agents have taken the minimum turns"""
        for index, _ in enumerate(self.agents):
            if self.act_counts[index] < self.max_turns:
                return False
        return True

    def parley(self):
        """
        For each agent, get any acts available, nonblocking.

        Propogate to other agents
        """
        for index, agent in enumerate(self.agents):
            act = agent.act(timeout=None)
            if act != None:
                self.last_act_times[index] = time.time()
                self.act_counts[index] += 1
                for other_agent in self.agents:
                    if other_agent != agent:
                        other_agent.observe(validate(act))

        time.sleep(0.1)  # Preventing tight loop on parley calls

        self.try_agent_timeouts()
        if self.is_done():
            self.episodeDone = True
            for agent in self.agents:
                agent.observe(
                    {
                        "id": "Coordinator",
                        "text": "Thanks for the conversation! You can submit",
                    }
                )

    def prep_save_data(self, agent):
        """Process and return any additional data from this world you may want to store"""
        return {
            "graph": self.graph_json,
            "characters": self.identities,
            "location": self.location_details,
        }

    def episode_done(self):
        return self.episodeDone

    def shutdown(self):
        """
        Shutdown all mturk agents in parallel, otherwise if one mturk agent is
        disconnected then it could prevent other mturk agents from completing.
        """

        def shutdown_agent(agent):
            try:
                agent.shutdown(timeout=None)
            except Exception:
                agent.shutdown()  # not MTurkAgent

        Parallel(n_jobs=len(self.agents), backend="threading")(
            delayed(shutdown_agent)(agent) for agent in self.agents
        )


def make_onboarding_world(opt, agent):
    return LIGHTMultiAgentDialogOnboardWorld(opt, agent)


def validate_onboarding(data):
    """Onboarding data for this task doesn't change approval"""
    print(f"Validating onboarding data {data}")
    return True


def make_world(opt, agents):
    return LIGHTMultiAgentDialogWorld(opt, agents)


def get_world_params():
    return {"agent_count": 3}
