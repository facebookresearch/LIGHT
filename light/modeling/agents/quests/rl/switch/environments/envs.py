# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3
import torch
from copy import deepcopy, copy
import pickle
import sys
from collections import deque
import numpy as np
import json

from parlai.core.metrics import F1Metric
from parlai.agents.tfidf_retriever.tokenizers.simple_tokenizer import SimpleTokenizer
from parlai.core.agents import create_agent, create_agent_from_shared
from light.modeling.agents.quests.rl.switch.environments.environment import Environment
from light.modeling.agents.quests.rl.switch.environments.env_generator import (
    EnvironmentGenerator,
)
from light.modeling.agents.quests.rl.shared.process.constants import *
from light.modeling.agents.quests.rl.switch.agents.env_agents import LightRetrievalAgent

RL_MODEL_FILES = {
    "action": {
        10: os.path.join(
            LIGHT_DATAPATH, "rl_quests_resources/actgoals/10clusters/model"
        ),
        100: os.path.join(
            LIGHT_DATAPATH, "rl_quests_resources/actgoals/100clusters/model"
        ),
        500: os.path.join(
            LIGHT_DATAPATH, "rl_quests_resources/actgoals/500clusters/model"
        ),
    },
    "emote": {
        10: os.path.join(
            LIGHT_DATAPATH, "rl_quests_resources/emotegoals/10clusters/model"
        ),
        100: os.path.join(
            LIGHT_DATAPATH, "rl_quests_resources/emotegoals/100clusters/model"
        ),
        500: os.path.join(
            LIGHT_DATAPATH, "rl_quests_resources/emotegoals/500clusters/model"
        ),
    },
}


