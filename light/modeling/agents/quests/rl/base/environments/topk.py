import torch
from copy import deepcopy, copy
import pickle
import sys
import random
from collections import deque
import numpy as np
import json

import torch.nn.functional as F
from parlai.core.metrics import F1Metric
from parlai.agents.tfidf_retriever.tokenizers.simple_tokenizer import SimpleTokenizer
from parlai.core.agents import create_agent, create_agent_from_shared
from light.modeling.agents.quests.rl.base.environments.environment import Environment
from light.modeling.agents.quests.rl.base.environments.env_generator import (
    EnvironmentGenerator,
)
from light.modeling.agents.quests.rl.shared.process.constants import *


class TopKEnvironmentWrapper(object):
    def __init__(self, opt):
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

        RLAgent_opt = {
            "model_file": opt["rl_model_file"],
            "override": {
                "model": "from light.modeling.agents.quests.rl.base.agents.rl_agent:TopKRLAgent",
                "person_tokens": True,
                "eval_candidates": "fixed",
                "encode_candidate_vecs": True,
                "fixed_candidates_path": opt["act_fixed_candidate_file"],
                "fp16": True,
                "rank_top_k": 1,  # opt['k_value'],
                "path": opt["path"],
                "datatype": datatype,
                "text_truncate": 768,
            },
        }

        EnvAgent_opt = {
            "model_file": opt["env_model_file"],
            "override": {
                "model": "from light.modeling.agents.quests.rl.base.agents.env_agents"
                ":LightRetrievalAgent",
                "person_tokens": True,
                "eval_candidates": "fixed",
                "encode_candidate_vecs": True,
                "fixed_candidates_path": opt["speech_fixed_candidate_file"],
                "fp16": True,
                "path": opt["path"],
                "text_truncate": 768,
            },
        }

        self.rl_encoder = create_agent(RLAgent_opt)
        if not opt["flow_encoder"]:
            with torch.no_grad():
                self.rl_encoder.model.eval()
        else:
            self.rl_encoder.model.train()
            self.rl_encoder.is_training = True
        rl_share = self.rl_encoder.share()

        self.env_agent = create_agent(EnvAgent_opt)
        with torch.no_grad():
            self.env_agent.model.eval()
        env_share = self.env_agent.share()

        self.rl_encoders, self.env_agents = [], []
        self.envs = []
        for idx in range(self.no_envs):
            rl_share["batchindex"] = idx
            self.rl_encoders.append(create_agent_from_shared(rl_share))
            env_share["batchindex"] = idx
            self.env_agents.append(create_agent_from_shared(env_share))

            self.envs.append(Environment(opt))

        # if opt['flow_encoder']:
        #    self.observation_shape = [384]#[opt['k_value'] + 1, 768]
        # else:
        self.observation_shape = [768]  # [opt['k_value'] + 1, 768]

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

    def load_act_cands(self, opt):
        with open(opt["act_fixed_candidate_file"], "r") as f:
            self.all_act_cands = [a.strip() for a in f.readlines()]
            random.shuffle(self.all_act_cands)

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

    def goal_achieved(self, env_utt, env_action, possible_acts):
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
                act_goal_reward, done[idx] = self.envs[idx].quest.act(env_action[idx])

            reward_max = max([act_goal_reward, utt_goal_reward])
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
            if done[idx]:
                speech_rewards.append(utt_goal_reward)
            info_dict["episode"]["r"] = reward[idx].item()
            # print(reward[idx].item())
            # print('------')
            info_dict["episode"]["score"] = self.envs[idx].quest.score
            info_dict["episode"]["real_score"] = self.envs[idx].quest.real_score
            info_dict["episode"]["done"] = done[idx].item()
            info_dict["episode"]["steps"] = self.envs[idx].steps
            if bad_transition:
                info_dict["bad_transition"] = True
            info.append(info_dict)

        # self.mean_episode_rewards.append(np.mean(speech_rewards))

        return reward, done, info

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
        if end:
            return None, True

        # encoded = []

        for i in range(self.no_envs):
            print(self.envs[i].goal)
        print(self.all_act_cands)
        if self.opt["flow_encoder"]:
            output = [None] * self.no_envs
            """for idx in range(self.no_envs):
                rl_obs[idx]['labels'] = ['test']
            output = self.rl_encoder.batch_act(rl_obs)"""
            encoded = []
            for idx in range(self.no_envs):
                tar = torch.zeros(768)
                src = obs[idx]["text_vec"]
                tar[: obs[idx]["text_vec"].size(0)] = src
                encoded.append(tar.unsqueeze(0))

            encoded = torch.cat(encoded, dim=0)
        else:
            output = deepcopy(self.rl_encoder.batch_act(obs))
            encoded = torch.cat(
                [output[i]["embedding_ctx"].unsqueeze(0) for i in range(self.no_envs)],
                dim=0,
            )

        # for_type = output[0]['embedding_ctx']
        # num_cands = len(output[0]['cand_hs'])
        # encoded = for_type.new(self.no_envs, num_cands + 1, for_type.size(0))

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
        return encoded, end

    def set_candidates(self, output):
        # curr_deter_cands = []
        # for c in self.all_act_cands:
        #    loc = output['cands'].index(c)
        #    curr_deter_cands.append((output['cands'][loc], output['cand_hs'][loc]))
        # assert [c[0] for c in curr_deter_cands] == self.all_act_cands
        return [(a, [0]) for a in self.all_act_cands]  # curr_deter_cands

    def step(self, action, write_episode=False):
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
        rl_acts = [act.item() for act in action]
        with torch.no_grad():
            rl_says = []
            for idx in range(self.no_envs):
                self.episode_acts[idx].append(rl_acts[idx])
                # TODO HERE CHANGE THIS TO ACTION MAPPINGS
                # THEN JUST CALCULATE REWARD BASED ON THAT
                # THEN HAVE THE ENV OBSERVE THAT ACTION/EXECUTE IT IN THE EGINE AND USE IT AS ENCODING FOR NEXT STEP
                cand_chosen, _ = self.envs[idx].rl_say_mappings[rl_acts[idx]]
                rl_says.append(cand_chosen)

            # get possible actions from the environment
            # if 'emote' in self.goal_types:
            #    possible_acts = [copy(ALL_EMOTES) for _ in range(self.no_envs)]
            # else:
            possible_acts = [
                self.envs[idx].possible_acts for idx in range(self.no_envs)
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
                    self.episode_possible_acts[idx].append(self.envs[idx].possible_acts)
                self.envs[idx].steps += 1
                rl_encoder_input = {
                    "text": rl_says[idx],
                    "p1_token": SELF_ACT,
                    "episode_done": False,
                }
                env_speech_input = {
                    "text": rl_says[idx],
                    "p1_token": PARTNER_ACT,
                    "tag_token": MISSING_SAY_TAG,
                    "episode_done": False,
                }
                self.rl_encoders[idx].observe(copy(rl_encoder_input))
                env_utt_obs.append(self.env_agents[idx].observe(copy(env_speech_input)))

            # environment utterance
            env_utt = deepcopy(self.env_agent.batch_act(env_utt_obs))

            """for idx in range(self.no_envs):
                if write_episode:
                    self.episode_possible_acts[idx].append(self.envs[idx].possible_acts)
                #self.envs[idx].steps += 1
                rl_encoder_input = {
                    'text': env_utt[idx]['text'],
                    'p1_token': PARTNER_SAY,
                    'episode_done': False,
                }
                self.rl_encoders[idx].observe(copy(rl_encoder_input))
                env_speech_input = {
                    'text': env_utt[idx]['text'],
                    'p1_token': SELF_SAY,
                    'tag_token': MISSING_SAY_TAG,
                    'episode_done': False,
                }
                self.env_agents[idx].observe(copy(env_speech_input))"""
            # env_utt_obs.append(self.env_agents[idx].observe(copy(env_speech_input)))
            # utt_blank = {'id': 'LightRetrieval', 'episode_done': False, 'text': '', 'text_candidates': []}
            # env_utt = [deepcopy(utt_blank)] * len(self.envs)

            # environment, RL agent observe env utt
            env_act_obs = []
            # for idx in range(self.no_envs):
            #    all_cands += possible_acts[idx]

            # all_cands = [self.envs[0].goal.get('action', NULL_TAG['action']), random.choice(self.envs[0].possible_acts)]

            """for idx in range(self.no_envs):
                act_input = {
                    'text': env_utt[idx]['text'],
                    'p1_token': SELF_ACT,
                    'tag_token': MISSING_TAG,
                    'episode_done': False,
                }
                if self.envs[idx].possible_acts != []:
                    act_input['label_candidates'] = self.cand_actions[idx]
                    #act_input['label_candidates'] = self.envs[idx].possible_acts
                    #act_input['label_candidates'] = all_cands
                else:
                    act_input['label_candidates'] = ['hit person', 'hug person']
                env_act_obs.append(self.env_agents[idx].observe(copy(act_input)))"""

            # environment act
            # env_act = deepcopy(self.env_agent.batch_act(env_act_obs))
            # env_act = deepcopy(env_utt)
            # env agent observes own act, execute env agent act in game engine
            self_act = rl_says
            """for idx in range(self.no_envs):
                if self.envs[idx].possible_acts != []:
                    self.env_agents[idx].observe(
                        {
                            'text': self_act[idx],
                            'p1_token': PARTNER_ACT,
                            'episode_done': False,
                        }
                    )
                    if 'action' in self.goal_types:
                        try:
                            _ = self.envs[idx].graph.parse_exec(
                                self.envs[idx].partner_id, self_act[idx]
                            )
                        except:
                            print('Action cannot be executed ...')
                            print(self_act[idx])"""

            # check reward
            reward, done, info = self.goal_achieved(env_utt, self_act, possible_acts)

            rl_obs = []
            # print(len(self.env_agents[0].history.get_history_str().split()), len(self.rl_encoders[0].history.get_history_str().split()))
            for idx in range(self.no_envs):
                if done[idx]:
                    # make all agents observe episode_done
                    self.env_agents[idx].observe({"episode_done": True})
                    self.env_agents[idx].reset()
                    # self.set_act_cands(idx)
                    e_done = {
                        "text": env_utt[idx]["text"]
                        + "\n"
                        + SELF_ACT
                        + " "
                        + self_act[idx],  # ['text'],
                        "p1_token": PARTNER_SAY,
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

                    try:
                        self.envs[idx].set_attrs(self.get_env())
                    except TypeError:
                        end = True
                        continue
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
                else:
                    rl_encoder_input = {
                        "text": env_utt[idx]["text"],
                        "p1_token": PARTNER_SAY,
                        "episode_done": False,
                    }
                    env_speech_input = {
                        "text": env_utt[idx]["text"],
                        "p1_token": SELF_SAY,
                        "tag_token": MISSING_SAY_TAG,
                        "episode_done": False,
                    }
                    self.env_agents[idx].observe(copy(env_speech_input))

                    rl_obs.append(self.rl_encoders[idx].observe(copy(rl_encoder_input)))
        if end:
            return None, reward, done, info, end

        # encoded = []
        if self.opt["flow_encoder"]:
            output = [None] * self.no_envs
            """for idx in range(self.no_envs):
                rl_obs[idx]['labels'] = ['test']
            output = self.rl_encoder.batch_act(rl_obs)"""
            encoded = []
            for idx in range(self.no_envs):
                tar = torch.zeros(768)
                src = rl_obs[idx]["text_vec"]
                tar[: rl_obs[idx]["text_vec"].size(0)] = src
                encoded.append(tar.unsqueeze(0))

            encoded = torch.cat(encoded, dim=0)
        else:
            output = deepcopy(self.rl_encoder.batch_act(rl_obs))
            encoded = torch.cat(
                [output[i]["embedding_ctx"].unsqueeze(0) for i in range(self.no_envs)],
                dim=0,
            )

        # for_type = output[0]['embedding_ctx']
        # num_cands = len(output[0]['cand_hs'])
        # encoded = for_type.new(self.no_envs, num_cands + 1, for_type.size(0))

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
        return encoded, valid_masks, reward, done, info, end

    def generate_valid_masks(self):
        masks_all = []
        for idx in range(self.no_envs):
            mask = [0] * len(self.envs[idx].rl_say_mappings)
            cutoff = min(self.opt["act_value"], len(self.envs[idx].possible_acts))
            acts = (
                self.envs[idx].possible_acts[:cutoff]
                + self.envs[idx].goal["action_seq"]
            )
            # acts = self.envs[idx].goal['action_seq']
            # print(acts)
            for act in self.envs[idx].goal["action_seq"]:
                assert act in self.all_act_cands
            for act in acts:
                try:
                    mask_idx = self.all_act_cands.index(act)
                    # print(mask_idx)
                    mask[mask_idx] = 1
                except ValueError:
                    print(act)
                    pass
            masks_all.append(mask)
        return torch.FloatTensor(masks_all)

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
        self.list_instances = self.EnvGen.from_original_dialogs_shuffled_all(
            shuffled=False
        )

        while len(self.list_instances) > 0:
            with torch.no_grad():
                instance = self.list_instances.pop(0)
                instance["output_label"] = []
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

                i = 0
                idx = 0
                # Get embeddings
                self.envs[0].set_attrs(instance)
                """self.rl_encoders[idx].history.set_goal(self.envs[idx].goal)
                curr_self_inst = {
                    'text': self.envs[idx].self_setting,
                    'ignore_person_tokens': True,
                    'prev_obs': False,
                    'episode_done': False,
                }"""
                curr_self_inst = {
                    # 'text': self.envs[idx].self_setting,
                    "text": "",
                    "ignore_person_tokens": True,
                    "episode_done": False,
                }
                self.rl_encoders[idx].history.set_context(self.envs[idx].self_setting)
                new_obs = self.rl_encoders[idx].observe(copy(curr_self_inst))
                output = deepcopy(self.rl_encoder.batch_act([copy(new_obs)]))
                for_type = output[0]["embedding_ctx"]
                encoded = for_type.new(for_type.size(0))
                if self.opt.get("normalize_rl_input", True):
                    norm = torch.norm(output[i]["embedding_ctx"])
                    encoded_ctx = torch.div(output[i]["embedding_ctx"], norm)
                else:
                    encoded_ctx = output[i]["embedding_ctx"]
                encoded_candhs = [
                    t.unsqueeze(0).type(torch.FloatTensor).cuda()
                    for t in output[i]["cand_hs"]
                ]
                encoded_ctx = encoded_ctx.unsqueeze(0).type(torch.FloatTensor).cuda()
                all_ctxs = [encoded_ctx] + encoded_candhs
                encoded = torch.cat(all_ctxs)
                self.envs[i].rl_say_mappings = list(
                    zip(output[i]["cands"], output[i]["cand_hs"])
                )

                instance["embeddings"] = encoded.tolist()

                for cluster in range(opt["k_value"]):
                    cand_chosen, _ = self.envs[idx].rl_say_mappings[cluster]

                    if "emote" in self.goal_types:
                        possible_acts = copy(ALL_EMOTES)
                    else:
                        possible_acts = [
                            self.envs[0].graph.get_possible_actions(
                                self.envs[0].partner_id, use_actions=USE_ACTIONS
                            )
                        ]

                    curr_env_inst = {
                        "text": self.envs[0].partner_setting,
                        "ignore_person_tokens": True,
                        "episode_done": False,
                    }

                    self.env_agents[0].observe(copy(curr_env_inst))

                    env_utt_obs, env_act_obs = [], []

                    self.envs[0].steps += 1
                    env_agent_input = {
                        "text": cand_chosen,
                        "p1_token": PARTNER_SAY,
                        "tag_token": MISSING_SAY_TAG,
                        "episode_done": False,
                    }
                    env_next_utt_obs = self.env_agents[0].observe(copy(env_agent_input))
                    env_utt_obs.append(env_next_utt_obs)
                    env_utt = deepcopy(self.env_agent.batch_act(env_utt_obs))
                    act_input = {
                        "text": env_utt[0]["text"],
                        "p1_token": SELF_ACT,
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

                    if possible_acts[0] != []:
                        self.env_agents[0].observe(
                            {
                                "text": env_act[0]["text"],
                                "p1_token": SELF_ACT,
                                "episode_done": False,
                            }
                        )
                    if "action" in self.goal_types:
                        try:
                            _ = self.envs[0].graph.parse_exec(
                                self.envs[0].partner_id, env_act[0]["text"]
                            )
                        except:
                            print("Action cannot be executed ...")
                            print(env_act[0]["text"])

                    # make all agents observe episode_done
                    self.env_agents[0].observe({"episode_done": True})

                    if self.envs[0].goal.get("action") == env_act[0]["text"]:
                        all_achievable += 1
                        instance["output_label"].append(cluster)

                self.rl_encoders[0].observe({"episode_done": True})

                if instance["output_label"] != []:
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

    def reset_for_supervised(self):
        obs = []
        with torch.no_grad():
            # All agents observe settings
            for idx in range(self.no_envs):
                self.rl_encoders[idx].observe({"episode_done": True})
                self.env_agents[idx].observe({"episode_done": True})

                self.envs[idx].set_attrs(self.get_env())

                """self.rl_encoders[idx].history.set_goal(self.envs[idx].goal)

                curr_self_inst = {
                    'text': self.envs[idx].self_setting,
                    'ignore_person_tokens': True,
                    'prev_obs': False,
                    'episode_done': False,
                }"""
                curr_self_inst = {
                    # 'text': self.envs[idx].self_setting,
                    "text": "",
                    "ignore_person_tokens": True,
                    "episode_done": False,
                }
                self.rl_encoders[idx].history.set_context(self.envs[idx].self_setting)
                new_obs = self.rl_encoders[idx].observe(copy(curr_self_inst))
                obs.append(copy(new_obs))

                curr_env_inst = {
                    "text": self.envs[idx].partner_setting,
                    "ignore_person_tokens": True,
                    "episode_done": False,
                }
                self.env_agents[idx].observe(copy(curr_env_inst))

        output = deepcopy(self.rl_encoder.batch_act(obs))
        for_type = output[0]["embedding_ctx"]
        num_cands = len(output[0]["cand_hs"])
        encoded = for_type.new(self.no_envs, num_cands + 1, for_type.size(0))
        labels = []
        for i in range(self.no_envs):
            labels.append(self.envs[i].output_label)
            if self.opt.get("normalize_rl_input", True):
                norm = torch.norm(output[i]["embedding_ctx"])
                encoded_ctx = torch.div(output[i]["embedding_ctx"], norm)
            else:
                encoded_ctx = output[i]["embedding_ctx"]
            encoded_candhs = [
                t.unsqueeze(0).type(torch.FloatTensor).cuda()
                for t in output[i]["cand_hs"]
            ]
            encoded_ctx = encoded_ctx.unsqueeze(0).type(torch.FloatTensor).cuda()
            all_ctxs = [encoded_ctx] + encoded_candhs
            encoded[i] = torch.cat(all_ctxs)
            self.envs[i].rl_say_mappings = list(
                zip(output[i]["cands"], output[i]["cand_hs"])
            )
        return encoded, labels

    def generate_examples_step(self, action):
        """
        This probably doesn't work for topk yet, need modification
        TODO
        """
        MISSING_TAG = (
            MISSING_EMOTE_TAG if "emote" in self.goal_types else MISSING_ACT_TAG
        )

        # get utterances that RL Agent selected
        rl_acts = [act.item() for act in action]
        rl_ret_obs = []
        # combine the chosen cluster with the context
        with torch.no_grad():
            cands_chosen = []
            for idx in range(self.no_envs):
                self.episode_acts[idx].append(rl_acts[idx])
                cand_chosen, _ = self.envs[idx].rl_say_mappings[rl_acts[idx]]
                cands_chosen.append(cand_chosen)
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
                self.episode_possible_acts[idx].append(possible_acts[idx])
                self.envs[idx].steps += 1
                env_speech_input = {
                    "text": cands_chosen[idx],
                    "p1_token": PARTNER_SAY,
                    "tag_token": MISSING_SAY_TAG,
                    "episode_done": False,
                }
                rl_encoder_input = {
                    "text": cands_chosen[idx],
                    "p1_token": SELF_ACT,
                    "episode_done": False,
                }
                self.rl_encoders[idx].observe(copy(rl_encoder_input))
                env_utt_obs.append(self.env_agents[idx].observe(copy(env_speech_input)))

            env_utt = deepcopy(self.env_agent.batch_act(env_utt_obs))

            for idx in range(self.no_envs):
                act_input = {
                    "text": env_utt[idx]["text"],
                    "p1_token": SELF_ACT,
                    "tag_token": MISSING_ACT_TAG,
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
                    if "action" in self.goal_types:
                        try:
                            _ = self.envs[idx].graph.parse_exec(
                                self.envs[idx].partner_id, env_act[idx]["text"]
                            )
                        except:
                            print("Action cannot be executed ...")
                            print(env_act[idx]["text"])

            reward, done, info = self.goal_achieved(env_utt, env_act, possible_acts)
            rl_obs = []

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
                    full_history_rl = self.rl_encoders[idx].observe(copy(e_done))

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
                    """self.rl_encoders[idx].history.set_goal(self.envs[idx].goal)

                    curr_self_inst = {
                        'text': self.envs[idx].self_setting,
                        'ignore_person_tokens': True,
                        'prev_obs': True,
                        'episode_done': False,
                    }"""
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
                else:
                    encode_model_input = {
                        "text": env_utt[idx]["text"]
                        + "\n"
                        + PARTNER_ACT
                        + " "
                        + env_act[idx]["text"],
                        "p1_token": PARTNER_SAY,
                        "prev_obs": False,
                        "episode_done": False,
                    }
                    rl_obs.append(
                        self.rl_encoders[idx].observe(copy(encode_model_input))
                    )
            output = deepcopy(self.rl_encoder.batch_act(rl_obs))
            for_type = output[0]["embedding_ctx"]
            num_cands = len(output[0]["cand_hs"])
            encoded = for_type.new(self.no_envs, num_cands + 1, for_type.size(0))
            for i in range(self.no_envs):
                if self.opt.get("normalize_rl_input", True):
                    norm = torch.norm(output[i]["embedding_ctx"])
                    encoded_ctx = torch.div(output[i]["embedding_ctx"], norm)
                else:
                    encoded_ctx = output[i]["embedding_ctx"]
                encoded_candhs = [
                    t.unsqueeze(0).type(torch.FloatTensor).cuda()
                    for t in output[i]["cand_hs"]
                ]
                encoded_ctx = encoded_ctx.unsqueeze(0).type(torch.FloatTensor).cuda()
                all_ctxs = [encoded_ctx] + encoded_candhs
                encoded[i] = torch.cat(all_ctxs)
                self.envs[i].rl_say_mappings = list(
                    zip(output[i]["cands"], output[i]["cand_hs"])
                )
            return encoded, reward, done, info

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
