#!/usr/bin/env python3


# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import numpy as np
import torch
import torch.nn as nn
import torch.functional as F
from light.modeling.agents.quests.rl.switch.models.distributions import Categorical
from light.modeling.agents.quests.rl.shared.utils import init

from parlai.agents.transformer.modules import (
    TransformerEncoderLayer,
    TransformerEncoder,
    get_n_positions_from_options,
)


class TopKPolicy(nn.Module):
    def __init__(
        self,
        obs_shape,
        action_space,
        base=None,
        base_kwargs=None,
        flow_encoder=False,
        hidden_size=512,
        rl_encoder=None,
    ):
        super(TopKPolicy, self).__init__()
        if base_kwargs is None:
            base_kwargs = {}
        # base = TransformerBase
        # base = NNBase
        init_ = lambda m: init(
            m, nn.init.orthogonal_, lambda x: nn.init.constant_(x, 0), np.sqrt(2)
        )
        if flow_encoder:
            base = MLPBase
            self.rl_encoder = rl_encoder
            # base_kwargs['hidden_size'] = 384
            base_kwargs["flow_encoder"] = True
            base_kwargs["poly_n_codes"] = obs_shape[0]
        else:
            base = MLPBase
        base_kwargs["hidden_size"] = hidden_size
        # base_kwargs['input_size'] = 768

        self.base = base(obs_shape[1], **base_kwargs)

        self.actor_act = nn.Sequential(
            init_(nn.Linear(hidden_size, 2 * hidden_size)),
            nn.Tanh(),
            init_(nn.Linear(2 * hidden_size, 2 * hidden_size)),
            nn.Tanh(),
            init_(nn.Linear(2 * hidden_size, action_space[0])),  # nn.Tanh()
        )

        self.actor_speech = nn.Sequential(
            init_(nn.Linear(hidden_size, 2 * hidden_size)),
            nn.Tanh(),
            init_(nn.Linear(2 * hidden_size, 2 * hidden_size)),
            nn.Tanh(),
            init_(nn.Linear(2 * hidden_size, action_space[1])),  # nn.Tanh()
        )

        self.dist_act = Categorical(action_space[0], action_space[0], use_linear=False)
        self.dist_speech = Categorical(
            action_space[1], action_space[1], use_linear=False
        )

        self.critic = nn.Sequential(
            # init_(nn.Linear(hidden_size * 2, hidden_size)), nn.Tanh(),
            init_(nn.Linear(hidden_size, hidden_size)),
            nn.Tanh(),
            init_(nn.Linear(hidden_size, hidden_size)),
            nn.Tanh(),
            init_(nn.Linear(hidden_size, 1)),
        )

        self.count = 0

    @property
    def is_recurrent(self):
        return self.base.is_recurrent

    @property
    def recurrent_hidden_state_size(self):
        """Size of rnn_hx."""
        return self.base.recurrent_hidden_state_size

    # def forward(self, inputs, rnn_hxs, masks):
    #    raise NotImplementedError

    def forward(self, inputs, rnn_hxs, masks, switch, deterministic=False):
        actor_features, rnn_hxs = self.base(inputs, rnn_hxs, masks)

        actor_act_features = self.actor_act(actor_features)
        actor_speech_features = self.actor_speech(actor_features)

        # value = self.critic(torch.cat([actor_act_features, actor_speech_features], dim=-1))
        # actor_act_features = actor_features.clone()
        # actor_speech_features = actor_features.clone()
        value = self.critic(actor_features)

        dist_act = self.dist_act(actor_act_features)
        dist_speech = self.dist_speech(actor_speech_features)

        if deterministic:
            act = dist_act.mode().unsqueeze(-1)
            speech = dist_speech.mode().unsqueeze(-1)
            actions_all = torch.cat([act, speech], dim=-1)
        else:
            act = dist_act.sample().unsqueeze(-1)
            speech = dist_speech.sample().unsqueeze(-1)
            actions_all = torch.cat([act, speech], dim=-1)

        act_log_probs = dist_act.log_probs(act.squeeze(-1)).unsqueeze(-1)
        speech_log_probs = dist_speech.log_probs(speech.squeeze(-1)).unsqueeze(-1)

        all_log_probs = torch.cat([act_log_probs, speech_log_probs], dim=-1)

        # action = torch.LongTensor([[actions_all[switch[i]][i]] for i in range(switch.size(0))]).cuda() #actions_all.gather(0, switch).squeeze(0)
        # action_log_probs = all_log_probs.gather(0, switch).squeeze(0)
        # dist_entropy = dist.entropy().mean()
        # action_log_probs = torch.FloatTensor([[all_log_probs[switch[i]][i]] for i in range(switch.size(0))]).cuda()

        # return value, action, action_log_probs, rnn_hxs, (dist_act.probs, dist_speech.probs)

        return (
            value,
            actions_all.squeeze(1),
            all_log_probs.squeeze(1),
            rnn_hxs,
            (dist_act.probs, dist_speech.probs),
        )

    def get_value(self, inputs, rnn_hxs, masks):
        actor_features, rnn_hxs = self.base(inputs, rnn_hxs, masks)

        # actor_act_features = self.actor_act(actor_features.clone())
        # actor_speech_features = self.actor_speech(actor_features.clone())

        # value = self.critic(torch.cat([actor_act_features, actor_speech_features], dim=-1))
        # actor_act_features = actor_features.clone()
        # actor_speech_features = actor_features.clone()
        value = self.critic(actor_features)
        return value

    def evaluate_actions(self, inputs, rnn_hxs, masks, action, switch, obs_shape):
        # Can't change input/output without changing main as well
        """
        outputs = []
        for i in range(len(inputs)):
            output = self.rl_encoder.batch_act(inputs[i])
            outputs.append(torch.cat([output[i]['embedding_ctx'].unsqueeze(0) for i in range(len(inputs[i]))], dim=0).unsqueeze(0))

        inputs = torch.cat(outputs, dim=0).view(-1, *obs_shape).float()
        #"""
        # """
        inputs = [tobs for step_tobs in inputs for tobs in step_tobs]
        outputs = self.rl_encoder.batch_act(inputs)
        inputs = torch.cat(
            [outputs[i]["embedding_ctx"].unsqueeze(0) for i in range(len(inputs))],
            dim=0,
        ).float()
        # """

        actor_features, rnn_hxs = self.base(inputs, rnn_hxs, masks)

        actor_act_features = self.actor_act(actor_features.clone())
        actor_speech_features = self.actor_speech(actor_features.clone())

        # value = self.critic(torch.cat([actor_act_features, actor_speech_features], dim=-1))
        # actor_act_features = actor_features.clone()
        # actor_speech_features = actor_features.clone()
        value = self.critic(actor_features)

        dist_act = self.dist_act(actor_act_features)
        dist_speech = self.dist_speech(actor_speech_features)
        # dist_entropy = dist_act.entropy().mean()# + dist_speech.entropy().mean()

        act_action = action[:, 0]
        speech_action = action[:, 1]

        act_log_probs = dist_act.log_probs(act_action)
        speech_log_probs = dist_speech.log_probs(speech_action)
        return (
            value,
            act_log_probs,
            speech_log_probs,
            dist_act.entropy(),
            dist_speech.entropy(),
            rnn_hxs,
            dist_act.probs,
            dist_speech.probs,
        )

        """act_log_probs = dist_act.logits.unsqueeze(0)
        speech_log_probs = dist_speech.logits.unsqueeze(0)

        pad_size = max(act_log_probs.size(-1), speech_log_probs.size(-1))
        act_pad = nn.ConstantPad1d((0, pad_size - act_log_probs.size(-1)), 0)
        speech_pad = nn.ConstantPad1d((0, pad_size - speech_log_probs.size(-1)), 0)

        act_log_probs = act_pad(act_log_probs)
        speech_log_probs = speech_pad(speech_log_probs)

        all_log_probs = torch.cat([act_log_probs, speech_log_probs], dim=0)

        switch = switch.unsqueeze(-1).unsqueeze(0).repeat(1, 1, pad_size).clone()
        switch_gathered_log_probs = all_log_probs.gather(0, switch)

        action_log_probs = switch_gathered_log_probs.gather(2, action.unsqueeze(0))"""

        # assert action_log_probs == action_log_probs[action_log_probs.nonzero()]

        # gather_indices = torch.cat([switch.unsqueeze(-1).unsqueeze(0), action.unsqueeze(0)], dim=0)

        # return value, action_log_probs, dist_entropy, rnn_hxs, dist_act.probs, dist_speech.probs


