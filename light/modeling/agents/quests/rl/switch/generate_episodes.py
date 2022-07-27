import numpy as np
import torch

from light.modeling.agents.quests.rl.switch.algo.a2c_acktr import A2C_ACKTR
from light.modeling.agents.quests.rl.switch.arguments import get_args
from light.modeling.agents.quests.rl.switch.environments.envs import EnvironmentWrapper
from light.modeling.agents.quests.rl.switch.models.model import Policy
from light.modeling.agents.quests.rl.switch.environments.topk import (
    TopKEnvironmentWrapper,
)
from light.modeling.agents.quests.rl.switch.models.topkmodel import (
    TopKPolicy,
    TopKBiencoderPolicy,
)


class GenerateEpisodes(object):
    def __init__(self, num_processes, device, max_eps=1000):

        self.no_envs = num_processes
        self.device = device

        self.total_episodes = 0
        self.episode_rewards = []
        self.max_eps = max_eps
        self.infos = []

    def ge_cluster(self, args, write_examples_file, write_eps=True):
        write_file = args.get("write_test_episodes_file")
        if args.get("eval_model", None) is not None:
            checkpoint = torch.load(args["eval_model"])
            self.envs = EnvironmentWrapper(args)
            self.actor_critic = Policy(
                # MLP w/ GRU, obs -> act
                self.envs.observation_shape,
                self.envs.action_shape,
                checkpoint["opts"],
                base_kwargs={"recurrent": checkpoint["opts"]["recurrent_policy"]},
            )
            self.actor_critic.to(self.device)

            agent = A2C_ACKTR(
                self.actor_critic,
                checkpoint["opts"]["value_loss_coef"],
                checkpoint["opts"]["entropy_coef"],
                lr=checkpoint["opts"]["lr"],
                eps=checkpoint["opts"]["eps"],
                alpha=checkpoint["opts"]["alpha"],
                max_grad_norm=checkpoint["opts"]["max_grad_norm"],
                acktr=checkpoint["opts"]["use_kfac_optim"],
                adam=checkpoint["opts"].get("use_adam", False),
                optim_state=checkpoint["optimizer"],
            )
            self.actor_critic.load_state_dict(checkpoint["actor_critic"])
            self.actor_critic.to(self.device)
            self.actor_critic.load_state_dict(checkpoint["actor_critic"])

        else:
            self.envs = EnvironmentWrapper(args)
            self.actor_critic = Policy(
                envs.observation_shape,
                envs.action_shape,
                args,
                base_kwargs={"recurrent": args["recurrent_policy"]},
            )
            self.actor_critic.to(self.device)
            _ = A2C_ACKTR(
                actor_critic, args["value_loss_coef"], args["entropy_coef"], acktr=True
            )
        obs = self.envs.reset()
        eval_recurrent_hidden_states = torch.zeros(
            self.no_envs,
            self.actor_critic.recurrent_hidden_state_size,
            device=self.device,
        )
        eval_masks = torch.zeros(self.no_envs, 1, device=self.device)
        total_eps = 0
        for _ in range(self.max_eps * args["num_steps"]):
            float_obs = obs.float()
            with torch.no_grad():
                (
                    _,
                    action,
                    _,
                    eval_recurrent_hidden_states,
                    actor_features,
                ) = self.actor_critic.act(
                    float_obs,
                    eval_recurrent_hidden_states,
                    eval_masks,
                    deterministic=True,
                )
            try:
                obs, _, done, infos = self.envs.step(action, write_episode=True)
            except TypeError:
                break
            eval_masks = torch.tensor(
                [[0.0] if done_ else [1.0] for done_ in done],
                dtype=torch.float32,
                device=self.device,
            )

            for info, done_ in zip(infos, done):
                if done_:
                    self.episode_rewards.append(info["episode"]["r"])
                    self.total_episodes += 1
                    self.infos.append(info)
                    text_to_write = info["text_to_write"]
                    if write_eps:
                        with open(write_file, "a") as wf:
                            wf.write(text_to_write + "\n")
                    if self.total_episodes >= self.max_eps:
                        break

            if self.total_episodes >= self.max_eps:
                break

            if self.total_episodes == 0:
                continue

        print(
            "Total #Episode: "
            + str(self.total_episodes)
            + " ;"
            + "Mean/Median Reward: "
            + str(self.mean_episodes())
            + "/"
            + str(self.median_episodes())
            + "; percent success: "
            + str(self.percent_success())
            + "; avg turns: "
            + str(self.avg_turns())
            + ";\n"
        )
        write_examples_file.write(
            "Total #Episode: "
            + str(self.total_episodes)
            + " ;"
            + "Mean/Median Reward: "
            + str(self.mean_episodes())
            + "/"
            + str(self.median_episodes())
            + "; percent success: "
            + str(self.percent_success())
            + "; avg turns: "
            + str(self.avg_turns())
            + ";\n"
        )

    def ge_topk(self, args, write_examples_file, write_eps=True):
        write_file = args.get("write_test_episodes_file")
        self.envs = TopKEnvironmentWrapper(args)
        if args["eval_model"]:
            checkpoint = torch.load(args["eval_model"])
            self.actor_critic = TopKPolicy(
                self.envs.observation_shape,
                self.envs.action_shape,
                checkpoint["opts"],
                base_kwargs={"recurrent": checkpoint["opts"]["recurrent_policy"]},
            )
            self.actor_critic.to(self.device)
            agent = A2C_ACKTR(
                self.actor_critic,
                checkpoint["opts"]["value_loss_coef"],
                checkpoint["opts"]["entropy_coef"],
                lr=checkpoint["opts"]["lr"],
                eps=checkpoint["opts"]["eps"],
                alpha=checkpoint["opts"]["alpha"],
                max_grad_norm=checkpoint["opts"]["max_grad_norm"],
                acktr=checkpoint["opts"]["use_kfac_optim"],
                adam=checkpoint["opts"].get("use_adam", False),
                optim_state=checkpoint["optimizer"],
            )
            self.actor_critic.load_state_dict(checkpoint["actor_critic"])
        else:
            self.actor_critic = TopKPolicy(
                envs.observation_shape,
                envs.action_shape,
                args,
                base_kwargs={"recurrent": args["recurrent_policy"]},
            )
            self.actor_critic.to(self.device)
            agent = A2C_ACKTR(
                self.actor_critic,
                args["value_loss_coef"],
                args["entropy_coef"],
                lr=args["lr"],
                eps=args["eps"],
                alpha=args["alpha"],
                max_grad_norm=args["max_grad_norm"],
                adam=args["use_adam"],
                acktr=args["use_kfac_optim"],
            )
        obs = self.envs.reset()
        eval_recurrent_hidden_states = torch.zeros(
            self.no_envs,
            self.actor_critic.recurrent_hidden_state_size,
            device=self.device,
        )
        eval_masks = torch.zeros(self.no_envs, 1, device=self.device)
        total_eps = 0
        for _ in range(self.max_eps * args["num_steps"]):
            float_obs = obs.float()
            with torch.no_grad():
                _, action, _, eval_recurrent_hidden_states, _ = self.actor_critic.act(
                    float_obs,
                    eval_recurrent_hidden_states,
                    eval_masks,
                    deterministic=True,
                )
            try:
                obs, _, done, infos = self.envs.step(action, write_episode=True)
            except TypeError:
                break

            eval_masks = torch.tensor(
                [[0.0] if done_ else [1.0] for done_ in done],
                dtype=torch.float32,
                device=self.device,
            )

            for info, done_ in zip(infos, done):
                if done_:
                    self.episode_rewards.append(info["episode"]["r"])
                    self.total_episodes += 1
                    self.infos.append(info)
                    text_to_write = info["text_to_write"]
                    if write_eps:
                        with open(write_file, "a") as wf:
                            wf.write(text_to_write + "\n")
                    if self.total_episodes >= self.max_eps:
                        break

            if self.total_episodes >= self.max_eps:
                break

            if self.total_episodes == 0:
                continue

        print(
            "Total #Episode: "
            + str(self.total_episodes)
            + " ;"
            + "Mean/Median Reward: "
            + str(self.mean_episodes())
            + "/"
            + str(self.median_episodes())
            + "; percent success: "
            + str(self.percent_success())
            + "; avg turns: "
            + str(self.avg_turns())
            + ";\n"
        )
        write_examples_file.write(
            "Total #Episode: "
            + str(self.total_episodes)
            + " ;"
            + "Mean/Median Reward: "
            + str(self.mean_episodes())
            + "/"
            + str(self.median_episodes())
            + "; percent success: "
            + str(self.percent_success())
            + "; avg turns: "
            + str(self.avg_turns())
            + ";\n"
        )

    def ge_topkbiencoder(self, args, write_examples_file, write_eps=True):
        write_file = args.get("write_test_episodes_file")
        self.envs = TopKEnvironmentWrapper(args)
        if args["eval_model"]:
            checkpoint = torch.load(args["eval_model"])
            self.actor_critic = TopKBiencoderPolicy(
                self.envs.observation_shape,
                self.envs.action_shape,
                checkpoint["opts"],
                base_kwargs={"recurrent": checkpoint["opts"]["recurrent_policy"]},
            )
            self.actor_critic.to(self.device)
            agent = A2C_ACKTR(
                self.actor_critic,
                checkpoint["opts"]["value_loss_coef"],
                checkpoint["opts"]["entropy_coef"],
                lr=checkpoint["opts"]["lr"],
                eps=checkpoint["opts"]["eps"],
                alpha=checkpoint["opts"]["alpha"],
                max_grad_norm=checkpoint["opts"]["max_grad_norm"],
                acktr=checkpoint["opts"]["use_kfac_optim"],
                adam=checkpoint["opts"].get("use_adam", False),
                optim_state=checkpoint["optimizer"],
            )
            self.actor_critic.load_state_dict(checkpoint["actor_critic"])
        else:
            self.actor_critic = TopKBiencoderPolicy(
                envs.observation_shape,
                envs.action_shape,
                args,
                base_kwargs={"recurrent": args["recurrent_policy"]},
            )
            self.actor_critic.to(self.device)
            agent = A2C_ACKTR(
                self.actor_critic,
                args["value_loss_coef"],
                args["entropy_coef"],
                lr=args["lr"],
                eps=args["eps"],
                alpha=args["alpha"],
                max_grad_norm=args["max_grad_norm"],
                adam=args["use_adam"],
                acktr=args["use_kfac_optim"],
            )
        obs = self.envs.reset()
        eval_recurrent_hidden_states = torch.zeros(
            self.no_envs,
            self.actor_critic.recurrent_hidden_state_size,
            device=self.device,
        )
        eval_masks = torch.zeros(self.no_envs, 1, device=self.device)
        total_eps = 0
        for _ in range(self.max_eps * args["num_steps"]):
            float_obs = obs.float()
            with torch.no_grad():
                _, action, _, eval_recurrent_hidden_states, _ = self.actor_critic.act(
                    float_obs,
                    eval_recurrent_hidden_states,
                    eval_masks,
                    deterministic=True,
                )
            try:
                obs, _, done, infos = self.envs.step(action, write_episode=True)
            except TypeError:
                break

            eval_masks = torch.tensor(
                [[0.0] if done_ else [1.0] for done_ in done],
                dtype=torch.float32,
                device=self.device,
            )

            for info, done_ in zip(infos, done):
                if done_:
                    self.episode_rewards.append(info["episode"]["r"])
                    self.total_episodes += 1
                    self.infos.append(info)
                    text_to_write = info["text_to_write"]
                    if write_eps:
                        with open(write_file, "a") as wf:
                            wf.write(text_to_write + "\n")
                    if self.total_episodes >= self.max_eps:
                        break

            if self.total_episodes >= self.max_eps:
                break

            if self.total_episodes == 0:
                continue

        print(
            "Total #Episode: "
            + str(self.total_episodes)
            + " ;"
            + "Mean/Median Reward: "
            + str(self.mean_episodes())
            + "/"
            + str(self.median_episodes())
            + "; percent success: "
            + str(self.percent_success())
            + "; avg turns: "
            + str(self.avg_turns())
            + ";\n"
        )
        write_examples_file.write(
            "Total #Episode: "
            + str(self.total_episodes)
            + " ;"
            + "Mean/Median Reward: "
            + str(self.mean_episodes())
            + "/"
            + str(self.median_episodes())
            + "; percent success: "
            + str(self.percent_success())
            + "; avg turns: "
            + str(self.avg_turns())
            + ";\n"
        )

    def ge_inverse(self, args, write_examples_file):
        self.envs = EnvironmentWrapper(args)
        obs = self.envs.reset()
        for _ in range(self.max_eps * args["num_steps"]):
            action = []
            try:
                obs, _, done, infos = self.envs.step(action)
            except TypeError:
                break

            for info, done_ in zip(infos, done):
                if done_:
                    self.episode_rewards.append(info["episode"]["r"])
                    self.total_episodes += 1
                    self.infos.append(info)

            if self.total_episodes >= self.max_eps:
                return

            if self.total_episodes == 0:
                continue

            write_examples_file.write(
                "Total #Episode: "
                + str(self.total_episodes)
                + " ;"
                + "Mean/Median Reward: "
                + str(self.mean_episodes())
                + "/"
                + str(self.median_episodes())
                + "; percent success: "
                + str(self.percent_success())
                + "; avg turns: "
                + str(self.avg_turns())
                + ";\n"
            )
            print(
                "Total #Episode: "
                + str(self.total_episodes)
                + " ;"
                + "Mean/Median Reward: "
                + str(self.mean_episodes())
                + "/"
                + str(self.median_episodes())
                + "; percent success: "
                + str(self.percent_success())
                + "; avg turns: "
                + str(self.avg_turns())
                + ";\n"
            )


def main():
    args = get_args()
    torch.manual_seed(args["seed"])
    torch.cuda.manual_seed_all(args["seed"])
    np.random.seed(args["seed"])
    if args["cuda"] and torch.cuda.is_available() and args["cuda_deterministic"]:
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True

    torch.set_num_threads(1)
    device = torch.device("cuda:0" if args["cuda"] else "cpu")
    max_eps = args["max_eval_eps"]
    write_examples_file = open(args["write_examples_file"], "w")
    ge = GenerateEpisodes(args["num_processes"], device, max_eps=max_eps)
    if args["model_type"] == "inverse":
        ge.ge_inverse(args, write_examples_file, write_eps=True)
    elif args["model_type"] == "topk":
        ge.ge_topk(args, write_examples_file, write_eps=True)
    elif args["model_type"] == "topkbiencoder":
        ge.ge_topkbiencoder(args, write_examples_file, write_eps=True)
    elif args["model_type"] == "cluster":
        ge.ge_cluster(args, write_examples_file, write_eps=True)


if __name__ == "__main__":
    main()
