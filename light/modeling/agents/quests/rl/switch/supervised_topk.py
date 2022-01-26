import os
import time
from collections import deque
import sys

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from tensorboardX import SummaryWriter

import light.modeling.agents.quests.rl.shared.utils
from light.modeling.agents.quests.rl.switch.arguments import get_args
from light.modeling.agents.quests.rl.switch.environments.topk import (
    TopKEnvironmentWrapper,
)
from models.topkmodel import TopKPolicy  # where is this?

torch.autograd.set_detect_anomaly(True)


def topk_supervised(args):
    total_episodes = 0

    print(args)
    writer = SummaryWriter(os.path.join(args["save_dir"], args["algo"]))

    torch.manual_seed(args["seed"])
    torch.cuda.manual_seed_all(args["seed"])

    if args["cuda"] and torch.cuda.is_available() and args["cuda_deterministic"]:
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True

    log_dir = os.path.expanduser(args["log_dir"])
    utils.cleanup_log_dir(log_dir)
    torch.set_num_threads(1)
    device = torch.device("cuda:0" if args["cuda"] else "cpu")

    # if you want train from some checkpoint
    if args["train_from"] != "":
        total_episodes = args["num_processes"] * int(
            args["train_from"].split("/")[-1].split(".")[0].split("_")[-1]
        )
        checkpoint = torch.load(args["train_from"])
        envs = TopKEnvironmentWrapper(checkpoint["opts"])
        actor_critic = TopKPolicy(
            envs.observation_shape,
            envs.action_shape,
            checkpoint["opts"],
            base_kwargs={"recurrent": checkpoint["opts"]["recurrent_policy"]},
        )

        actor_critic.to(device)

        actor_critic.load_state_dict(checkpoint["actor_critic"])
    else:
        envs = TopKEnvironmentWrapper(args)
        actor_critic = TopKPolicy(
            envs.observation_shape,
            envs.action_shape,
            args,
            base_kwargs={"recurrent": args["recurrent_policy"]},
        )
        actor_critic.to(device)

    loss_fn = nn.CrossEntropyLoss(reduction="sum")
    optimizer = optim.RMSprop(
        actor_critic.parameters(), args["lr"], eps=args["eps"], alpha=args["alpha"]
    )
    # rollouts = RolloutStorage(args['num_steps'], args['num_processes'],
    #                           envs.observation_shape, envs.action_shape,
    #                           actor_critic.recurrent_hidden_state_size)
    # changed from obs
    obs, label_inds = envs.reset_for_supervised()

    episode_rewards = deque(maxlen=args["num_processes"])

    start = time.time()
    num_updates = (
        int(args["num_env_steps"]) // args["num_steps"] // args["num_processes"]
    )
    for j in range(num_updates):

        if args["use_linear_lr_decay"]:
            utils.update_linear_schedule(optimizer, j, num_updates, optimizer.lr)

        step = 0
        print(label_inds)
        print(obs.size())

        (
            value,
            action,
            action_log_prob,
            recurrent_hidden_states,
            action_weights,
        ) = actor_critic.act(obs.float(), None, None)
        print(action)
        reward = []
        for (act, label) in zip(action, label_inds):
            if int(act) == int(label):
                reward.append(1)
                episode_rewards.append(1)
            else:
                reward.append(0)
                episode_rewards.append(0)

        total_episodes += len(reward)
        label_inds = torch.LongTensor(label_inds).cuda()
        loss = loss_fn(action_weights, label_inds)

        loss.backward()
        # import pdb;pdb.set_trace()
        param_grads = [
            x.grad.data for x in actor_critic.parameters() if x.grad is not None
        ]
        to_hist = []
        for idx, param in enumerate(param_grads):
            if idx in [0, int(len(param_grads) / 2), len(param_grads)]:
                to_hist.append(param.cpu().numpy())
        writer.add_histogram("param_grads", np.array(to_hist), j)

        optimizer.step()

        writer.add_histogram("act_weights", action_weights[0].detach().cpu().numpy(), j)

        optimizer.zero_grad()
        obs, label_inds = envs.reset_for_supervised()

        # save for every interval-th episode or for the last epoch
        if (j % args["save_interval"] == 0 or j == num_updates - 1) and args[
            "save_dir"
        ] != "":
            save_path = os.path.join(args["save_dir"], args["algo"])
            print("Saving at j: " + str(j))
            try:
                os.makedirs(save_path)
            except OSError:
                pass

            checkpoint = {
                "actor_critic": actor_critic.state_dict(),
                "optimizer": optimizer.state_dict(),
                "opts": args,
            }
            # import ipdb; ipdb.set_trace()
            torch.save(
                checkpoint,
                os.path.join(save_path, args["env_name"] + "_" + str(j) + ".pt"),
            )

        if j % args["log_interval"] == 0 and len(episode_rewards) > 1:
            total_num_steps = (j + 1) * args["num_processes"] * args["num_steps"]
            end = time.time()
            print(
                "Updates {}, num timesteps {}, FPS {} \n Last {} "
                "training episodes: mean/median reward {:.1f}/{:.1f},"
                " min/max reward {:.1f}/{:.1f}; "
                "loss: {:.3f} \n".format(
                    j,
                    total_num_steps,
                    int(total_num_steps / (end - start)),
                    len(episode_rewards),
                    # total_episodes,
                    np.mean(episode_rewards),
                    np.median(episode_rewards),
                    np.min(episode_rewards),
                    np.max(episode_rewards),
                    loss,
                )
            )
            writer.add_scalars(
                "train_data",
                {
                    "reward": np.mean(episode_rewards),
                    "episodes": total_episodes,
                    "loss": loss,
                    "value": value.mean().item(),
                },
                total_episodes,
            )
            sys.stdout.flush()

    writer.close()


def main():
    args = get_args()
    topk_supervised(args)


if __name__ == "__main__":
    main()
