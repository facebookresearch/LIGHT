# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import torch
from copy import copy
from copy import deepcopy
import os

from parlai.core.agents import create_agent, create_agent_from_shared
from light.modeling.agents.quests.rl.switch.environments.environment import Environment
from light.modeling.agents.quests.rl.switch.environments.env_generator import (
    EnvironmentGenerator,
)
from light.modeling.agents.quests.rl.shared.process.constants import *

from parlai.core.metrics import F1Metric
from parlai.core.message import Message
from parlai.core.params import ParlaiParser
from parlai.utils.misc import msg_to_str

ParlaiParser()  # instantiate to set PARLAI_HOME environment var

PARLAI_PATH = os.environ["PARLAI_HOME"]


class InverseEnv(object):
    def __init__(self, opt):
        self.EnvGen = EnvironmentGenerator(opt)
        self.no_envs = opt["num_processes"]
        self.reward_threshold = opt["utt_reward_threshold_start"]

        RLAgent_opt = {
            "model_file": opt["rl_model_file"],
            "override": {
                "model": "parlai_internal.projects.light.quests.tasks.rl_switch.agents.env_agents"
                ":LightRetrievalAgent",
                "person_tokens": True,
                "eval_candidates": "fixed",
                "encode_candidate_vecs": True,
                "fixed_candidates_path": opt["speech_fixed_candidate_file"],
                "fp16": True,
            },
        }

        EnvAgent_opt = {
            "model_file": opt["env_model_file"],
            "override": {
                "model": "parlai_internal.projects.light.quests.tasks.rl_switch.agents.env_agents"
                ":LightRetrievalAgent",
                "person_tokens": True,
                "eval_candidates": "fixed",
                "encode_candidate_vecs": True,
                "fixed_candidates_path": opt["speech_fixed_candidate_file"],
                "fp16": True,
            },
        }

        self.rl_encoder = create_agent(RLAgent_opt)
        with torch.no_grad():
            self.rl_encoder.model.eval()
        rl_share = self.rl_encoder.share()

        self.env_agent = create_agent(EnvAgent_opt)
        with torch.no_grad():
            self.env_agent.model.eval()
        env_share = self.env_agent.share()

        self.rl_encoders, self.envs = [], []
        self.env_agents = []
        self.previous_dones = []
        for idx in range(self.no_envs):
            rl_share["batchindex"] = idx
            self.rl_encoders.append(create_agent_from_shared(rl_share))
            env_share["batchindex"] = idx
            self.env_agents.append(create_agent_from_shared(env_share))
            self.envs.append(Environment(opt))
            self.previous_dones.append(False)

        self.observation_shape = [768]
        self.action_shape = 6
        self.num_steps = opt["num_steps"]
        self.list_instances = []
        self.opt = opt
        self.fw = open(PARLAI_PATH + "inverse_model_eps.txt", "w")

    def get_new_env(self):
        if not self.list_instances:
            while True:
                self.list_instances += self.EnvGen.environment_generator()
                if self.list_instances:
                    break
        instance = self.list_instances.pop(0)
        return instance

    def goal_achieved(self, env_utt, env_action, possible_acts):

        reward = torch.FloatTensor(self.no_envs, 1)
        done = torch.ByteTensor(self.no_envs, 1)

        for idx in range(self.no_envs):
            act_goal_reward = int(
                env_action[idx]["text"]
                == self.envs[idx].goal.get("action", NULL_TAG["action"])
            )
            utt_goal_reward = (
                0.0
                if self.envs[idx].goal.get("speech", NULL_TAG["speech"])
                == NULL_TAG["speech"]
                else F1Metric._prec_recall_f1_score(
                    self.envs[idx].goal.get("speech", NULL_TAG["speech"]).split(),
                    env_utt[idx]["text"].split(),
                )[2]
            )
            reward_max = max(act_goal_reward, utt_goal_reward)
            if reward_max > self.reward_threshold:
                reward[idx] = reward_max
                done[idx] = True
            elif self.envs[idx].steps >= self.num_steps:
                reward[idx] = 0
                done[idx] = True
            elif possible_acts == []:
                reward[idx] = 0
                done[idx] = True
            else:
                reward[idx] = 0
                done[idx] = False

        return reward, done

    def reset(self):

        obs = []
        for idx in range(self.no_envs):
            # set new env
            self.envs[idx].set_attrs(self.get_new_env())
            # set goal
            self.rl_encoders[idx].history.set_goal(self.envs[idx].goal)

            curr_self_inst = Message(
                {
                    "text": self.envs[idx].self_setting,
                    "ignore_person_tokens": True,
                    "episode_done": False,
                }
            )
            # print('RL SETTING OBS', curr_self_inst)
            obs.append(self.rl_encoders[idx].observe(copy(curr_self_inst)))
            # print("RL SETTING OBS POST OBS", obs)
            setting = self.rl_encoders[idx].history.get_history_str()
            to_write = {"text": setting, "labels": self.envs[idx].labels}
            txt = msg_to_str(to_write)
            self.fw.write(txt + "\n")
            self.fw.flush()

            curr_env_inst = Message(
                {
                    "text": self.envs[idx].partner_setting,
                    "ignore_person_tokens": True,
                    "episode_done": False,
                }
            )

            # print('ENV SETTING OBS', curr_env_inst)
            self.env_agents[idx].observe(copy(curr_env_inst))
            # print('ENV SETTING OBS POST OBS', curr_env_inst)

        output = deepcopy(self.rl_encoder.batch_act(obs))
        # print("RL AGENT OUTPUT", output)
        return output

    def step(self, actions):
        """
        1. Gets the possible actions the environment can take
        at the current state in game.
        2. The environment observes and acts depending on the
        response from RL agent
        3. The environment observes its own action/response
        4. The environment checks if the episode is done
        5. It generates the next embedding for the RL to observe.
        Parameters:
        actions(list of Output): the responses given by RL agent
        Return Value:
        output: List of Outputs from RL agent,
        reward: List of rewards for each episode,
        done: List of whether the episode is done or not
        info: dictionary of meta information
        """

        """ Don't execute self actions because RL Agent returns utts """
        possible_acts = [
            self.envs[idx].graph.get_possible_actions(
                self.envs[idx].partner_id, use_actions=USE_ACTIONS
            )
            for idx in range(self.no_envs)
        ]
        # print("ALL POSSIBLE ACTS:", possible_acts)

        env_utts_obs, env_acts_obs = [], []

        with torch.no_grad():
            # Environment observes RL agent acts
            for idx in range(self.no_envs):
                self.envs[idx].steps += 1
                env_agent_speech_input = {
                    "text": actions[idx]["text"],
                    "tag_token": MISSING_SAY_TAG,
                    "p1_token": PARTNER_SAY,
                    "episode_done": False,
                }
                # print("ENV AGENT SPEECH INPUT", env_agent_speech_input)
                env_utts_obs.append(
                    self.env_agents[idx].observe(
                        copy(env_agent_speech_input), self_observe=False
                    )
                )

            # print("ENV UTT OBS", env_utts_obs)
            env_utt = deepcopy(self.env_agent.batch_act(env_utts_obs))
            # print("ENV UTT OBS POST OBS", env_utts_obs)
            # print("ENV UTT", env_utt)
            for idx in range(self.no_envs):
                env_agent_act_input = {
                    "text": env_utt[idx]["text"],
                    "p1_token": SELF_SAY,
                    "tag_token": MISSING_ACT_TAG,
                    "episode_done": False,
                }
                if possible_acts[idx] != []:
                    env_agent_act_input["label_candidates"] = possible_acts[idx]
                else:
                    env_agent_act_input["label_candidates"] = [
                        "hit person",
                        "hug person",
                    ]
                # print("ENV AGENT ACT INPUT", env_agent_act_input)
                env_acts_obs.append(
                    self.env_agents[idx].observe(
                        copy(env_agent_act_input), self_observe=False
                    )
                )
                # print(self.act_env_agents[idx].history.get_history_str())
            # print("ENV AGENT ACT OBS POST OBS", env_acts_obs)
            env_act = deepcopy(self.env_agent.batch_act(env_acts_obs))

            # print("ENV ACT", env_act)
            for idx in range(self.no_envs):
                if possible_acts[idx] != []:
                    env_agent_post_act_obs = {
                        "text": env_act[idx]["text"],
                        "p1_token": SELF_ACT,
                        "episode_done": False,
                    }
                    # print("ENV AGENT POST ACT OBS", env_agent_post_act_obs)
                    self.env_agents[idx].observe(env_agent_post_act_obs)
                    try:
                        _ = self.envs[idx].graph.parse_exec(
                            self.envs[idx].partner_id, env_act[idx]["text"]
                        )
                    except:
                        print(env_act[idx]["text"])

            reward, done = self.goal_achieved(env_utt, env_act, possible_acts)
            # print("REWARD, DONE", reward, done)
            rl_obs, info = [], []
            for idx in range(self.no_envs):

                if done[idx]:
                    # print("**episode", idx, "done**")
                    info_dict = {"episode": {}}
                    info_dict["episode"]["r"] = reward[idx].item()
                    info_dict["episode"]["done"] = done[idx].item()
                    info_dict["episode"]["steps"] = self.envs[idx].steps
                    if self.envs[idx].labels:
                        if self.envs[idx].labels == actions[idx]["text"]:
                            info_dict["episode"]["hit"] = 1
                        else:
                            info_dict["episode"]["hit"] = 0
                    else:
                        info_dict["episode"]["hit"] = 0
                    info.append(info_dict)

                    # print('UttA obs epi done')
                    self.env_agents[idx].observe(
                        {"episode_done": True}, self_observe=False
                    )

                    # print('RL obs epi done')
                    last_rl_obs = self.rl_encoders[idx].observe(
                        {
                            "text": env_utt[idx]["text"]
                            + "\n"
                            + PARTNER_ACT
                            + env_act[idx]["text"],
                            "p1_token": PARTNER_SAY,
                            "episode_done": True,
                        }
                    )

                    # debug_fw.write()
                    # print(self.rl_encoders[idx].history.get_history_str())

                    self.envs[idx].set_attrs(self.get_new_env())

                    self.rl_encoders[idx].history.set_goal(self.envs[idx].goal)
                    curr_self_inst = {
                        "text": self.envs[idx].self_setting,
                        "ignore_person_tokens": True,
                        "episode_done": False,
                    }
                    # print('RL reset obs')
                    rl_obs.append(
                        self.rl_encoders[idx].observe(
                            copy(curr_self_inst), self_observe=False
                        )
                    )
                    # print(self.rl_encoders[idx].history.get_history_str())
                    sett = self.rl_encoders[idx].history.get_history_str()
                    to_write = {"text": sett, "labels": self.envs[idx].labels}
                    txt = msg_to_str(to_write)
                    self.fw.write(txt + "\n")

                    curr_env_inst = {
                        "text": self.envs[idx].partner_setting,
                        "ignore_person_tokens": True,
                        "episode_done": False,
                    }
                    # print('UttA reset obs')
                    self.env_agents[idx].observe(
                        copy(curr_env_inst), self_observe=False
                    )

                else:
                    encode_model_input = {
                        "text": utt_env_resp[idx]["text"]
                        + "\n"
                        + PARTNER_ACT
                        + act_env_resp[idx]["text"],
                        "p1_token": PARTNER_SAY,
                        "tag_token": MISSING_SELF_SAY,
                        "episode_done": False,
                    }
                    rl_obs.append(
                        self.rl_encoders[idx].observe(copy(encode_model_input))
                    )

            output = deepcopy(self.rl_encoder.batch_act(rl_obs))

        return output, reward, done, info


#
# def make_inverse_envs(opt):
#     envs = InverseWrapper(opt)
#     return envs
#
#
# if __name__ == '__main__':
#     make_inverse_envs(opt)
