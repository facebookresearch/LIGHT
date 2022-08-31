# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import torch
from copy import deepcopy, copy
import pickle
import sys
import random
from collections import deque
import numpy as np
import json
import math

import torch.nn.functional as F
from parlai.core.metrics import F1Metric
from parlai.agents.tfidf_retriever.tokenizers.simple_tokenizer import SimpleTokenizer
from parlai.core.agents import create_agent, create_agent_from_shared
from light.modeling.agents.quests.rl.switch.environments.environment import Environment
from light.modeling.agents.quests.rl.switch.environments.env_generator import (
    EnvironmentGenerator,
)
from light.modeling.agents.quests.rl.shared.process.constants import *


SAMPLE_INDS = [1, 100, 1000, 2000, 5000, 10000, 20000, 50000, 95000]
SUBSAMPLE_CANDS = -1

SWITCH_PREPEND = [SELF_ACT, SELF_SAY]
SWITCH_PARTNER_PREPEND = [PARTNER_ACT, PARTNER_SAY]


def add_scoring_model(opt, model_key):
    if opt.get("shared_scoring_params") is None:
        opt["shared_scoring_params"] = {}
    bot_params = opt["shared_bot_params"]
    params = bot_params[model_key]
    scoring_params = params.copy()
    scoring_params["opt"] = params["opt"].copy()
    scoring_params["opt"]["use_reply"] = "none"
    scoring_params["opt"]["override"] = params["opt"]["override"].copy()
    scoring_params["opt"]["override"]["use_reply"] = "none"
    opt["shared_scoring_params"][model_key] = scoring_params


