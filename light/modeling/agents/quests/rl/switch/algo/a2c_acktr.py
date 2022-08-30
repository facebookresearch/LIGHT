#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from light.modeling.agents.quests.rl.shared.algo.kfac import KFACOptimizer


def invert(tensor):
    res = tensor.clone()
    res[tensor == 0] = 1
    res[tensor != 0] = 0
    return res


class A2C_ACKTR:
    def __init__(
        self,
        actor_critic,
        value_loss_coef,
        entropy_coef,
        valid_loss_coef,
        actor_loss_coef,
        scale_coef,
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
        self.scale_coef = scale_coef
        self.max_grad_norm = max_grad_norm

        self.valid_loss_fn = nn.BCELoss(reduction="none")

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

        switches = (
            torch.LongTensor(rollouts.switches).cuda().detach()[:-1, :].unsqueeze(-1)
        )
        # switches = torch.LongTensor(rollouts.switches).cuda()[:-1, :].unsqueeze(-1)

        text_obs = rollouts.text[:-1]  # .view(-1, *obs_shape)
        # text_obs = [tobs for step_tobs in rollouts.text[:-1] for tobs in step_tobs]

        (
            values,
            act_log_probs,
            speech_log_probs,
            dist_act_entropy,
            dist_speech_entropy,
            _,
            act_probs,
            speech_probs,
        ) = self.actor_critic.evaluate_actions(
            # rollouts.obs[:-1].view(-1, *obs_shape),
            text_obs,
            rollouts.recurrent_hidden_states[0].view(
                -1, self.actor_critic.recurrent_hidden_state_size
            ),
            rollouts.masks[:-1].view(-1, 1),
            rollouts.actions.view(-1, action_shape),
            switches.view(-1),
            obs_shape,
        )

        values = values.view(num_steps, num_processes, 1)

        # action_probs = F.softmax(rollouts.action_probs, dim=2).permute(1, 0, 2)

        advantages = rollouts.returns[:-1] - values
        value_loss = advantages.pow(2).mean()

        # switches = rollouts.switches[:-1, :].unsqueeze(-1)
        inv_switches = invert(switches)

        act_probs = act_probs.view(num_steps, num_processes, -1).permute(1, 0, 2)
        valid_act = rollouts.valid_act.permute(1, 0, 2)
        valid_act_loss = (
            self.valid_loss_fn(act_probs, valid_act)
            * inv_switches.repeat(1, 1, act_probs.size(-1)).permute(1, 0, 2)
        ).sum()

        speech_probs = speech_probs.view(num_steps, num_processes, -1).permute(1, 0, 2)
        valid_speech = rollouts.valid_speech.permute(1, 0, 2)
        valid_speech_loss = (
            self.valid_loss_fn(speech_probs, valid_speech)
            * switches.repeat(1, 1, speech_probs.size(-1)).permute(1, 0, 2)
        ).sum()

        valid_loss = valid_act_loss + self.scale_coef * valid_speech_loss

        dist_act_entropy = (
            dist_act_entropy.view(num_steps, num_processes, 1) * inv_switches
        ).mean()

        dist_speech_entropy = (
            dist_speech_entropy.view(num_steps, num_processes, 1) * switches
        ).mean()

        dist_entropy = dist_act_entropy + self.scale_coef * dist_speech_entropy

        act_log_probs = act_log_probs.view(num_steps, num_processes, 1)
        act_loss = -((advantages.detach() * act_log_probs) * inv_switches).mean()

        speech_log_probs = speech_log_probs.view(num_steps, num_processes, 1)
        speech_loss = -((advantages.detach() * speech_log_probs) * switches).mean()

        action_loss = act_loss + self.scale_coef * speech_loss

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