class NNBase(nn.Module):
    def __init__(self, recurrent, recurrent_input_size, hidden_size):
        super(NNBase, self).__init__()

        self._hidden_size = hidden_size
        self._recurrent = recurrent

        if recurrent:
            self.gru = nn.GRU(recurrent_input_size, hidden_size)
            for name, param in self.gru.named_parameters():
                if "bias" in name:
                    nn.init.constant_(param, 0)
                elif "weight" in name:
                    nn.init.orthogonal_(param)

    @property
    def is_recurrent(self):
        return self._recurrent

    @property
    def recurrent_hidden_state_size(self):
        if self._recurrent:
            return self._hidden_size
        return 1

    @property
    def output_size(self):
        return self._hidden_size

    def _forward_gru(self, x, hxs, masks):
        if x.size(0) == hxs.size(0):
            x, hxs = self.gru(x.unsqueeze(0), (hxs * masks).unsqueeze(0))
            x = x.squeeze(0)
            hxs = hxs.squeeze(0)
        else:
            # x is a (T, N, -1) tensor that has been flatten to (T * N, -1)
            N = hxs.size(0)
            T = int(x.size(0) / N)

            # unflatten
            x = x.view(T, N, x.size(1))

            # Same deal with masks
            masks = masks.view(T, N)

            # Let's figure out which steps in the sequence have a zero for any agent
            # We will always assume t=0 has a zero in it as that makes the logic cleaner
            has_zeros = (masks[1:] == 0.0).any(dim=-1).nonzero().squeeze().cpu()

            # +1 to correct the masks[1:]
            if has_zeros.dim() == 0:
                # Deal with scalar
                has_zeros = [has_zeros.item() + 1]
            else:
                has_zeros = (has_zeros + 1).numpy().tolist()

            # add t=0 and t=T to the list
            has_zeros = [0] + has_zeros + [T]

            hxs = hxs.unsqueeze(0)
            outputs = []
            for i in range(len(has_zeros) - 1):
                # We can now process steps that don't have any zeros in masks together!
                # This is much faster
                start_idx = has_zeros[i]
                end_idx = has_zeros[i + 1]

                rnn_scores, hxs = self.gru(
                    x[start_idx:end_idx], hxs * masks[start_idx].view(1, -1, 1)
                )

                outputs.append(rnn_scores)

            # assert len(outputs) == T
            # x is a (T, N, -1) tensor
            x = torch.cat(outputs, dim=0)
            # flatten
            x = x.view(T * N, -1)
            hxs = hxs.squeeze(0)

        return x, hxs