class EnvironmentWrapper(object):
    def __init__(self, opt):
        self.EnvGen = EnvironmentGenerator(opt)
        self.no_envs = opt["num_processes"]
        self.reward_threshold = opt["utt_reward_threshold_start"]
        if opt.get("model_type", False) == "inverse":
            self.inverse = True
        else:
            self.inverse = False
        self.mean_episode_rewards = deque(maxlen=10)
        self.random_embeddings = {}
        self.tokenizer = SimpleTokenizer()
        self.refill = True
        rl_model_file = RL_MODEL_FILES.get(opt["goal_types"]).get(opt["num_clusters"])

        RLAgent_opt = {
            "model_file": rl_model_file,
            "model": "light.modeling.agents.quests.rl.switch.agents.rl_agent:RLAgent",
            "person_tokens": True,
            "eval_candidates": "fixed",
            "encode_candidate_vecs": True,
            "fixed_candidates_path": opt["speech_fixed_candidate_file"],
            "fp16": True,
            "repeat_blocking_heuristic": False,
        }
        # replicated above
        RLRetrieval_opt = {
            "model": "light.modeling.agents.quests.rl.switch.agents.env_agents:LightRetrievalAgent",
            "person_tokens": True,
            "eval_candidates": "fixed",
            "encode_candidate_vecs": True,
            "fixed_candidates_path": opt["speech_fixed_candidate_file"],
            "fp16": True,
            "repeat_blocking_heuristic": False,
        }

        RLGeneration_opt = {
            "model": "light.modeling.agents.quests.rl.switch.agents.env_agents:LightGeneratorAgent",
            "person_tokens": True,
            "eval_candidates": "fixed",
            "encode_candidate_vecs": True,
            "fixed_candidates_path": opt["speech_fixed_candidate_file"],
            "fp16": True,
            "repeat_blocking_heuristic": False,
        }

        EnvAgent_opt = {
            "model_file": opt["env_model_file"],
            "model": "light.modeling.agents.quests.rl.switch.agents.env_agents:LightRetrievalAgent",
            "person_tokens": True,
            "eval_candidates": "fixed",
            "encode_candidate_vecs": True,
            "fixed_candidates_path": opt["speech_fixed_candidate_file"],
            "fp16": True,
            # 'repeat_blocking_heuristic': False,
        }

        self.rl_encoder = create_agent(RLAgent_opt)
        with torch.no_grad():
            self.rl_encoder.model.eval()
        # share takes the opts from one and shares to another model file w/o reloading
        rl_share = self.rl_encoder.share()

        for key in rl_share["opt"]:
            if key not in RLRetrieval_opt:
                RLRetrieval_opt[key] = rl_share["opt"][key]
        self.rl_retrieval = LightRetrievalAgent(RLRetrieval_opt, shared=rl_share)
        with torch.no_grad():
            self.rl_retrieval.model.eval()
        ret_share = self.rl_retrieval.share()

        self.env_agent = create_agent(EnvAgent_opt)
        with torch.no_grad():
            self.env_agent.model.eval()
        env_share = self.env_agent.share()

        # retrievers takes the cluster and outputs utterance
        # rl retrievers is what needs to be flipped with generator
        # old code RL agent never actually acts
        # one cluster for context for both action and speech
        # encoders take all of context in and output encoding for rl retrieval
        # history for self say partner say self act partner act

        self.rl_encoders, self.rl_retrievers, self.env_agents = [], [], []
        self.envs = []
        for idx in range(self.no_envs):
            rl_share["batchindex"] = idx
            self.rl_encoders.append(create_agent_from_shared(rl_share))
            ret_share["batchindex"] = idx
            self.rl_retrievers.append(create_agent_from_shared(ret_share))
            env_share["batchindex"] = idx
            self.env_agents.append(create_agent_from_shared(env_share))

            self.envs.append(Environment(opt))

        self.observation_shape = [768]
        self.action_shape = opt["num_clusters"]
        self.episode_steps = opt.get("episode_steps")
        if self.episode_steps is None:
            self.episode_steps = opt["num_steps"]
        self.list_instances = []
        self.opt = opt
        self.episode_acts = [[] for i in range(self.no_envs)]
        self.episode_possible_acts = [[] for i in range(self.no_envs)]
        self.previous_rl_obs = []
        self.goal_types = opt["goal_types"].split(",")
        self.i = 0

    def get_env(self):
        """
        Maintains a buffer of environment instances.
        """
        if self.list_instances == []:
            if self.opt["combo"] == "train_ex":
                while self.list_instances == []:
                    self.list_instances += self.EnvGen.from_original_dialogs()
            elif self.opt["combo"] == "train_ex_shuffled":
                self.list_instances = self.EnvGen.from_original_dialogs_shuffled_all()
            elif self.opt["combo"] == "all_goals":
                self.list_instances = self.EnvGen.from_all_possible_goals()
            elif self.opt["combo"] == "fixed_episodes":
                self.list_instances = self.EnvGen.from_fixed_episodes_file()
            elif self.opt["combo"] == "fixed_episodes_test":
                if self.refill:
                    self.list_instances = self.EnvGen.from_fixed_episodes_file()
                    self.refill = False
                else:
                    return None
            elif self.opt["combo"] == "train_ex_generate_examples":
                if self.refill:
                    self.list_instances = (
                        self.EnvGen.from_original_dialogs_shuffled_all(shuffled=False)
                    )
                    self.refill = False
                else:
                    return None
        instance = self.list_instances.pop(0)
        return instance

    def goal_achieved(self, env_utt, env_action, possible_acts):
        """Calculate the reward to return to the RL loop
        Takes into account utt, act, and emote goals.
        Arguments:
        env_utt: batch_act output of the env agent on its utterance turn
        env_act: batch_act output of the env agent on its act turn
        possible_acts: list of strings indicating possible actions for env agent
        Outputs:
        reward: Float Tensor with rewards for each env
        done: Float Tensor with 0 or 1 indicating not done/done with episode
        info: list of dicts containing reward, done, #steps, time limit info
        """
        info = []
        bad_transition = False
        reward = torch.FloatTensor(self.no_envs, 1)
        done = torch.ByteTensor(self.no_envs, 1)
        speech_rewards = []

        for idx in range(self.no_envs):
            info_dict = {"episode": {}}
            act_goal_reward, utt_goal_reward, emote_goal_reward = 0, 0, 0
            if "action" in self.goal_types:
                act_goal_reward = int(
                    env_action[idx]["text"]
                    == self.envs[idx].goal.get("action", NULL_TAG["action"])
                )
            if "speech" in self.goal_types:
                utt_goal_reward = (
                    0.0
                    if self.envs[idx].goal.get("speech", NULL_TAG["speech"])
                    == NULL_TAG["speech"]
                    else self.f1_without_stopwords(
                        self.envs[idx].goal.get("speech", NULL_TAG["speech"]),
                        env_utt[idx]["text"],
                    )[2]
                )
            if "emote" in self.goal_types:
                emote_goal_reward = int(
                    env_action[idx]["text"]
                    == self.envs[idx].goal.get("emote", NULL_TAG["emote"])
                )
            reward_max = max([act_goal_reward, utt_goal_reward, emote_goal_reward])
            reward[idx] = reward_max
            if reward_max >= self.reward_threshold:
                reward[idx] = reward_max
                done[idx] = True
            elif self.envs[idx].steps >= self.episode_steps:
                reward[idx] = 0
                done[idx] = True
                bad_transition = True  # not used
            elif possible_acts == []:
                reward[idx] = 0
                done[idx] = True
            else:
                reward[idx] = 0
                done[idx] = False
            if done[idx]:
                speech_rewards.append(utt_goal_reward)
            info_dict["episode"]["r"] = reward[idx].item()
            info_dict["episode"]["done"] = done[idx].item()
            info_dict["episode"]["steps"] = self.envs[idx].steps
            if bad_transition:
                info_dict["bad_transition"] = True
            info.append(info_dict)

        self.mean_episode_rewards.append(np.mean(speech_rewards))
        if (
            len(self.mean_episode_rewards) == self.mean_episode_rewards.maxlen
            and np.mean(list(self.mean_episode_rewards)) > self.reward_threshold
            and self.reward_threshold < 0.95
        ):
            self.reward_threshold += 0.05
        return reward, done, info

    def reset(self):
        """
        1. Gets new environment settings and sets them
        2. Sets goals for RL encoder and RL retriever
        3. RL encoder, Utt and Act Env models observe their
        respective settings
        4. RL encoder acts and returns an embedding
        Return Value: list of embeddings
        """
        obs = []
        with torch.no_grad():
            end = False
            # All agents observe settings
            for idx in range(self.no_envs):
                try:
                    self.envs[idx].set_attrs(self.get_env())
                except TypeError:
                    end = True

                self.rl_encoders[idx].history.set_goal(self.envs[idx].goal)
                self.rl_retrievers[idx].history.set_goal(self.envs[idx].goal)

                curr_self_inst = {
                    "text": self.envs[idx].self_setting,
                    "ignore_person_tokens": True,
                    "episode_done": False,
                }
                new_obs = self.rl_encoders[idx].observe(copy(curr_self_inst))
                obs.append(copy(new_obs))
                self.previous_rl_obs.append(copy(curr_self_inst))

                curr_env_inst = {
                    "text": self.envs[idx].partner_setting,
                    "ignore_person_tokens": True,
                    "episode_done": False,
                }
                self.env_agents[idx].observe(copy(curr_env_inst))

            if end:
                return _, True
            # get context embeddings
            output = deepcopy(self.rl_encoder.batch_act(obs))
            for_type = output[0]["embedding_ctx"]
            encoded = for_type.new(self.no_envs, for_type.size(0))
            for i in range(self.no_envs):
                if self.opt.get("normalize_rl_input", True):
                    norm = torch.norm(output[i]["embedding_ctx"])
                    encoded[i] = torch.div(output[i]["embedding_ctx"], norm)
                else:
                    encoded[i] = output[i]["embedding_ctx"]
        return encoded, end

    def step(self, action, write_episode=False):
        """
        1. RL retriever model observes the text and the cluster
        chosen by the RL agent
        2. Gets the possible actions the environment can take
        at the current state in game.
        3. The environment observes and acts depending on the
        response from RL agent
        4. The environment observes its own action/response
        5. The environment checks if the episode is done
        6. It generates the next embedding for the RL to observe.
        Parameters:
        action: list of clusters chosen by the RL agent
        Return Value:
        output: List of Outputs from RL agent,
        reward: List of rewards for each episode,
        done: List of whether the episode is done or not
        info: dictionary of meta information
        """
        MISSING_TAG = (
            MISSING_EMOTE_TAG if "emote" in self.goal_types else MISSING_ACT_TAG
        )
        end = False
        if not self.inverse:
            rl_acts = [act.item() for act in action]

        with torch.no_grad():
            # RL retriever observes clusters, then chooses utterance
            rl_utt_obs = []
            for idx in range(self.no_envs):
                if write_episode:
                    self.episode_acts[idx].append(rl_acts[idx])
                if not self.inverse:
                    self.rl_retrievers[idx].history.set_cluster(
                        "_cluster" + str(rl_acts[idx])
                    )
                    rl_utt_obs.append(
                        self.rl_retrievers[idx].observe(self.previous_rl_obs[idx])
                    )
            print("\nRL RET OBS")
            print(rl_utt_obs)
            rl_utts = self.rl_retrieval.batch_act(rl_utt_obs)

            # get possible actions from the environment
            if "emote" in self.goal_types:
                possible_acts = [copy(ALL_EMOTES) for _ in range(self.no_envs)]
            else:
                possible_acts = [
                    list(
                        sorted(
                            self.envs[idx].graph.get_possible_actions(
                                self.envs[idx].partner_id, use_actions=USE_ACTIONS
                            )
                        )
                    )
                    for idx in range(self.no_envs)
                ]

            # environment, RL agent observe RL utt
            env_utt_obs = []
            for idx in range(self.no_envs):
                if write_episode:
                    self.episode_possible_acts[idx].append(copy(possible_acts[idx]))
                self.envs[idx].steps += 1
                rl_encoder_input = {
                    "text": rl_utts[idx]["text"],
                    "p1_token": SELF_SAY,
                    "episode_done": False,
                }
                env_speech_input = {
                    "text": rl_utts[idx]["text"],
                    "p1_token": PARTNER_SAY,
                    "tag_token": MISSING_SAY_TAG,
                    "episode_done": False,
                }
                self.rl_encoders[idx].observe(copy(rl_encoder_input))
                env_utt_obs.append(self.env_agents[idx].observe(copy(env_speech_input)))
            print("\nENV UTT OBS")
            print(env_utt_obs)

            # environment utterance
            env_utt = deepcopy(self.env_agent.batch_act(env_utt_obs))

            # environment, RL agent observe env utt
            env_act_obs = []
            for idx in range(self.no_envs):
                # rl_encoder_input = {
                #     'text': env_utt[idx],
                #     'p1_token': PARTNER_SAY,
                #     'episode_done': False,
                # }
                env_act_input = {
                    "text": env_utt[idx]["text"],
                    "p1_token": SELF_SAY,
                    "tag_token": MISSING_TAG,
                    "episode_done": False,
                }
                if possible_acts[idx] != []:
                    env_act_input["label_candidates"] = possible_acts[idx]
                else:
                    env_act_input["label_candidates"] = ["hit person", "hug person"]
                # self.rl_encoders[idx].observe(
                #     copy(rl_encoder_input)
                # )
                env_act_obs.append(self.env_agents[idx].observe(copy(env_act_input)))
            print("\nENV ACT OBS")
            print(env_act_obs)

            # environment act
            env_act = deepcopy(self.env_agent.batch_act(env_act_obs))

            # env agent observes own act, execute env agent act in game engine
            for idx in range(self.no_envs):
                if possible_acts[idx] != []:
                    self.env_agents[idx].observe(
                        {
                            "text": env_act[idx]["text"],
                            "p1_token": SELF_ACT,
                            "episode_done": False,
                        }
                    )
                    if "action" in self.goal_types:
                        try:
                            _ = self.envs[idx].graph.parse_exec(
                                self.envs[idx].partner_id, env_act[idx]["text"]
                            )
                        except:
                            print("Action cannot be executed ...")
                            print(env_act[idx]["text"])

            # check reward
            reward, done, info = self.goal_achieved(env_utt, env_act, possible_acts)

            rl_obs = []
            self.previous_rl_obs = []
            for idx in range(self.no_envs):
                if done[idx]:
                    # make all agents observe episode_done
                    env_history = self.env_agents[idx].observe({"episode_done": True})
                    self.env_agents[idx].reset()
                    e_done = {
                        "text": env_utt[idx]["text"]
                        + "\n"
                        + PARTNER_ACT
                        + " "
                        + env_act[idx]["text"],
                        "p1_token": PARTNER_SAY,
                        "episode_done": True,
                    }
                    full_history_rl = self.rl_encoders[idx].observe(copy(e_done))
                    print("\nRL ENCODER HISTORY\n")
                    print(full_history_rl)
                    print("\nENV HISTORY\n")
                    print(env_history)
                    self.rl_retrievers[idx].observe(copy(e_done))
                    self.rl_encoders[idx].reset()
                    self.rl_retrievers[idx].reset()

                    if write_episode:
                        info[idx]["text_to_write"] = self.parse_full_history(
                            full_history_rl["full_text"],
                            copy(self.episode_acts[idx]),
                            copy(self.episode_possible_acts[idx]),
                            self.envs[idx].internal_id,
                        )
                        self.episode_acts[idx] = []
                        self.episode_possible_acts[idx] = []

                    # reset the environment with new instance
                    try:
                        self.envs[idx].set_attrs(self.get_env())
                    except TypeError:
                        end = True
                        continue
                    self.rl_encoders[idx].history.set_goal(self.envs[idx].goal)
                    self.rl_retrievers[idx].history.set_goal(self.envs[idx].goal)

                    curr_self_inst = {
                        "text": self.envs[idx].self_setting,
                        "ignore_person_tokens": True,
                        "episode_done": False,
                    }
                    rl_obs.append(
                        copy(self.rl_encoders[idx].observe(copy(curr_self_inst)))
                    )
                    self.previous_rl_obs.append(copy(curr_self_inst))
                    curr_env_inst = {
                        "text": self.envs[idx].partner_setting,
                        "ignore_person_tokens": True,
                        "episode_done": False,
                    }
                    self.env_agents[idx].observe(copy(curr_env_inst))
                else:
                    encode_model_input = {
                        "text": env_utt[idx]["text"]
                        + "\n"
                        + PARTNER_ACT
                        + " "
                        + env_act[idx]["text"],
                        "p1_token": PARTNER_SAY,
                        "episode_done": False,
                    }
                    self.previous_rl_obs.append(copy(encode_model_input))
                    rl_obs.append(
                        copy(self.rl_encoders[idx].observe(copy(encode_model_input)))
                    )
            if end:
                return None, reward, done, info, end
            output = deepcopy(self.rl_encoder.batch_act(rl_obs))
            print("OUTPUT", output)
            for_type = output[0]["embedding_ctx"]
            encoded = for_type.new(self.no_envs, for_type.size(0))
            for i in range(self.no_envs):
                if self.opt.get("normalize_rl_input", True):
                    norm = torch.norm(output[i]["embedding_ctx"])
                    encoded[i] = torch.div(output[i]["embedding_ctx"], norm)
                else:
                    encoded[i] = output[i]["embedding_ctx"]
        return encoded, reward, done, info, end

    def parse_full_history(
        self, history_text, all_actions, all_possible_acts, internal_id
    ):
        history_split = history_text.split("\n")
        history_arr = []
        for s in history_split:
            if len(s) == 0:
                continue
            if s[0] == "_":
                ssplit = s.split(" ", 1)
                if len(ssplit) < 2:
                    if s[:8] == "_cluster":
                        continue
                    if s[:13] == "_missing_self":
                        continue

                    ssplit = [s, " "]
                else:
                    ssplit[0] = ssplit[0].replace("_future_partner", "_goal")
            else:
                ssplit = [" ", s]
            history_arr.append(ssplit)

        history_json = {"history_text": history_arr}
        history_json["actions"] = all_actions
        history_json["possible acts"] = all_possible_acts
        history_json["internal_id"] = internal_id
        return json.dumps(history_json)

    def debug_step(self):
        """
        This function is used to pass through the settings of the
        train set and exhaustively search through the 50 clusters
        to get the samples which reach the goal with one or more
        cluster tags.
        Every 1000 episodes, it writes the filtered samples in a
        pickle file.
        """
        MISSING_TAG = (
            MISSING_EMOTE_TAG if "emote" in self.goal_types else MISSING_ACT_TAG
        )
        self.achievable = []
        all_achievable = 0
        episode_count, save_count, achievable_eps = 0, 0, 0
        done_flag = False
        while True:
            while self.list_instances == []:
                orig = self.EnvGen.from_original_dialogs(debug_mode=True)
                if orig is None:
                    done_flag = True
                    break
                else:
                    self.list_instances += orig

            if done_flag:
                break

            with torch.no_grad():
                instance = self.list_instances.pop(0)
                instance["cluster_label"] = []
                episode_count += 1

                if episode_count % 20 == 0:
                    print("Done: " + str(episode_count))
                    print(str(achievable_eps), "were achievable episodes")
                    print(str(all_achievable), "achievable episode-cluster combos")
                    sys.stdout.flush()

                if len(self.achievable) >= 10:
                    save_count += 1
                    with open(
                        "achievable_settings_"
                        + str(save_count)
                        + "_"
                        + str(episode_count)
                        + ".pkl",
                        "wb",
                    ) as out:
                        pickle.dump(self.achievable, out)
                    self.achievable = []

                for cluster in range(opt["num_clusters"]):
                    self.envs[0].set_attrs(instance)
                    if "emote" in self.goal_types:
                        possible_acts = copy(ALL_EMOTES)
                    else:
                        possible_acts = [
                            self.envs[0].graph.get_possible_actions(
                                self.envs[0].partner_id, use_actions=USE_ACTIONS
                            )
                        ]

                    self.rl_retrievers[0].history.set_goal(self.envs[0].goal)
                    curr_self_inst = {
                        "text": self.envs[0].self_setting,
                        "ignore_person_tokens": True,
                        "episode_done": False,
                    }

                    curr_env_inst = {
                        "text": self.envs[0].partner_setting,
                        "ignore_person_tokens": True,
                        "episode_done": False,
                    }

                    self.env_agents[0].observe(copy(curr_env_inst))

                    rl_ret_obs = []
                    self.rl_retrievers[0].history.set_cluster("_cluster" + str(cluster))
                    rl_next_obs = self.rl_retrievers[0].observe(
                        copy(copy(curr_self_inst))
                    )
                    rl_ret_obs.append(rl_next_obs)
                    actions = self.rl_retrieval.batch_act(rl_ret_obs)
                    # get possible actions from the environment

                    env_utt_obs, env_act_obs = [], []

                    self.envs[0].steps += 1
                    env_agent_input = {
                        "text": actions[0]["text"],
                        "p1_token": PARTNER_SAY,
                        "tag_token": MISSING_SAY_TAG,
                        "episode_done": False,
                    }
                    env_next_utt_obs = self.env_agents[0].observe(copy(env_agent_input))
                    env_utt_obs.append(env_next_utt_obs)
                    env_utt = deepcopy(self.env_agent.batch_act(env_utt_obs))
                    act_input = {
                        "text": env_utt[0]["text"],
                        "p1_token": SELF_SAY,
                        "tag_token": MISSING_TAG,
                        "episode_done": False,
                    }
                    if possible_acts[0] != []:
                        act_input["label_candidates"] = possible_acts[0]
                    else:
                        act_input["label_candidates"] = ["hit person", "hug person"]
                    env_next_act_obs = self.env_agents[0].observe(copy(act_input))
                    env_act_obs.append(env_next_act_obs)
                    env_act = deepcopy(self.env_agent.batch_act(env_act_obs))
                    # Utterance agent observes what act agent said

                    if possible_acts[0] != []:
                        self.env_agents[0].observe(
                            {
                                "text": env_act[0]["text"],
                                "p1_token": SELF_ACT,
                                "episode_done": False,
                            }
                        )
                    try:
                        _ = self.envs[0].graph.parse_exec(
                            self.envs[0].partner_id, env_act[0]["text"]
                        )
                    except:
                        print("Action cannot be executed ...")
                        print(env_act[0]["text"])

                    # make all agents observe episode_done
                    self.env_agents[0].observe({"episode_done": True})

                    e_done = {
                        "text": env_utt[0]["text"]
                        + "\n"
                        + PARTNER_ACT
                        + " "
                        + env_act[0]["text"],
                        "p1_token": PARTNER_SAY,
                        "episode_done": True,
                    }
                    self.rl_retrievers[0].observe(copy(e_done))

                    if self.envs[0].goal.get("action") == env_act[0]["text"]:
                        all_achievable += 1
                        instance["cluster_label"].append(cluster)

                if instance["cluster_label"] != []:
                    achievable_eps += 1
                    self.achievable.append(copy(instance))

        if self.achievable != []:
            save_count += 1
            with open(
                "achievable_settings_"
                + str(save_count)
                + "_"
                + str(episode_count)
                + ".pkl",
                "wb",
            ) as out:
                pickle.dump(self.achievable, out)

    def generate_examples_step(self, action):
        """
        1. RL retriever model observes the text and the cluster
        chosen by the RL agent
        2. Gets the possible actions the environment can take
        at the current state in game.
        3. The environment observes and acts depending on the
        response from RL agent
        4. The environment observes its own action/response
        5. The environment checks if the episode is done
        6. It generates the next embedding for the RL to observe.
        Parameters:
        action: list of clusters chosen by the RL agent
        Return Value:
        output: List of Outputs from RL agent,
        reward: List of rewards for each episode,
        done: List of whether the episode is done or not
        info: dictionary of meta information
        """

        MISSING_TAG = (
            MISSING_EMOTE_TAG if "emote" in self.goal_types else MISSING_ACT_TAG
        )
        # get clusters that RL Agent selected
        rl_acts = [act.item() for act in action]
        rl_ret_obs = []
        # combine the chosen cluster with the context
        with torch.no_grad():
            for idx in range(self.no_envs):
                self.episode_acts[idx].append(rl_acts[idx])
                self.rl_retrievers[idx].history.set_cluster(
                    "_cluster" + str(rl_acts[idx])
                )

            # get responses from RL Agent and that should be responses
            actions = self.rl_retrieval.batch_act(rl_ret_obs)

            # get possible actions from the environment
            if "emote" in self.goal_types:
                possible_acts = [copy(ALL_EMOTES) for _ in range(self.no_envs)]
            else:
                possible_acts = [
                    list(
                        sorted(
                            self.envs[idx].graph.get_possible_actions(
                                self.envs[idx].partner_id, use_actions=USE_ACTIONS
                            )
                        )
                    )
                    for idx in range(self.no_envs)
                ]

            env_utt_obs, env_act_obs = [], []

            for idx in range(self.no_envs):

                self.episode_possible_acts[idx].append(copy(possible_acts[idx]))
                self.envs[idx].steps += 1
                env_speech_input = {
                    "text": actions[idx]["text"],
                    "p1_token": PARTNER_SAY,
                    "tag_token": MISSING_SAY_TAG,
                    "episode_done": False,
                }
                rl_encoder_input = {
                    "text": actions[idx]["text"],
                    "p1_token": SELF_SAY,
                    "episode_done": False,
                }
                self.rl_encoders[idx].observe(copy(rl_encoder_input))
                self.rl_retrievers[idx].observe(copy(rl_encoder_input))
                env_utt_obs.append(self.env_agents[idx].observe(copy(env_speech_input)))

            env_utt = deepcopy(self.env_agent.batch_act(env_utt_obs))

            for idx in range(self.no_envs):
                act_input = {
                    "text": env_utt[idx]["text"],
                    "p1_token": SELF_SAY,
                    "tag_token": MISSING_TAG,
                    "episode_done": False,
                }
                if possible_acts[idx] != []:
                    act_input["label_candidates"] = possible_acts[idx]
                else:
                    act_input["label_candidates"] = ["hit person", "hug person"]
                env_act_obs.append(self.env_agents[idx].observe(copy(act_input)))

            env_act = deepcopy(self.env_agent.batch_act(env_act_obs))

            # Utterance agent observes what act agent said
            for idx in range(self.no_envs):
                if possible_acts[idx] != []:
                    self.env_agents[idx].observe(
                        {
                            "text": env_act[idx]["text"],
                            "p1_token": SELF_ACT,
                            "episode_done": False,
                        }
                    )
                    try:
                        _ = self.envs[idx].graph.parse_exec(
                            self.envs[idx].partner_id, env_act[idx]["text"]
                        )
                    except:
                        print("Action cannot be executed ...")
                        print(env_act[idx]["text"])

            reward, done, info = self.goal_achieved(env_utt, env_act, possible_acts)
            rl_obs = []
            self.previous_rl_obs = []

            for idx in range(self.no_envs):
                if done[idx]:
                    # make all agents observe episode_done
                    self.env_agents[idx].observe({"episode_done": True})

                    e_done = {
                        "text": env_utt[idx]["text"]
                        + "\n"
                        + PARTNER_ACT
                        + " "
                        + env_act[idx]["text"],
                        "p1_token": PARTNER_SAY,
                        "episode_done": True,
                    }
                    self.rl_encoders[idx].observe(copy(e_done))
                    full_history_rl = self.rl_retrievers[idx].observe(copy(e_done))
                    info[idx]["text_to_write"] = self.parse_full_history(
                        full_history_rl["full_text"],
                        self.episode_acts[idx],
                        self.episode_possible_acts[idx],
                        self.envs[idx].internal_id,
                    )
                    self.episode_acts[idx] = []
                    self.episode_possible_acts[idx] = []
                    # reset the environment with new instance
                    new_env = self.get_env()
                    if new_env is None:
                        return None, reward, done, info
                    self.envs[idx].set_attrs(new_env)
                    self.rl_encoders[idx].history.set_goal(self.envs[idx].goal)
                    self.rl_retrievers[idx].history.set_goal(self.envs[idx].goal)

                    curr_self_inst = {
                        "text": self.envs[idx].self_setting,
                        "ignore_person_tokens": True,
                        "episode_done": False,
                    }
                    rl_obs.append(self.rl_encoders[idx].observe(copy(curr_self_inst)))
                    self.previous_rl_obs.append(curr_self_inst)

                    curr_env_inst = {
                        "text": self.envs[idx].partner_setting,
                        "ignore_person_tokens": True,
                        "episode_done": False,
                    }
                    self.env_agents[idx].observe(copy(curr_env_inst))
                else:
                    encode_model_input = {
                        "text": env_utt[idx]["text"]
                        + "\n"
                        + PARTNER_ACT
                        + " "
                        + env_act[idx]["text"],
                        "p1_token": PARTNER_SAY,
                        "episode_done": False,
                    }
                    rl_obs.append(
                        self.rl_encoders[idx].observe(copy(encode_model_input))
                    )
                    self.previous_rl_obs.append(copy(encode_model_input))
            output = deepcopy(self.rl_encoder.batch_act(rl_obs))
            for_type = output[0]["embedding_ctx"]
            encoded = for_type.new(self.no_envs, for_type.size(0))
            for i in range(self.no_envs):
                if self.opt.get("normalize_rl_input", True):
                    norm = torch.norm(output[i]["embedding_ctx"])
                    encoded[i] = torch.div(output[i]["embedding_ctx"], norm)
                else:
                    encoded[i] = output[i]["embedding_ctx"]
        return encoded, reward, done, info

    def f1_without_stopwords(self, sent1, sent2):
        tklist1 = self.tokenizer.tokenize(sent1).words()
        tklist2 = self.tokenizer.tokenize(sent2).words()
        tklist1 = [tk.lower() for tk in tklist1]
        tklist2 = [tk.lower() for tk in tklist2]
        if self.opt.get("no_stopwords", False):
            tklist1 = [tk for tk in tklist1 if tk not in STOP_WORDS]
            tklist2 = [tk for tk in tklist2 if tk not in STOP_WORDS]
        return F1Metric._prec_recall_f1_score(tklist1, tklist2)
