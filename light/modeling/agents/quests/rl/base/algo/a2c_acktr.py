#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from light.modeling.agents.quests.rl.shared.algo.kfac import KFACOptimizer


class A2C_ACKTR:
    def __init__(
        self,
        actor_critic,
        value_loss_coef,
        entropy_coef,
        valid_loss_coef,
        actor_loss_coef,
        lr=None,
        eps=None,
        alpha=None,
        max_grad_norm=None,
        acktr=False,
        adam=False,
        optim_state=None,
    ):

        self.actor_critic = actor_critic
        self.acktr = acktr

        self.value_loss_coef = value_loss_coef
        self.entropy_coef = entropy_coef
        self.actor_loss_coef = actor_loss_coef
        self.valid_loss_coef = valid_loss_coef
        self.max_grad_norm = max_grad_norm

        self.valid_loss_fn = nn.BCELoss()

        if acktr:
            self.optimizer = KFACOptimizer(actor_critic, optim_state=optim_state)
        elif adam:
            self.optimizer = optim.Adam(
                actor_critic.parameters(), lr=lr, betas=(0.8, 0.999), eps=1e-8
            )
            if optim_state:
                self.optimizer.load_state_dict(optim_state)
        else:
            self.optimizer = optim.RMSprop(
                actor_critic.parameters(), lr, eps=eps, alpha=alpha
            )

    def update(self, rollouts):
        obs_shape = rollouts.obs.size()[2:]
        action_shape = rollouts.actions.size()[-1]
        num_steps, num_processes, _ = rollouts.rewards.size()

        (
            values,
            action_log_probs,
            dist_entropy,
            _,
            action_probs,
        ) = self.actor_critic.evaluate_actions(
            rollouts.obs[:-1].view(-1, *obs_shape),
            rollouts.recurrent_hidden_states[0].view(
                -1, self.actor_critic.recurrent_hidden_state_size
            ),
            rollouts.masks[:-1].view(-1, 1),
            rollouts.actions.view(-1, action_shape),
        )

        values = values.view(num_steps, num_processes, 1)
        action_log_probs = action_log_probs.view(num_steps, num_processes, 1)

        # action_probs = F.softmax(rollouts.action_probs, dim=2).permute(1, 0, 2)
        action_probs = action_probs.view(num_steps, num_processes, -1).permute(1, 0, 2)
        valid = rollouts.valid.permute(1, 0, 2)

        valid_loss = self.valid_loss_fn(action_probs, valid)

        advantages = rollouts.returns[:-1] - values
        value_loss = advantages.pow(2).mean()

        action_loss = -(advantages.detach() * action_log_probs).mean()

        if self.acktr and self.optimizer.steps % self.optimizer.Ts == 0:
            # Sampled fisher, see Martens 2014
            self.actor_critic.zero_grad()
            pg_fisher_loss = -action_log_probs.mean()

            value_noise = torch.randn(values.size())
            if values.is_cuda:
                value_noise = value_noise.cuda()

            sample_values = values + value_noise
            vf_fisher_loss = -(values - sample_values.detach()).pow(2).mean()

            fisher_loss = pg_fisher_loss + vf_fisher_loss
            self.optimizer.acc_stats = True
            fisher_loss.backward(retain_graph=True)
            self.optimizer.acc_stats = False

        self.optimizer.zero_grad()
        full_loss = (
            value_loss * self.value_loss_coef
            + action_loss * self.actor_loss_coef
            + valid_loss * self.valid_loss_coef
            - dist_entropy * self.entropy_coef
        )
        # from torchviz import make_dot
        # make_dot(full_loss).render("attached_flow", format='pdf')
        # exit()

        full_loss.backward()

        if self.acktr == False:
            nn.utils.clip_grad_norm_(self.actor_critic.parameters(), self.max_grad_norm)

        self.optimizer.step()

        return (
            value_loss.item(),
            action_loss.item(),
            valid_loss.item(),
            dist_entropy.item(),
            values,
            advantages,
        )
