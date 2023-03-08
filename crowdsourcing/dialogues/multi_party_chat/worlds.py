#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import time
from joblib import Parallel, delayed
from datetime import datetime

from parlai.crowdsourcing.utils.worlds import CrowdOnboardWorld, CrowdTaskWorld
from parlai.core.worlds import validate
import parlai.utils.logging as logging
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.exceptions import (
    AgentReturnedError,
    AgentDisconnectedError,
    AgentTimeoutError,
    AgentShutdownError,
)
from mephisto.abstractions._subcomponents.agent_state import AgentState

import constants
from acceptability import MultiPartyChatChecker


SHORT_FORCED_TIMEOUT_TIME = 0.0001
mephisto_db = LocalMephistoDB()


def get_worker_from_agent(agent):
    return agent.mephisto_agent.get_worker()


def gen_world_name(prfx):
    dt = datetime.now()
    return prfx + dt.strftime("%H-%M-%S")


class MultiAgentDialogOnboardWorld(CrowdOnboardWorld):
    def __init__(self, opt, agent):
        super().__init__(opt, agent)
        self.agent.agent_id = "Guard"  # Assign fixed persona for onboarding
        self.opt = opt
        self._world_name = gen_world_name("onboarding_world_")
        self.messages = []
        checker = MultiPartyChatChecker()
        checker.min_words_violation_threshold = constants.MIN_AVG_WORD_LENGTH_UTTERANCES
        self.checker = checker
        self.last_act_time = time.time()
        self.has_warned = False  # Warning this turn for inactivity

    def get_worker(self):
        return get_worker_from_agent(self.agent)

    def get_worker_name(self):
        return self.get_worker().worker_name

    def try_timeout(self):
        if (
            0 <= self.opt["turn_timeout"] - (time.time() - self.last_act_time) <= 60
            and not self.has_warned
        ):
            self.agent.observe(
                {
                    "id": "Coordinator",
                    "text": "Please respond within 60 seconds or you will get kicked out",
                }
            )
            self.has_warned = True

        # check if any of the remaining connected agents have timed out
        if time.time() - self.last_act_time > self.opt["turn_timeout"]:
            # Forced timeout loop even catches if someone sends a message
            # right after the timeout without breaking
            while self.agent.act(timeout=SHORT_FORCED_TIMEOUT_TIME) is not None:
                pass

    def wait_for_response(self):
        logging.info(
            f"[OnboardingWorld] Waiting for response from {self.get_worker_name()}."
        )
        while True:
            try:
                act = self.agent.act(timeout=None)
            except Exception:
                act = self.agent.act()  # not MTurk
            self.try_timeout()
            if act is not None:
                self.last_act_time = time.time()
                self.has_warned = False
                return act
            time.sleep(0.1)  # Preventing tight loop

    def parley(self):
        m = {
            "id": "Coordinator",
            "text": constants.ONBOARDING_WELCOME_MESSAGE,
            "task_data": {
                "persona": {
                    "name": "Guard",
                    "persona": constants.ONBOARDING_PERSONA_DESCRIPTION,
                },
                "location": {
                    "name": "Throne room",
                    "description": constants.ONBOARDING_LOCATION_DESCRIPTION,
                },
            },
            "timestamp": time.time(),
        }

        self.agent.observe(m)
        self.messages.append(m)
        time.sleep(4)

        m = {
            "id": "Coordinator",
            "text": constants.ONBOARDING_CHAT_PARTNERS,
            "task_data": {
                "partners": [
                    {
                        "name": "King",
                    },
                    {
                        "name": "Sword-Maker",
                    },
                ]
            },
        }

        self.agent.observe(m)
        self.messages.append(m)
        time.sleep(4)

        m = {
            "id": "Sword-Maker",
            "text": constants.ONBOARDING_MESSAGES[0],
        }
        self.agent.observe(m)
        self.messages.append(m)
        time.sleep(4)

        m = {
            "id": "King",
            "text": constants.ONBOARDING_MESSAGES[1],
        }
        self.agent.observe(m)
        self.messages.append(m)

        m = {
            "id": "Coordinator",
            "text": constants.ONBOARDING_MESSAGES[2],
        }
        self.agent.observe(m)
        self.messages.append(m)

        msg1 = self.wait_for_response()
        self.messages.append(msg1)
        time.sleep(4)

        m = {
            "id": "King",
            "text": constants.ONBOARDING_MESSAGES[3],
        }
        self.agent.observe(m)

        m = {"id": "Coordinator", "text": constants.ONBOARDING_MESSAGES[4]}
        self.agent.observe(m)

        msg2 = self.wait_for_response()
        self.messages.append(msg2)
        time.sleep(4)

        m = {
            "id": "Sword-Maker",
            "text": constants.ONBOARDING_MESSAGES[5],
        }
        self.agent.observe(m)
        self.messages.append(m)

        m = {"id": "Coordinator", "text": constants.ONBOARDING_MESSAGES[6]}
        self.agent.observe(m)
        self.messages.append(m)

        msg3 = self.wait_for_response()
        self.messages.append(msg3)
        time.sleep(4)

        self.agent.observe(
            {
                "id": "Coordinator",
                "text": constants.ONBOARDING_MESSAGES[7],
                "episode_done": True,
            }
        )
        self.episodeDone = True

    def reason_to_reject(self, agent):
        if not self.episodeDone:
            return "left/diconnected before the task was over."

        acceptability_checker_results = self.checker.check_messages(
            agent.agent_id,
            messages=self.messages,
            location_description=constants.ONBOARDING_LOCATION_DESCRIPTION,
            persona_description=constants.ONBOARDING_PERSONA_DESCRIPTION,
            violation_types=constants.ACCEPTABILITY_VIOLATIONS,
            is_onboarding=True,
        )
        if acceptability_checker_results:
            return f'ParlAI acceptability checker found violations: "{acceptability_checker_results}"'

        return None

    def prep_save_data(self, agent_as_list):
        rejection_reason = self.reason_to_reject(agent_as_list[0])
        return {
            constants.SAVED_DATA_WORKER_KEY: self.get_worker_name(),
            constants.WORKER_REJECT_REASON: rejection_reason,
        }

    def shutdown(self):
        logging.info(f"Shutting down {self._world_name}")
        super().shutdown()
        logging.info("Shutdown completed successfully.")


