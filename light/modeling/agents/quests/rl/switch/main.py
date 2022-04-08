#!/usr/bin/env python3
import os
import time
from collections import deque
import sys

import numpy as np
import torch
from tensorboardX import SummaryWriter

import utils
from light.modeling.agents.quests.rl.switch.algo.a2c_acktr import A2C_ACKTR
from light.modeling.agents.quests.rl.shared.algo.ppo import PPO
from light.modeling.agents.quests.rl.switch.arguments import get_args
from light.modeling.agents.quests.rl.switch.environments.envs import EnvironmentWrapper
from models.model import Policy  # where is this?
from light.modeling.agents.quests.rl.switch.process.storage import RolloutStorage
from light.modeling.agents.quests.rl.switch.environments.topk import (
    TopKEnvironmentWrapper,
)
from models.topkmodel import TopKPolicy  # where is this?
from light.modeling.agents.quests.rl.switch.process import format

# DEBUG = False
import random


def train_loop(
    args, actor_critic, envs, agent, device, total_episodes=0, updates_done=0
):

    writer = SummaryWriter(
        os.path.join(
            args["save_dir"], args["model_type"], args["allfname"], args["run_num"]
        ),
        purge_step=total_episodes,
    )
    envs.EnvGen.writer = writer

    log_dir = os.path.expanduser(args["log_dir"])
    # utils.cleanup_log_dir(log_dir)
    # utils.cleanup_log_dir(os.path.join(args['save_dir'], args['model_type'], allfname, args['run_num']))
    torch.set_num_threads(1)

    # if args['flow_encoder']:
    #    hidden_size = 384
    # else:
    if "text" not in args["enc_type"]:
        hidden_size = envs.observation_shape[1]
    else:
        hidden_size = 768

    rollouts = RolloutStorage(
        args["num_steps"],
        args["num_processes"],
        envs.observation_shape,
        envs.action_shape,
        hidden_size
        # actor_critic.recurrent_hidden_state_size,
    )

    obs, text, switch, _ = envs.reset()
    print(obs.size(), rollouts.obs.size())
    rollouts.obs[0].copy_(obs)
    rollouts.text[0] = text
    # rollouts.text[0].copy_(text)

    rollouts.switches[0] = switch
    rollouts.to(device)

    episode_rewards = deque(maxlen=args["num_processes"])
    episode_act_goals = deque(maxlen=args["num_processes"])
    episode_speech_goals = deque(maxlen=args["num_processes"])

    start = time.time()
    num_updates = 0
    """(
        int(args['num_env_steps']) // args['num_steps'] // args['num_processes']
    )"""

    # if DEBUG:
    #     torch.manual_seed(args['seed'])
    #     torch.cuda.manual_seed_all(args['seed'])
    #     np.random.seed(args['seed'])
    #     actor_critic.eval()
    #     value2, action2, action_log_prob2, recurrent_hidden_states2, actor_features2 =\
    #         actor_critic.act(
    #         rollouts.obs[0],
    #         rollouts.recurrent_hidden_states[0],
    #         rollouts.masks[0]
    #         )
    #     print("DEBUG")
    #     print(value2, action2, action_log_prob2, actor_features2)
    #     return

    j = updates_done
    while True:

        for step in range(args["num_steps"]):
            # Sample actions
            # print(step)
            with torch.no_grad():
                deterministic = args["eval_mode"] == "test"
                (
                    value,
                    action,
                    action_log_prob,
                    recurrent_hidden_states,
                    actor_features,
                ) = actor_critic.forward(
                    rollouts.obs[step],
                    rollouts.recurrent_hidden_states[step],
                    rollouts.masks[step],
                    switch,
                    # deterministic
                )

            # print(action)

            obs, text, valid, switch, reward, done, infos, end = envs.step(
                action, switch
            )

            # print('reward', reward)

            for info in infos:
                if "episode" in info.keys():
                    if info["episode"]["done"]:
                        episode_rewards.append(info["episode"]["score"])
                        episode_act_goals.append(info["episode"]["real_act_score"])
                        episode_speech_goals.append(
                            info["episode"]["real_speech_score"]
                        )
                        total_episodes += 1

            # If done then clean the history of observations.
            masks = torch.FloatTensor([[0.0] if done_ else [1.0] for done_ in done])
            bad_masks = torch.FloatTensor(
                [[0.0] if "bad_transition" in info.keys() else [1.0] for info in infos]
            )
            rollouts.insert(
                obs,
                recurrent_hidden_states,
                action,
                action_log_prob,
                value,
                reward,
                masks,
                bad_masks,
                valid,
                actor_features,
                switch,
                text,
            )
        if args["eval_mode"] == "train":
            with torch.no_grad():
                next_value = actor_critic.get_value(
                    rollouts.obs[-1],
                    rollouts.recurrent_hidden_states[-1],
                    rollouts.masks[-1],
                ).detach()

            rollouts.compute_returns(
                next_value,
                args["use_gae"],
                args["gamma"],
                args["gae_lambda"],
                args["use_proper_time_limits"],
            )

            (
                value_loss,
                action_loss,
                valid_loss,
                dist_entropy,
                values,
                advantages,
            ) = agent.update(rollouts)
            rollouts.after_update()
        else:
            value_loss, action_loss, valid_loss, dist_entropy = 0, 0, 0, 0
        # values, advantages = values.mean().item(), advantages.mean().item()

        # save for every interval-th episode or for the last epoch
        if (
            (j % args["save_interval"] == 0 or j == num_updates - 1)
            and args["save_dir"] != ""
            and args["eval_mode"] == "train"
        ):

            print("Saving at j: " + str(j))
            try:
                os.makedirs(
                    os.path.join(args["model_dir"], args["allfname"], args["run_num"]),
                    exist_ok=True,
                )
            except OSError:
                pass

            checkpoint = {
                "actor_critic": actor_critic.state_dict(),
                "optimizer": agent.optimizer.state_dict(),
                "opts": args,
                "updates_done": j,
                "episodes_done": total_episodes,
            }

            # torch.save(checkpoint, os.path.join(args['model_dir'], args['allfname'], args['run_num'], 'checkpoint_' + str(j) + '.pt'))
            torch.save(
                checkpoint,
                os.path.join(
                    args["model_dir"],
                    args["allfname"],
                    args["run_num"],
                    "checkpoint_last.pt",
                ),
            )

        if (
            j % args["log_interval"] == 0
            and len(episode_rewards) >= args["num_processes"]
        ):
            total_num_steps = (
                ((j - updates_done) + 1) * args["num_processes"] * args["num_steps"]
            )
            end = time.time()
            print(
                "Updates {}, num timesteps {}, FPS {} \n Last {} "
                "training episodes: mean/median reward {:.1f}/{:.1f},"
                " min/max reward {:.1f}/{:.1f}; "
                " act/speech goals  {:.1f}/{:.1f}; "
                " entropy, value, action, valid loss: {:.3f}, {:.3f}, {:.3f}, {:.3f}\n".format(
                    j,
                    total_num_steps,
                    int(total_num_steps / (end - start)),
                    len(episode_rewards),
                    np.mean(episode_rewards),
                    np.median(episode_rewards),
                    np.min(episode_rewards),
                    np.max(episode_rewards),
                    np.mean(episode_act_goals),
                    np.mean(episode_speech_goals),
                    dist_entropy,
                    value_loss,
                    action_loss,
                    valid_loss,
                )
            )
            if args["run_num"] == "debug":
                print(
                    " || ".join(
                        [f"Q:{q},P:{p}" for q, p in envs.EnvGen.priorities.items()]
                    )
                )
            if args["eval_mode"] == "test":
                if args["eval_mode"] == "test":
                    print("Q Index", envs.EnvGen.index)
                    print(
                        "Act and Speech completions: ",
                        sum([a for a in envs.EnvGen.priorities.values()])
                        / envs.EnvGen.index,
                    )
                    print(
                        "Act completions: ",
                        sum([a for a in envs.EnvGen.priorities_act.values()])
                        / envs.EnvGen.index,
                    )
                    print(
                        "Speech completions: ",
                        sum([a for a in envs.EnvGen.priorities_speech.values()])
                        / envs.EnvGen.index,
                    )

            if args["eval_mode"] == "train":
                writer.add_scalars(
                    args["eval_mode"] + "_data",
                    {
                        "reward": np.mean(episode_rewards),
                        "act_goals": np.mean(episode_act_goals),
                        "speech_goals": np.mean(episode_speech_goals),
                        "episodes": total_episodes,
                        #'dist_entropy': dist_entropy,
                        #'value_loss': value_loss,
                        #'action_loss': action_loss,
                        #'values': values,
                        #'advantage': advantages,
                        #'abs_advantage': abs(advantages),
                    },
                    total_episodes,
                )
            sys.stdout.flush()
            # exit()
        if args["eval_mode"] == "train":
            if args["curriculum"] == "linear":
                if (j + 1) % args["curr_schedule_steps"] == 0:
                    envs.EnvGen.increase_pool(args["curr_step_size"])
            elif args["curriculum"] == "reward":
                if np.mean(episode_rewards) > args["curr_rew_threshold"]:
                    envs.EnvGen.increase_pool(args["curr_step_size"])

        if (j + 1) % args["dropint"] == 0:
            if args["droptask"] != []:
                sample = random.choices(
                    population=range(3), weights=args["droptask"], k=1
                )[0]
                # action only
                if sample == 0:
                    envs.switch_steps = 1
                    # args['switch_steps'] = 1
                # speak only
                elif sample == 1:
                    envs.switch_steps = envs.episode_steps + 1
                    # args['switch_steps'] = envs.episode_steps + 1
                # speak and act
                elif sample == 2:
                    envs.switch_steps = args["switch_steps"]
                    # args['switch_steps']

        j += 1
    writer.close()