class TransformerBase(NNBase):
    def __init__(
        self,
        embedding_size,
        recurrent=False,
        hidden_size=768,
        num_layers=4,
        dropout=0.2,
        relu_dropout=0.0,
        attention_dropout=0.2,
        variant="xlm",
        activation="gelu",
        n_heads=1,
        action_size=100,
        flow_encoder=False,
        poly_n_codes=1,
        opt=None,
        dict=None,
    ):
        super(TransformerBase, self).__init__(
            recurrent, embedding_size * poly_n_codes, hidden_size
        )
        self.padding_idx = 0
        self.flow_enc = flow_encoder
        self._hidden_size = embedding_size  # * poly_n_codes
        if recurrent:
            num_inputs = hidden_size

        init_ = lambda m: init(
            m, nn.init.orthogonal_, lambda x: nn.init.constant_(x, 0), np.sqrt(2)
        )
        self.n_layers = num_layers
        ffn_size = embedding_size * 4

        if self.flow_enc:
            self.enc_layers = nn.ModuleList()
            for _ in range(self.n_layers):
                self.enc_layers.append(
                    TransformerEncoderLayer(
                        n_heads,
                        embedding_size,
                        ffn_size,
                        attention_dropout=attention_dropout,
                        relu_dropout=relu_dropout,
                        dropout=dropout,
                        variant=variant,
                        activation=activation,
                    )
                )

        #'''
        self.layers = nn.ModuleList()
        for _ in range(self.n_layers):
            self.layers.append(
                TransformerEncoderLayer(
                    n_heads,
                    embedding_size,
                    ffn_size,
                    attention_dropout=attention_dropout,
                    relu_dropout=relu_dropout,
                    dropout=dropout,
                    variant=variant,
                    activation=activation,
                    # learn_positional_embeddings=True
                )
            )
        self.value_linear = init_(nn.Linear(embedding_size, 1))
        self.actor_hidden = nn.Sequential(
            init_(nn.Linear(embedding_size, hidden_size)),
            nn.Tanh(),
            init_(nn.Linear(hidden_size, embedding_size)),
            nn.Tanh(),
        )
        self.train()

    # def forward(self, inputs):
    def forward(self, inputs, rnn_hxs, masks):
        bsz = inputs.size(0)
        tensor = inputs

        # tensor, masks = self.encoder(tensor.squeeze(1).long())
        #'''
        if self.flow_enc:
            masks_enc = torch.ones([inputs.size(0), inputs.size(1)]).cuda()
            # tensor = tensor.unsqueeze(1)

            for i in range(self.n_layers):
                tensor = self.layers[i](
                    tensor, masks_enc
                )  # nn.Tanh()(self.layers[i](tensor, masks_enc))
        #'''

        # tensor = tensor[:, 0, :].squeeze(1)
        # tensor = nn.Tanh()(tensor)
        # tensor = self.enc_aggr(tensor)
        if self.is_recurrent:
            tensor, rnn_hxs = self._forward_gru(tensor.view(bsz, -1), rnn_hxs, masks)

        # context_tensor = tensor.view(bsz, -1)

        # masks = torch.ones([inputs.size(0), inputs.size(1)]).cuda()
        # masks_pol = torch.ones([inputs.size(0), 1]).cuda()
        # tensor = tensor.unsqueeze(1)

        # for i in range(self.n_layers):
        #    tensor = self.layers[i](tensor, masks_pol)

        # context_tensor = tensor[:, 0, :].squeeze(1)
        context_tensor = tensor
        # cand_tensors = tensor[:, 1:, :]
        # actor_features = torch.bmm(
        #    cand_tensors, context_tensor.unsqueeze(1).transpose(2, 1)
        # ).squeeze(2)
        actor_features = self.actor_hidden(context_tensor)

        return actor_features, rnn_hxs


