import torch
from copy import copy
from copy import deepcopy
import os
from light.constants import LIGHT_DATAPATH

from parlai.core.agents import create_agent, create_agent_from_shared
from light.modeling.agents.quests.rl.switch.environments.environment import Environment
from light.modeling.agents.quests.rl.switch.environments.env_generator import (
    EnvironmentGenerator,
)
from light.modeling.agents.quests.rl.shared.process.constants import *
from light.modeling.agents.quests.rl.switch.arguments import get_args

from light.modeling.agents.quests.rl.switch.agents.env_agents import LightRetrievalAgent

from parlai.core.params import ParlaiParser

ParlaiParser()  # instantiate to set PARLAI_HOME environment var

PARLAI_PATH = os.environ["PARLAI_HOME"]


class InteractiveLoop:
    def __init__(self, opt):
        if not opt["rl_model_file"]:
            opt["rl_model_file"] = (
                os.path.join(
                    LIGHT_DATAPATH,
                    "quests/rl_quests_resources/base_models/untrained_small_poly/model",
                ),
            )
        if not opt["env_model_file"]:
            opt["env_model_file"] = os.path.join(
                LIGHT_DATAPATH, "quests/rl_quests_resources/env_model/model"
            )
        # opt['combo'] = 'train_ex'
        opt["combo"] = "achievable"

        self.EnvGen = EnvironmentGenerator(opt)
        self.no_envs = opt["num_processes"]
        RLAgent_opt = {
            "model_file": opt["rl_model_file"],
            "override": {
                "model": "parlai_internal.projects.light.quests.tasks.rl_switch.agents.rl_agent:RLAgent",
                "person_tokens": True,
                "eval_candidates": "fixed",
                "encode_candidate_vecs": True,
                "fixed_candidates_path": opt["speech_fixed_candidate_file"],
                "fp16": True,
                # 'data_parallel': False,
            },
        }

        RLRetrieval_opt = {
            "override": {
                "model": "parlai_internal.projects.light.quests.tasks.rl_switch.agents.env_agents"
                ":LightRetrievalAgent",
                "person_tokens": True,
                "eval_candidates": "fixed",
                "encode_candidate_vecs": True,
                "fixed_candidates_path": opt["speech_fixed_candidate_file"],
                "fp16": True,
                # 'data_parallel': False,
            }
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
                # 'data_parallel': False,
            },
        }

        self.rl_encoder = create_agent(RLAgent_opt)
        with torch.no_grad():
            self.rl_encoder.model.eval()
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
        self.action_shape = 50
        self.cur_env = None
        self.num_steps = opt["num_steps"]
        self.list_instances = []
        self.opt = opt
        self.previous_rl_obs = []
        self.i = 0

    def get_new_env(self):
        if self.list_instances == []:
            if self.opt["combo"] == "train_ex":
                while self.list_instances == []:
                    self.list_instances += self.EnvGen.from_original_dialogs()
            elif self.opt["combo"] == "achievable":
                self.list_instances = self.EnvGen.from_achievable_settings()
            elif self.opt["combo"] == "all":
                self.list_instances += self.EnvGen.environment_generator()
            elif self.opt["combo"] == "mix":
                self.i += 1
                if self.i < self.opt["supervise_steps"]:
                    while self.list_instances == []:
                        self.list_instances += self.EnvGen.from_original_dialogs()
            else:
                self.list_instances += self.EnvGen.environment_generator()

        self.cur_env = self.list_instances.pop(0)
        return

    def reset(self, refresh=True):
        obs = []
        with torch.no_grad():
            # All agents observe settings
            idx = 0
            self.envs[idx].set_attrs(self.cur_env)

            # self.rl_encoders[idx].history.set_goal(
            #     self.envs[idx].goal
            #     )
            # self.rl_retrievers[idx].history.set_goal(
            #     self.envs[idx].goal
            #     )

            curr_self_inst = {
                "text": self.envs[idx].self_setting,
                "ignore_person_tokens": True,
                "prev_obs": False,
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

            print("Context sent to RL agent:", self.envs[idx].self_setting)
        return

    def step(self):
        idx = 0

        possible_acts = [
            sorted(
                self.envs[idx].graph.get_possible_actions(
                    self.envs[idx].partner_id, use_actions=USE_ACTIONS
                )
            )
        ]
        print("POSSIBLE ACTIONS FOR ENVIRONMENT AGENT:", possible_acts[0])
        goal = self.envs[idx].goal
        hinput = input(
            "Action goal is set to '"
            + goal.get("action")
            + "' but you can enter a new one, or just enter to accept the goal: "
        )
        if hinput != "":
            goal = {"action": hinput}
        self.rl_retrievers[idx].history.set_goal(goal)

        cluster = input(
            "Enter cluster to use (between 0 and 49 inclusive) or just enter to not use clusters: "
        )

        while True:
            if cluster == "":
                break
            try:
                cluster = int(cluster)
                break
            except:
                cluster = input(
                    "That is not a valid input. Enter cluster to use (between 0 and 49 inclusive) or just enter to not use clusters: "
                )
        rl_ret_obs = []
        # combine the chosen cluster with the context
        with torch.no_grad():
            if cluster != "":
                self.rl_retrievers[idx].history.set_cluster("_cluster" + str(cluster))
            if self.previous_rl_obs[idx]["prev_obs"]:
                rl_ret_obs.append(
                    self.rl_retrievers[idx].observe(
                        copy(self.previous_rl_obs[idx]), self_observe=False
                    )
                )
            else:
                rl_ret_obs.append(
                    self.rl_retrievers[idx].observe(copy(self.previous_rl_obs[idx]))
                )
            print(rl_ret_obs)

            # get responses from RL Agent and that should be responses
            actions = self.rl_retrieval.batch_act(rl_ret_obs)

            # get possible actions from the environment

            rl_utt = actions[idx]["text"]
            print("RL AGENT SPEECH:", rl_utt)
            hinput = input(
                "Press enter to use the RL agent's speech, or enter your own utterance to override it: "
            )
            if hinput != "":
                rl_utt = hinput

            env_utt_obs, env_act_obs = [], []
            self.envs[idx].steps += 1
            env_speech_input = {
                "text": rl_utt,
                "tag_token": MISSING_SAY_TAG,
                "p1_token": PARTNER_SAY,
                "episode_done": False,
            }
            env_utt_obs.append(
                self.env_agents[idx].observe(copy(env_speech_input), self_observe=False)
            )
            print(env_utt_obs)
            env_utt = deepcopy(self.env_agent.batch_act(env_utt_obs))
            env_utt_text = env_utt[idx]["text"]
            print("ENVIRONMENT SPEECH:", env_utt[idx]["text"])
            hinput = input(
                "Press enter to use the environemnt's speech, or enter your own utterance to override it: "
            )
            if hinput != "":
                env_utt_text = hinput
            act_input = {
                "text": env_utt_text,
                "p1_token": SELF_SAY,
                "tag_token": MISSING_ACT_TAG,
                "episode_done": False,
            }
            if possible_acts[idx] != []:
                act_input["label_candidates"] = possible_acts[idx]
            else:
                act_input["label_candidates"] = ["hit person", "hug person"]
            env_act_obs.append(
                self.env_agents[idx].observe(copy(act_input), self_observe=False)
            )
            print(env_act_obs)

            env_act = deepcopy(self.env_agent.batch_act(env_act_obs))
            print("ENVIRONMENT ACTION CHOSEN:", env_act[idx]["text"])

            # Utterance agent observes what act agent said
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

            # make all agents observe episode_done
            print(self.env_agent.history.history_raw_strings)
            print(self.rl_retrieval.history.history_raw_strings)
            self.env_agents[idx].observe({"episode_done": True}, self_observe=False)
            e_done = {
                "text": env_utt_text + "\n" + PARTNER_ACT + env_act[idx]["text"],
                "p1_token": PARTNER_SAY,
                "episode_done": True,
            }
            self.rl_retrievers[idx].observe(copy(e_done))
        return

    def run_loop(self):
        self.get_new_env()
        while True:
            self.reset()
            self.step()
            hinput = input(
                "\nEnter n to get a new environment, or anything else to try the same one again: "
            )
            if hinput == "n":
                self.get_new_env()


def main(opt):
    interactive = InteractiveLoop(opt)
    interactive.run_loop()


if __name__ == "__main__":
    args = get_args()
    main(args)