def main():
    args = get_args()
    random.seed(args["seed"])
    checkpoint = {}
    device = torch.device("cuda" if args["cuda"] else "cpu")
    total_episodes = 0
    updates_done = 0

    path, k, switch_ratio = format.preprocess(args)
    args["k_value"] = k
    args["path"] = path
    for key in [
        "data_file",
        "speech_fixed_candidate_file",
        "act_fixed_candidate_file",
        "env_all_cands",
        "env_act_cands",
        "quest_all_cands",
    ]:
        args[key] = os.path.join(path, args[key])

    args["droptask"] = [float(a) for a in args["droptask"].split(",")]

    if args["priority"] == "true" and args["droptask"] == []:
        # args['num_steps'] = 100
        args["switch_steps"] = int(1 / switch_ratio)
        print("SWITCH STEPS", args["switch_steps"])

    if args["eval_mode"] == "test":
        args["data_file"] = os.path.join(path, "formatted_hobbot_quests_test.pkl")

    # utils.cleanup_enc_vecs([os.path.join(path, a) for a in ['env', 'rl']])

    if args["episode_steps"] is None:
        args["episode_steps"] = args["num_steps"]

    if args["train_from"] != "":
        updates_done = int(
            args["train_from"].split("/")[-1].split(".")[0].split("_")[-1]
        )
        if args.get("updates_done"):
            updates_done = int(args["updates_done"])
        total_episodes = args["num_processes"] * updates_done
        checkpoint = torch.load(args["train_from"])
    if (
        os.path.exists(
            os.path.join(
                args["model_dir"],
                args["allfname"],
                args["run_num"],
                "checkpoint_last.pt",
            )
        )
        and args["eval_mode"] == "train"
    ):  # and args['run_num'] != 'debug':
        print(
            "@@@@@@@@@@@@ Loading checkpoint from: ",
            os.path.join(
                args["model_dir"],
                args["allfname"],
                args["run_num"],
                "checkpoint_last.pt",
            ),
        )
        checkpoint = torch.load(
            os.path.join(
                args["model_dir"],
                args["allfname"],
                args["run_num"],
                "checkpoint_last.pt",
            )
        )
        total_episodes = checkpoint["episodes_done"]
        updates_done = checkpoint["updates_done"]

    if args["eval_mode"] == "test":
        print(
            "@@@@@@@@@@@@ Loading checkpoint from: ",
            os.path.join(
                args["model_dir"],
                args["allfname"],
                args["run_num"],
                "checkpoint_last.pt",
            ),
        )
        checkpoint = torch.load(
            os.path.join(
                args["model_dir"],
                args["allfname"],
                args["run_num"],
                "checkpoint_last.pt",
            )
        )
        args["num_processes"] = 1
        args["priority"] = "false"
        args["log_interval"] = 1
        args["num_steps"] = 1000
        args["switch_steps"] = 3

    model_args = args
    if len(checkpoint.items()) > 0:
        old_args = checkpoint["opts"]
        model_args["model_type"] = old_args["model_type"]

    if args["model_type"] == "topk":
        envs = TopKEnvironmentWrapper(args)
        actor_critic = TopKPolicy(
            envs.observation_shape,
            envs.action_shape,
            model_args,
            base_kwargs={"recurrent": model_args["recurrent_policy"]},
            flow_encoder=args["flow_encoder"],
            # poly_n_codes=envs.rl_encoder.opt['poly_n_codes'],
            hidden_size=args["hidden_size"],
            rl_encoder=envs.rl_encoder,
        )
        # actor_critic = torch.nn.DataParallel(actor_critic)
    elif args["model_type"] == "cluster":
        envs = EnvironmentWrapper(args)
        actor_critic = Policy(
            envs.observation_shape,
            envs.action_shape,
            model_args,
            base_kwargs={"recurrent": model_args["recurrent_policy"]},
        )
    else:
        raise Exception("please specify --model_type")
    actor_critic.to(device)
    lr = model_args["lr"]
    if args["lr"] == 0:
        lr = 0
    if args["algo"] == "a2c":
        agent = A2C_ACKTR(
            actor_critic,
            model_args["value_loss_coef"],
            model_args["entropy_coef"],
            model_args["valid_loss_coef"],
            model_args["actor_loss_coef"],
            model_args["scale_coef"],
            lr=lr,
            eps=model_args["eps"],
            alpha=model_args["alpha"],
            max_grad_norm=model_args["max_grad_norm"],
            acktr=model_args["use_kfac_optim"],
            adam=model_args.get("use_adam", False),
            optim_state=checkpoint.get("optimizer"),
        )
    elif args["algo"] == "ppo":
        agent = PPO(
            actor_critic,
            model_args["clip_param"],
            model_args["ppo_epoch"],
            model_args["num_mini_batch"],
            model_args["value_loss_coef"],
            model_args["entropy_coef"],
            lr=lr,
            eps=model_args["eps"],
            max_grad_norm=model_args["max_grad_norm"],
            use_clipped_value_loss=True,
        )

    if len(checkpoint.items()) > 0:
        actor_critic.load_state_dict(checkpoint["actor_critic"])
        actor_critic.to(device)
    if args["algo_mode"] == "train":
        train_loop(
            args,
            actor_critic,
            envs,
            agent,
            device,
            total_episodes=total_episodes,
            updates_done=updates_done,
        )
    elif args["algo_mode"] == "get_achievable":
        envs.debug_step()
    else:
        print("Wrong mode for algorithm, choose a valid option")


if __name__ == "__main__":
    main()