class MLPBase(NNBase):
    def __init__(
        self,
        num_inputs,
        recurrent=False,
        hidden_size=512,
        action_size=100,
        flow_encoder=False,
        poly_n_codes=None,
        opt=None,
        dict=None,
    ):
        super(MLPBase, self).__init__(recurrent, num_inputs, num_inputs)

        if recurrent:
            num_inputs = num_inputs

        self.flow_encoder = flow_encoder

        init_ = lambda m: init(
            m, nn.init.orthogonal_, lambda x: nn.init.constant_(x, 0), np.sqrt(2)
        )

        # if self.flow_encoder:
        self.encoder = nn.Sequential(
            init_(nn.Linear(num_inputs * poly_n_codes, hidden_size)),
            nn.Tanh(),
            init_(nn.Linear(hidden_size, num_inputs)),
            nn.Tanh(),
        )

        self.hidden_actor = nn.Sequential(
            init_(nn.Linear(num_inputs, hidden_size)),
            nn.Tanh(),
            init_(nn.Linear(hidden_size, hidden_size)),
            nn.Tanh(),
        )

        """
        self.actor = nn.Sequential(
            init_(nn.Linear(num_inputs, hidden_size)), nn.Tanh(),
            init_(nn.Linear(hidden_size, hidden_size)), nn.Tanh())
        self.critic = nn.Sequential(
            init_(nn.Linear(num_inputs, hidden_size)), nn.Tanh(),
            init_(nn.Linear(hidden_size, hidden_size)), nn.Tanh())

        self.critic_linear = init_(nn.Linear(hidden_size, 1))"""

        self.train()

    def forward(self, inputs, rnn_hxs, masks):
        batch_size = inputs.size(0)
        x = inputs

        # if self.flow_encoder:
        x = x.view(batch_size, -1)
        x = self.encoder(x)

        if self.is_recurrent:
            x, rnn_hxs = self._forward_gru(x, rnn_hxs, masks)

        # hidden_critic = self.critic(x)
        hidden_actor = self.hidden_actor(x)

        return hidden_actor, rnn_hxs