class TopKEnvironmentWrapper(object):
    def __init__(self, opt):
        self.dm = opt["dm"]
        self.EnvGen = EnvironmentGenerator(opt)
        self.no_envs = opt["num_processes"]
        self.reward_threshold = opt["utt_reward_threshold_start"]
        self.mean_episode_rewards = deque(maxlen=10)
        self.random_embeddings = {}
        self.tokenizer = SimpleTokenizer()
        self.refill = True

        if opt["flow_encoder"]:
            datatype = "train"
        else:
            datatype = "test"

        if "bimodel" in opt["enc_type"]:
            model_type = "from light.modeling.agents.quests.rl.switch.agents.rl_agent:TopKRLAgentBi"
        else:
            model_type = "from light.modeling.agents.quests.rl.switch.agents.rl_agent:TopKRLAgent"
        RLAgent_opt = {
            "model_file": opt["rl_model_file"],
            "override": {
                "model": model_type,
                "person_tokens": True,
                "eval_candidates": "fixed",
                "encode_candidate_vecs": True,
                "fixed_candidates_path": opt["quest_all_cands"],
                "fp16": True,
                "rank_top_k": 1,  # opt['k_value'],
                "path": opt["path"],
                "datatype": datatype,
                "text_truncate": 768,
                "eval_mode": opt["eval_mode"],
                "data-parallel": True,
                "enc_type": opt["enc_type"],
                "act_value": opt["act_value"]
                # 'poly-n-codes': 5,
            },
        }

        EnvAgent_opt = {
            "model_file": opt["env_model_file"],
            "override": {
                "model": "parlai_internal.projects.light.quests.tasks.rl_switch.agents.env_agents:LightRetrievalAgent",
                "person_tokens": True,
                "eval_candidates": "fixed",
                "encode_candidate_vecs": True,
                "fixed_candidates_path": opt["env_all_cands"],
                "fp16": True,
                "path": opt["path"],
                "eval_mode": opt["eval_mode"],
                "data-parallel": True,
                "text_truncate": 768,
            },
        }
        if self.dm:
            DMAgent_opt = {
                "model_file": opt["dm_model_file"],
                "override": {
                    "model": "parlai_internal.projects.light.quests.tasks.rl_switch.agents.env_agents:LightDMAgent",
                    "person_tokens": True,
                    "eval_candidates": "fixed",
                    "encode_candidate_vecs": True,
                    "fixed_candidates_path": opt["speech_fixed_candidate_file"],
                    "fp16": True,
                    "path": opt["path"],
                    "eval_mode": opt["eval_mode"],
                    "data-parallel": True,
                    "boring_alpha": 50,
                    "to_speaker_bonus": 20,
                    "from_speaker_bonus": 20,
                    "text_truncate": 768,
                },
            }

            self.scoring_agent = create_agent(DMAgent_opt)
            self._init_acting_score_agent()

            with torch.no_grad():
                self.scoring_agent.model.eval()
            scoring_share = self.scoring_agent.share()

        self.rl_encoder = create_agent(RLAgent_opt)
        if opt["flow_encoder"] == "false":
            with torch.no_grad():
                self.rl_encoder.model.eval()
        else:
            self.rl_encoder.model.train()
            self.rl_encoder.is_training = True
        rl_share = self.rl_encoder.share()

        self.env_agent = create_agent(EnvAgent_opt)
        # self.env_agent.model.to('cuda:1')
        with torch.no_grad():
            self.env_agent.model.eval()
        env_share = self.env_agent.share()

        self.rl_encoders, self.env_agents, self.scoring_agents = [], [], []
        self.envs = []
        for idx in range(self.no_envs):
            rl_share["batchindex"] = idx
            self.rl_encoders.append(create_agent_from_shared(rl_share))
            env_share["batchindex"] = idx
            self.env_agents.append(create_agent_from_shared(env_share))
            if self.dm:
                scoring_share["batchindex"] = idx
                self.scoring_agents.append(create_agent_from_shared(scoring_share))
            self.envs.append(Environment(opt))

        # if opt['flow_encoder']:
        #    self.observation_shape = [384]#[opt['k_value'] + 1, 768]
        # else:
        # self.observation_shape = [768]#[opt['k_value'] + 1, 768]
        shape0 = 1
        enc_shape = self.rl_encoder.opt["embedding_size"]
        if "poly_n_codes" in self.rl_encoder.opt.keys():
            shape0 = self.rl_encoder.opt["poly_n_codes"]

        if "text" in opt["enc_type"]:
            shape0 = 1
            enc_shape = 768

        if "cand" in opt["enc_type"]:
            shape0 += opt["act_value"]

        self.observation_shape = [shape0, enc_shape]
        self.action_shape = opt["k_value"]
        self.action_size = opt["act_value"]
        self.episode_steps = opt.get("episode_steps")
        if self.episode_steps is None:
            self.episode_steps = opt["num_steps"]
        self.list_instances = []
        self.opt = opt
        self.episode_acts = [[] for i in range(self.no_envs)]
        self.episode_possible_acts = [[] for i in range(self.no_envs)]
        self.goal_types = opt["goal_types"].split(",")
        self.i = 0

        self.cand_actions = {i: [] for i in range(self.no_envs)}

        self.load_act_cands(opt)

        self.prepped_cand_scores = [[] * self.no_envs]
        self.switch_steps = self.opt["switch_steps"]

    def _init_acting_score_agent(self):
        """Initialize the special acting score agent"""
        # self.scoring_agent.observe(obs)

        # mark this agent as the special acting score agent
        self.scoring_agent.actingscore = True
        # override eval step here
        self.scoring_agent.eval_step = self.scoring_agent.eval_step_scoresonly

        self.subsamp = SUBSAMPLE_CANDS
        if self.subsamp < 0 or self.subsamp > max(SAMPLE_INDS):
            # no subsampling
            self.SAMPLE_INDS = SAMPLE_INDS
            return

        # Subsample the candidates
        original_len = len(self.scoring_agent.fixed_candidates)
        print(
            " [ WARNING: Subsampling candidates for the acting "
            "score agent to {} total ]".format(self.subsamp)
        )
        self.scoring_agent.subsample_cands(self.subsamp)

        # now redefine sample inds appropriately ..
        ratio = original_len / self.subsamp
        self.SAMPLE_INDS = [math.floor(x / ratio) for x in SAMPLE_INDS if x > 0]

    def set_fixed_cand_scores(self, batch):
        """
        Compute the set of scores for candidates at various score
        levels to later compare the human utterance score to
        """
        self.scoring_agent.opt["eval_candidates"] = "fixed"
        self.scoring_agent.eval_candidates = "fixed"  # set candidates
        # _ = self.scoring_agent[idx].batch_act([batch])
        self.scoring_agent.batch_act(batch)
        self.prepped_cand_scores = self.scoring_agent.scores

    def get_pos_human_msg(self, calc_score, scores):
        """
        Get the model score of the human message and compare to fixed cands.
        """
        # human_score = float(self.scoring_agent[idx].score_one_candidate(human_msg))
        human_rank = int((scores > calc_score).sum())
        return human_rank, calc_score

    def get_acting_score(self, batch):
        """Get the score by which the ranking model would have
        ranked the given human message at based on the currently
        scored candidates
        """
        act_scores = []

        scores = self.scoring_agent.score_one_candidate(batch)

        for idx in range(self.no_envs):
            calc_score = scores[idx, 0].squeeze(0)
            prep_score = self.prepped_cand_scores[idx, :].squeeze(0)
            pos, score = self.get_pos_human_msg(calc_score, prep_score)

            score = 0
            if pos < self.SAMPLE_INDS[1]:  # in top 100
                score = 4
            elif pos < self.SAMPLE_INDS[2]:  # in top 1000
                score = 3
            elif pos < self.SAMPLE_INDS[3]:  # in top 2000
                score = 2

            act_scores.append(score)
        return act_scores

    def load_act_cands(self, opt):
        with open(opt["act_fixed_candidate_file"], "r") as f:
            self.all_act_cands = [a.strip() for a in f.readlines()]
            # random.shuffle(self.all_act_cands)
        with open(opt["speech_fixed_candidate_file"], "r") as f:
            self.all_speech_cands = [a.strip() for a in f.readlines()]

        with open(opt["env_act_cands"], "r") as f:
            self.env_act_cands = [a.strip() for a in f.readlines()]

        self.cache_set_act_cands, self.cache_set_speech_cands = [
            [(a, [0]) for a in self.all_act_cands],
            [(a, [0]) for a in self.all_speech_cands],
        ]

    def set_candidates(self, output):
        # curr_deter_cands = []
        # for c in self.all_act_cands:
        #    loc = output['cands'].index(c)
        #    curr_deter_cands.append((output['cands'][loc], output['cand_hs'][loc]))
        # assert [c[0] for c in curr_deter_cands] == self.all_act_cands
        return (
            self.cache_set_act_cands,
            self.cache_set_speech_cands,
        )  # [[(a, [0]) for a in self.all_act_cands], [(a, [0]) for a in self.all_speech_cands]]#curr_deter_cands

    def get_env(self):
        """
        Maintains a buffer of instances.
        There are three ways of refilling the buffer:
        1. from the original dialogs
        2. from the achievable file
        3. generate instances on the fly
        """
        if self.list_instances == []:
            if self.opt["combo"] == "train_ex":
                while self.list_instances == []:
                    self.list_instances += self.EnvGen.from_original_dialogs()
            elif self.opt["combo"] == "train_ex_shuffled":
                self.list_instances += self.EnvGen.from_original_dialogs_shuffled_all()
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
        # print(instance['goal']['action_seq'])
        return instance

    def goal_achieved(
        self, env_utt, self_action, possible_acts, dm_scores=None, switch=None
    ):
        if dm_scores is None:
            dm_scores = [0] * self.no_envs
        info = []
        bad_transition = False
        reward = torch.FloatTensor(self.no_envs, 1)
        done = torch.ByteTensor(self.no_envs, 1)
        speech_rewards = []
        # print([(self.envs[idx].goal.get('action', NULL_TAG['action']), env_action[idx]) for idx in range(self.no_envs)])

        for idx in range(self.no_envs):
            info_dict = {"episode": {}}
            act_goal_reward, utt_goal_reward = 0, 0
            if "action" in self.goal_types:
                # act_goal_reward, done[idx] = self.envs[idx].quest.act(self.envs[idx].goal.get('action', NULL_TAG['action']))
                act_goal_reward, done_act = 0, False
                if self.opt["task_type"] == "fwd" or self.opt["task_type"] == "all":
                    act_goal_reward, done_act = self.envs[idx].quest.act(
                        self_action[idx], self.envs[idx].self_id, self.opt["eval_mode"]
                    )

                reverse_goal_reward, done_reverse_act = 0, False
                if self.opt["task_type"] == "rev" or self.opt["task_type"] == "all":
                    reverse_goal_reward, done_reverse_act = self.envs[
                        idx
                    ].quest.reverse_act(env_utt[idx]["text"], self.envs[idx].partner_id)
                done[idx] = done_act or done_reverse_act

            reward_max = max([act_goal_reward, reverse_goal_reward])
            if switch[idx] == 1:
                reward[idx] = reward_max + dm_scores[idx]

                # if self_action[idx] in self.envs[idx].quest.possible_says:
                #    reward[idx] += self.envs[idx].quest.rewshape
            else:
                reward[idx] = reward_max
            """if reward_max >= self.reward_threshold:
                reward[idx] = reward_max
                done[idx] = True"""
            if self.envs[idx].steps >= self.episode_steps:
                reward[idx] = 0
                done[idx] = True
                bad_transition = True  # not used

            # else:
            #    reward[idx] = 0
            #    done[idx] = False
            # if done[idx]:
            #    speech_rewards.append(utt_goal_reward)
            info_dict["episode"]["r"] = reward[idx].item()
            # print(reward[idx].item())
            # print('------')
            info_dict["episode"]["score"] = self.envs[idx].quest.score
            info_dict["episode"]["real_act_score"] = self.envs[idx].quest.real_act_score
            info_dict["episode"]["real_speech_score"] = self.envs[
                idx
            ].quest.real_speech_score
            info_dict["episode"]["done"] = done[idx].item()
            info_dict["episode"]["steps"] = self.envs[idx].steps
            if bad_transition:
                info_dict["bad_transition"] = True
            info.append(info_dict)

        # self.mean_episode_rewards.append(np.mean(speech_rewards))

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
        dm_obs = []
        with torch.no_grad():
            end = False
            # All agents observe settings
            for idx in range(self.no_envs):
                # try:
                self.envs[idx].set_attrs(self.get_env())
                """except TypeError:
                    end = True
                    continue"""

                self.envs[idx].quest.reset()

                curr_self_inst = {
                    #'text': self.envs[idx].self_setting,
                    "text": "",
                    "ignore_person_tokens": True,
                    "episode_done": False,
                }
                self.rl_encoders[idx].history.set_context(self.envs[idx].self_setting)

                new_obs = self.rl_encoders[idx].observe(copy(curr_self_inst))
                # Giving it actions instead of utterances
                # self.set_act_cands(idx)
                obs.append(copy(new_obs))

                curr_env_inst = {
                    "text": self.envs[idx].partner_setting,
                    "ignore_person_tokens": True,
                    "episode_done": False,
                }
                self.env_agents[idx].observe(copy(curr_env_inst))
                if self.dm:
                    dm_obs.append(self.scoring_agents[idx].observe(copy(curr_env_inst)))
                # self.set_fixed_cand_scores(idx, curr_env_inst)
        if end:
            return None, True
        if self.dm:
            self.set_fixed_cand_scores(dm_obs)

        # encoded = []

        for i in range(self.no_envs):
            print(self.envs[i].goal)
        # print(self.all_act_cands)
        '''if self.opt['flow_encoder']:
            output = [None] * self.no_envs
            """for idx in range(self.no_envs):
                rl_obs[idx]['labels'] = ['test']
            output = self.rl_encoder.batch_act(rl_obs)"""
            encoded = []
            for idx in range(self.no_envs):
                tar = torch.zeros(768)
                src = obs[idx]['text_vec']
                tar[:obs[idx]['text_vec'].size(0)] = src
                encoded.append(tar.unsqueeze(0))

            encoded = torch.cat(encoded, dim=0)
        else:'''
        switch = self.generate_switch()
        for idx in range(self.no_envs):
            obs[idx]["label_indices"] = self.get_cand_indices(idx, switch[idx])
        output = self.rl_encoder.batch_act(obs)
        encoded = torch.cat(
            [output[i]["embedding_ctx"].unsqueeze(0) for i in range(self.no_envs)],
            dim=0,
        )

        if self.opt["flow_encoder"] == "true":
            for idx in range(self.no_envs):
                obs[idx]["labels"] = ""

        for i in range(self.no_envs):
            self.envs[i].rl_say_mappings = self.set_candidates(output[i])
        # valid_masks = self.generate_valid_masks()
        return encoded, obs, switch, end

    def get_cand_indices(self, idx, switch):
        ret = []
        if switch == 0:
            acts = (
                self.envs[idx].goal["action_seq"] + self.envs[idx].quest.possible_acts
            )
            # acts = self.envs[idx].goal['action_seq']
            # print(acts)
            # for act in self.envs[idx].goal['action_seq']:
            #    assert act in self.all_act_cands
            for act in acts:
                try:
                    mask_idx = self.all_act_cands.index(act)
                    # print(mask_idx)
                    ret.append(mask_idx)
                except ValueError:
                    # print(act)
                    pass
            cutoff = min(self.opt["act_value"], len(ret))
            return ret[:cutoff]
        else:
            acts = (
                self.envs[idx].goal["speech_seq"] + self.envs[idx].quest.possible_says
            )
            # acts = self.envs[idx].goal['action_seq']
            # print(acts)
            # for act in self.envs[idx].goal['action_seq']:
            #    assert act in self.all_act_cands
            for act in acts:
                try:
                    mask_idx = self.all_speech_cands.index(act) + len(
                        self.all_act_cands
                    )
                    # print(mask_idx)
                    ret.append(mask_idx)
                except ValueError:
                    # print(act)
                    pass
            cutoff = min(self.opt["act_value"], len(ret))
            return ret[:cutoff]

    def step(self, action, switch, write_episode=False):
        """
        1. Agents observe the utterance chosen by the RL model
        2. Get the possible actions the environment can take
        at the current state in game.
        3. The environment observes and acts depending on the
        response from RL agent
        4. The environment observes its own action/response
        5. The environment checks if the episode is done
        6. It generates the next embedding for the RL to observe.
        Parameters:
        action: list of clusters chosen by the RL agent
        switch: list of whether the actions are actions (0) or speech (1)
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
        valid_masks = self.generate_valid_masks()
        # get utterance that RL Agent selected
        rl_acts = [act.squeeze() for act in action]
        dm_obs = []
        with torch.no_grad():
            rl_says = []
            for idx in range(self.no_envs):
                self.episode_acts[idx].append(rl_acts[idx])
                # TODO HERE CHANGE THIS TO ACTION MAPPINGS
                # THEN JUST CALCULATE REWARD BASED ON THAT
                # THEN HAVE THE ENV OBSERVE THAT ACTION/EXECUTE IT IN THE EGINE AND USE IT AS ENCODING FOR NEXT STEP
                cand_chosen, _ = self.envs[idx].rl_say_mappings[switch[idx]][
                    rl_acts[idx][switch[idx]].item()
                ]
                rl_says.append(cand_chosen)

            # get possible actions from the environment
            # if 'emote' in self.goal_types:
            #    possible_acts = [copy(ALL_EMOTES) for _ in range(self.no_envs)]
            # else:
            possible_acts = [
                self.envs[idx].quest.possible_acts for idx in range(self.no_envs)
            ]
            """[
                    list(
                        sorted(
                            self.envs[idx].graph.get_possible_actions(
                                self.envs[idx].partner_id, use_actions=USE_ACTIONS
                            )
                        )
                    )
                    for idx in range(self.no_envs)
                ]"""

            env_utt_obs = []
            for idx in range(self.no_envs):
                if write_episode:
                    self.episode_possible_acts[idx].append(
                        self.envs[idx].quest.possible_acts
                    )
                self.envs[idx].steps += 1
                rl_encoder_input = {
                    "text": rl_says[idx],
                    "p1_token": SWITCH_PREPEND[switch[idx]],
                    "episode_done": False,
                }
                env_speech_input = {
                    "text": rl_says[idx],
                    "p1_token": SWITCH_PARTNER_PREPEND[switch[idx]],
                    "tag_token": MISSING_SAY_TAG,
                    "episode_done": False,
                }
                self.rl_encoders[idx].observe(copy(rl_encoder_input))
                env_utt_obs.append(self.env_agents[idx].observe(copy(env_speech_input)))
                if self.dm:
                    dm_input = {
                        "text": rl_says[idx],
                        "label_candidates": [rl_says[idx]],
                        "p1_token": SWITCH_PARTNER_PREPEND[switch[idx]],
                        "tag_token": MISSING_SAY_TAG,
                        "episode_done": False,
                    }
                    dm_obs.append(self.scoring_agents[idx].observe(dm_input))

            # environment utterance
            env_utt = self.env_agent.batch_act(env_utt_obs)
            # env_utt = [{'id': 'LightRetrieval',
            #            'episode_done': False,
            #             'text': "",
            #             'text_candidates': []}] * self.no_envs
            for idx in range(self.no_envs):
                self.envs[idx].quest.possible_says = env_utt[idx]["text_candidates"]

            dm_scores = None
            if self.dm:
                dm_scores = self.get_acting_score(
                    dm_obs
                )  # self.scoring_agent.score_one_candidate(dm_obs)

            self_act = rl_says

            # check reward
            reward, done, info = self.goal_achieved(
                env_utt, self_act, possible_acts, dm_scores, switch
            )

            rl_obs = []
            dm_obs = []
            # print(len(self.env_agents[0].history.get_history_str().split()), len(self.rl_encoders[0].history.get_history_str().split()))
            for idx in range(self.no_envs):
                if done[idx]:
                    if self.envs[idx].quest.real_act_score == 1:
                        print(
                            "Act Completed:",
                            self.rl_encoders[idx].history.get_history_str(),
                        )
                        self.EnvGen.priorities_act[self.envs[idx].qindex] += 5
                    if self.envs[idx].quest.real_speech_score == 1:
                        print(
                            "Speech Completed:",
                            self.rl_encoders[idx].history.get_history_str(),
                        )
                        self.EnvGen.priorities_speech[self.envs[idx].qindex] += 5
                    if (
                        self.envs[idx].quest.real_act_score == 1
                        and self.envs[idx].quest.real_speech_score == 1
                    ):
                        print(
                            "Speech AND Act Completed:",
                            self.rl_encoders[idx].history.get_history_str(),
                        )
                        self.EnvGen.priorities[self.envs[idx].qindex] += 5
                        # print(self.rl_encoders[idx].history.get_history_str())
                    # make all agents observe episode_done
                    self.env_agents[idx].observe({"episode_done": True})
                    self.env_agents[idx].reset()
                    if self.dm:
                        self.scoring_agents[idx].observe({"episode_done": True})
                        self.scoring_agents[idx].reset()
                    # self.set_act_cands(idx)
                    if env_utt[idx]["text"] in self.env_act_cands:
                        tag = "_ACT"
                    else:
                        tag = "_SAY"
                    e_done = {
                        "text": env_utt[idx]["text"]
                        + "\n"
                        + SELF_ACT
                        + " "
                        + self_act[idx],  # ['text'],
                        "p1_token": eval("PARTNER" + tag),
                        "episode_done": True,
                    }
                    full_history_rl = self.rl_encoders[idx].observe(copy(e_done))
                    self.rl_encoders[idx].reset()

                    if write_episode:
                        info[idx]["text_to_write"] = self.parse_full_history(
                            full_history_rl["full_text"],
                            self.episode_acts[idx],
                            self.episode_possible_acts[idx],
                            self.envs[idx].internal_id,
                        )
                        self.episode_acts[idx] = []
                        self.episode_possible_acts[idx] = []

                    self.envs[idx].set_attrs(self.get_env())

                    # self.rl_encoders[idx].history.set_goal(self.envs[idx].goal)
                    self.envs[idx].quest.reset()
                    curr_self_inst = {
                        # 'text': self.envs[idx].self_setting,
                        "text": "",
                        "ignore_person_tokens": True,
                        "episode_done": False,
                    }
                    self.rl_encoders[idx].history.set_context(
                        self.envs[idx].self_setting
                    )
                    rl_obs.append(self.rl_encoders[idx].observe(copy(curr_self_inst)))

                    curr_env_inst = {
                        "text": self.envs[idx].partner_setting,
                        "ignore_person_tokens": True,
                        "episode_done": False,
                    }
                    self.env_agents[idx].observe(copy(curr_env_inst))
                    if self.dm:
                        dm_obs.append(
                            self.scoring_agents[idx].observe(copy(curr_env_inst))
                        )
                else:
                    if env_utt[idx]["text"] in self.env_act_cands:
                        tag = "_ACT"
                    else:
                        tag = "_SAY"
                    rl_encoder_input = {
                        "text": env_utt[idx]["text"],
                        "p1_token": eval("PARTNER" + tag),
                        "episode_done": False,
                    }
                    env_speech_input = {
                        "text": env_utt[idx]["text"],
                        "p1_token": eval("SELF" + tag),
                        "tag_token": MISSING_SAY_TAG,
                        "episode_done": False,
                    }

                    self.env_agents[idx].observe(copy(env_speech_input))

                    rl_obs.append(self.rl_encoders[idx].observe(copy(rl_encoder_input)))
                    if self.dm:
                        dm_input = {
                            "text": "",
                            "p1_token": PARTNER_SAY,
                            "episode_done": False,
                        }
                        dm_obs.append(self.scoring_agents[idx].observe(copy(dm_input)))
        if end:
            return None, reward, done, info, end

        # encoded = []
        '''if self.opt['flow_encoder']:
            output = [None] * self.no_envs
            """for idx in range(self.no_envs):
                rl_obs[idx]['labels'] = ['test']
            output = self.rl_encoder.batch_act(rl_obs)"""
            encoded = []
            for idx in range(self.no_envs):
                tar = torch.zeros(768)
                src = rl_obs[idx]['text_vec']
                tar[:rl_obs[idx]['text_vec'].size(0)] = src
                encoded.append(tar.unsqueeze(0))

            encoded = torch.cat(encoded, dim=0)
        else:'''
        if self.dm:
            self.set_fixed_cand_scores(dm_obs)
        for idx in range(self.no_envs):
            rl_obs[idx]["label_indices"] = self.get_cand_indices(idx, switch[idx])
        output = self.rl_encoder.batch_act(rl_obs)
        encoded = torch.cat(
            [output[i]["embedding_ctx"].unsqueeze(0) for i in range(self.no_envs)],
            dim=0,
        )
        if self.opt["flow_encoder"] == "true":
            for idx in range(self.no_envs):
                rl_obs[idx]["labels"] = ""
        for i in range(self.no_envs):
            # if self.opt.get('normalize_rl_input', True):
            #    norm = torch.norm(output[i]['embedding_ctx'])
            #    encoded_ctx = torch.div(output[i]['embedding_ctx'], norm)
            # else:
            #    encoded_ctx = output[i]['embedding_ctx']
            # encoded_candhs = [
            #    t.unsqueeze(0).type(torch.FloatTensor).cuda()
            #    for t in output[i]['cand_hs']
            # ]
            # encoded_ctx = encoded_ctx.unsqueeze(0).type(torch.FloatTensor).cuda()
            # all_ctxs = [encoded_ctx]# + encoded_candhs
            # encoded[i] = torch.cat(all_ctxs)
            """
            self.envs[i].rl_say_mappings = list(
                zip(output[i]['cands'], output[i]['cand_hs'])
            )
            #"""
            self.envs[i].rl_say_mappings = self.set_candidates(output[i])

        # valid_masks = self.generate_valid_masks()
        switch = self.generate_switch()
        return encoded, rl_obs, valid_masks, switch, reward, done, info, end

    def generate_switch(self):
        switch = []
        for idx in range(self.no_envs):
            if (self.envs[idx].steps + 1) % self.switch_steps == 0:
                switch.append(0)
            else:
                switch.append(1)
        return switch  # torch.LongTensor(switch).cuda().detach()

    def generate_valid_masks(self):
        masks_all_act = []
        masks_all_speech = []
        for idx in range(self.no_envs):
            mask_act = [0] * len(self.envs[idx].rl_say_mappings[0])
            cutoff = min(self.opt["act_value"], len(self.envs[idx].quest.possible_acts))
            acts = (
                self.envs[idx].quest.possible_acts[:cutoff]
                + self.envs[idx].goal["action_seq"]
            )
            # acts = self.envs[idx].goal['action_seq']
            # print(acts)
            # for act in self.envs[idx].goal['action_seq']:
            #    assert act in acts
            for act in acts:
                try:
                    mask_idx = self.all_act_cands.index(act)
                    # print(mask_idx)
                    mask_act[mask_idx] = 1
                except ValueError:
                    # print(act)
                    pass

            masks_all_act.append(mask_act)

            mask_speech = [0] * len(self.envs[idx].rl_say_mappings[1])
            cutoff = min(self.opt["act_value"], len(self.envs[idx].quest.possible_says))
            speechs = (
                self.envs[idx].quest.possible_says[:cutoff]
                + self.envs[idx].goal["speech_seq"]
            )
            # acts = self.envs[idx].goal['action_seq']
            # print(acts)
            # for act in self.envs[idx].goal['action_seq']:
            #    assert act in self.all_act_cands
            for speech in speechs:
                try:
                    mask_idx = self.all_speech_cands.index(speech)
                    # print(mask_idx)
                    mask_speech[mask_idx] = 1
                except ValueError:
                    # print(act)
                    pass
            masks_all_speech.append(mask_speech)
        return (torch.FloatTensor(masks_all_act), torch.FloatTensor(masks_all_speech))

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

    ## Not using this but keeping for posterity (for speech goals)
    def f1_without_stopwords(self, sent1, sent2):
        tklist1 = self.tokenizer.tokenize(sent1).words()
        tklist2 = self.tokenizer.tokenize(sent2).words()
        tklist1 = [tk.lower() for tk in tklist1]
        tklist2 = [tk.lower() for tk in tklist2]
        if self.opt.get("no_stopwords", False):
            tklist1 = [tk for tk in tklist1 if tk not in STOP_WORDS]
            tklist2 = [tk for tk in tklist2 if tk not in STOP_WORDS]
        return F1Metric._prec_recall_f1_score(tklist1, tklist2)