class MultiAgentDialogWorld(CrowdTaskWorld):
    """
    Async multiparty chat where agents don't need to take turns.

    Task can be completed when minimum number of turns are reached. Task can continue
    after the minimum number of turns, and after partners leave. Coordinator issues
    timeout warning and notifications for partners leaving.
    """

    def __init__(self, opt, agents=None, shared=None):
        # Add passed in agents directly.
        self.agents = agents
        self.agent_ids = [0] * len(agents)
        self._world_name = gen_world_name("main_world_")
        self.is_connected = [True] * len(agents)  # agent diconnected or submitted
        self.has_warned = [False] * len(agents)  # timeout warning this turn
        self.graph, self.world = opt["builder"].get_constrained_graph(num_partners=2)
        # `get_constrained_graph` sometimes fails
        while not self.graph:
            self.graph, self.world = opt["builder"].get_constrained_graph(
                num_partners=2
            )
        self.graph_json = self.graph.to_json()
        self.messages = []
        # how many messages each agent has sent in this turn
        self.act_counts = [0] * len(agents)
        # how many turns has each agent acted
        self.turn_counts = [0] * len(agents)
        self.last_act_times = [time.time()] * len(agents)
        self.last_spoken_agent = None
        self.episodeDone = False
        # whether we've made the announcement the task is done
        self.has_announced = False
        # number of turns each agent must speak before the task is done
        # multiple acts from same agent before others act only count as 1 turn
        self.num_turns = opt.get("num_turns", 2)
        # the max number of messages an agent can send before others act
        self.max_acts_per_turn = opt.get("max_acts_per_turn", 5)
        self.opt = opt
        self.assign_identities()

        checker = MultiPartyChatChecker()
        checker.min_words_violation_threshold = constants.MIN_AVG_WORD_LENGTH_UTTERANCES
        self.checker = checker

        # self.soft_block_qname = opt["soft_block_qname"]

    def assign_identities(self):
        """
        Find three of the characters, and send them to the agents.
        """
        available_players = list(self.graph.agents.values())

        char_names_str = " , ".join([p.name for p in available_players])
        logging.info(f"Assigning characters ({self._world_name}): {char_names_str}")

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
        self.location_description = location.desc

        for idx, agent in enumerate(self.agents):
            agent.agent_id = self.identities[idx]["name"]
            self.agent_ids[idx] = agent.agent_id
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
                    "(If your character is plural, pretend to be one). ",
                    "task_data": {
                        "persona": self.identities[idx],
                        "location": self.location_details,
                    },
                }
            )

        time.sleep(4)

        for idx, agent in enumerate(self.agents):
            agent.observe(
                {
                    "task_data": {"current_dialogue_turn": self.turn_counts[idx]},
                }
            )
            p0, p1 = [[1, 2], [2, 0], [0, 1]][idx]
            partner_names = (
                f"{self.identities[p0]['name']} and {self.identities[p1]['name']}"
            )
            partners = [self.identities[p0], self.identities[p1]]
            agent.observe(
                {
                    "id": "Coordinator",
                    "text": f"Your chat partners are {partner_names}. More details "
                    "on your persona and location are available to the left.",
                    "task_data": {
                        "partners": partners,
                    },
                }
            )

    def try_agent_timeouts(self):
        """
        Check each agent to see that they've responded within the timeout updating to
        timeout status if they have exceeded the timeout.

        Additionally capture timeout exceptions so that conversation can continue
        for the remaining connected agents instead of shutting down by default.
        (see default behavior in `mephisto/abstractions/_subcomponents/task_runner.py: _launch_and_run_assignment`)
        """
        for i, agent in enumerate(self.agents):
            # send warning message if almost timing out
            if (
                self.is_connected[i]
                and 0
                <= self.opt["turn_timeout"] - (time.time() - self.last_act_times[i])
                <= 60
                and not self.has_warned[i]
            ):
                agent.observe(
                    {
                        "id": "Coordinator",
                        "text": "Please respond within 60 seconds or you will get kicked out",
                    }
                )
                self.has_warned[i] = True

            # check if any of the remaining connected agents have timed out
            if (
                self.is_connected[i]
                and time.time() - self.last_act_times[i] > self.opt["turn_timeout"]
            ):
                self.is_connected[i] = False
                # Forced timeout loop even catches if someone sends a message
                # right after the timeout without breaking
                try:
                    while agent.act(timeout=SHORT_FORCED_TIMEOUT_TIME) is not None:
                        pass
                except (
                    AgentReturnedError,
                    AgentTimeoutError,
                    AgentDisconnectedError,
                    AgentShutdownError,
                ) as e:
                    logging.warning(e)
                    self.messages.append(
                        {
                            "id": "Coordinator",
                            "text": f"{agent.agent_id} left the chat.",
                        }
                    )
                    for _, other_agent in enumerate(self.agents):
                        if other_agent != agent:
                            other_agent.observe(
                                {
                                    "id": "Coordinator",
                                    "text": f"{agent.agent_id} left the chat. No worries, you'll still get paid!",
                                }
                            )
                            # agent.update_status(AgentState.STATUS_PARTNER_DISCONNECT)
                    # Must expire the disconnected unit so that
                    # new workers aren't shown it
                    agent.mephisto_agent.get_unit().expire()

    def check_agent_status(self):
        for i, agent in enumerate(self.agents):
            if self.is_connected[i] and (
                agent.mephisto_agent.get_status() in AgentState.complete()
                or agent.mephisto_agent.did_submit.is_set()
            ):
                # Save data on submit
                # agent.mephisto_agent.handle_submit(self.prep_save_data([agent]))
                agent.mephisto_agent.state.update_data(
                    {
                        "id": "SUBMIT_WORLD_DATA",
                        "WORLD_DATA": self.prep_save_data([agent]),
                        "text": "",
                    }
                )
                agent.mephisto_agent.state.save_data()

                # Update status to completed
                self.is_connected[i] = False
                agent.mephisto_agent.update_status(AgentState.STATUS_COMPLETED)
                agent.observe({"task_data": {"has_submitted": True}})

                # Notify remaining agents
                self.messages.append(
                    {
                        "id": "Coordinator",
                        "text": f"{agent.agent_id} left the chat.",
                    }
                )
                for other_agent in self.agents:
                    if other_agent != agent:
                        other_agent.observe(
                            {
                                "id": "Coordinator",
                                "text": f"{agent.agent_id} left the chat. No worries, you'll still get paid!",
                            }
                        )

    def all_done(self):
        """
        The task can be shut down when everyone has either submitted or disconnected.
        """
        for is_connected in self.is_connected:
            if is_connected:
                return False
        return True

    def is_done(self):
        """
        The task is done if there's only 1 agent left, or if all remaining agents have
        taken the minimum turns.
        """
        # Check if there's only 1 agent left
        remaining_agents = 0
        for is_connected in self.is_connected:
            if is_connected:
                remaining_agents += 1
        if remaining_agents == 1:
            return True

        # Check whether remaining connected agents have all taken minimum turns
        for index, _ in enumerate(self.agents):
            if self.is_connected[index] and self.turn_counts[index] < self.num_turns:
                return False
        return True

    def parley(self):
        """
        For each agent, get any acts available, nonblocking.

        Propogate to other agents
        """
        for index, agent in enumerate(self.agents):
            # skip agent if they  sent too many messages before others reply, or if they have disconnected/ submitted
            if (
                self.act_counts[index] >= self.max_acts_per_turn
                or not self.is_connected[index]
            ):
                continue
            try:
                act = agent.act(timeout=None)
            except Exception:
                act = agent.act()  # not MTurk

            if act is not None:
                self.messages.append(act)
                worker = get_worker_from_agent(agent)
                logging.info(
                    f'({self._world_name} | {worker.worker_name}) {act["id"]}: {act["text"]}'
                )

                self.last_act_times[index] = time.time()
                self.has_warned[index] = False
                if self.last_spoken_agent == agent:  # same turn
                    self.act_counts[index] += 1
                else:  # new turn
                    self.last_spoken_agent = agent
                    self.turn_counts[index] += 1
                    self.act_counts[index] = 1  # 1 act in this new turn
                    agent.observe(
                        {
                            "task_data": {
                                "current_dialogue_turn": self.turn_counts[index]
                            },
                        }
                    )
                    # reset act counts for other agents in new turn
                    for other_index, other_agent in enumerate(self.agents):
                        if other_agent != agent:
                            self.act_counts[other_index] = 0

                for _, other_agent in enumerate(self.agents):
                    if other_agent != agent:
                        other_agent.observe(validate(act))

        time.sleep(0.1)  # Preventing tight loop on parley calls
        self.try_agent_timeouts()
        self.check_agent_status()

        if self.is_done():
            if not self.has_announced:
                self.has_announced = True
                for idx, agent in enumerate(self.agents):
                    if not self.is_connected[idx]:
                        continue

                    p0, p1 = [[1, 2], [2, 0], [0, 1]][idx]
                    partner1 = self.identities[p0]["name"]
                    partner2 = self.identities[p1]["name"]

                    agent.observe(
                        {
                            "id": "Coordinator",
                            "text": "Thanks for completing the task! You can keep going or submit and leave anytime",
                        }
                    )

                    agent.observe(
                        {
                            "task_data": {
                                "respond_with_form": [
                                    {
                                        "type": "choices",
                                        "question": "How much did you enjoy this conversation?",
                                        "choices": [
                                            "Not at all",
                                            "A little",
                                            "Somewhat",
                                            "A lot",
                                        ],
                                    },
                                    {
                                        "type": "choices",
                                        "question": f"Do you want to report {partner1} for bad behavior?",
                                        "choices": [
                                            "No",
                                            "Yes",
                                        ],
                                    },
                                    {
                                        "type": "choices",
                                        "question": f"Do you want to report {partner2} for bad behavior?",
                                        "choices": [
                                            "No",
                                            "Yes",
                                        ],
                                    },
                                    {
                                        "type": "text",
                                        "question": "Enter any comment here",
                                    },
                                ]
                            },
                        }
                    )

                    # Ensure agents can submit after completion
                    agent.observe({"task_data": {"task_done": True}})

        # Task can shut down when everyone has disconnected
        # (either due to inactivity or because they have submitted)
        if self.all_done():
            self.episodeDone = True

    def prep_save_data(self, agent_as_list):
        """
        Return any additional data from this world you may want to store.
        """
        agent = agent_as_list[0]
        agent_id = agent.agent_id
        logging.info(f"Preparing saved data for {agent_id}")

        data = {
            "agent_id": agent_id,
            "graph": self.graph_json,
            "characters": self.identities,
            "location": self.location_details,
            "message_history_copy": self.messages,
        }

        disqualify_reason = self.reason_to_reject(agent)
        if disqualify_reason:
            logging.info(f'Disqualified submission detecetd: "{disqualify_reason}"')
            data["disqualify_reason"] = disqualify_reason
            self._soft_block_agent(agent)

        return data

    def get_persona_description(self, agent):
        for identity in self.identities:
            name = identity["name"]
            if name == agent.agent_id:
                return identity["persona"]

    def reason_to_reject(self, agent):
        # Disconncet or timeout
        mephisto_agent = agent.mephisto_agent
        if mephisto_agent.get_status() in (
            AgentState.STATUS_EXPIRED,
            AgentState.STATUS_TIMEOUT,
        ):
            return "agent was disconnected."

        persona_description = self.get_persona_description(agent)

        acceptability_checker_results = self.checker.check_messages(
            agent.agent_id,
            messages=self.messages,
            location_description=self.location_description,
            persona_description=persona_description,
            violation_types=constants.ACCEPTABILITY_VIOLATIONS,
        )
        if acceptability_checker_results:
            return f'ParlAI acceptability checker found violations: "{acceptability_checker_results}"'

        return None

    def _soft_block_agent(self, agent):
        worker = get_worker_from_agent(agent)
        logging.warning(f"Soft blocking {worker.worker_name}")
        worker.grant_qualification(self.soft_block_qname)
        pass

    def episode_done(self):
        return self.episodeDone

    def shutdown(self):
        """
        Shutdown all mturk agents in parallel, otherwise if one mturk agent is
        disconnected then it could prevent other mturk agents from completing.
        """
        global shutdown_agent

        def shutdown_agent(agent):
            try:
                agent.shutdown(timeout=None)
            except Exception:
                agent.shutdown()  # not MTurkAgent

        Parallel(n_jobs=len(self.agents), backend="threading")(
            delayed(shutdown_agent)(agent) for agent in self.agents
        )


def make_onboarding_world(opt, agent):
    return MultiAgentDialogOnboardWorld(opt, agent)


def validate_onboarding(data):
    """
    Check the contents of the data to ensure they are valid.
    """
    logging.info(f"Validating onboarding data {data}")
    try:
        saved_data = data["outputs"]["messages"][-1]["WORLD_DATA"]
    except (IndexError, KeyError) as e:
        logging.warning(
            "Incomplete data to validate agent onboarding."
            f"Onboarding saved_data error: {e}"
        )
        return False

    rejection_reason = saved_data[constants.WORKER_REJECT_REASON]
    if rejection_reason:
        logging.warning(f"Rejected: {rejection_reason}")
        return False

    logging.info("Onboarding work accepted.")
    return True


def make_world(opt, agents):
    return MultiAgentDialogWorld(opt, agents)


def get_world_params():
    return {"agent_count": 3}
