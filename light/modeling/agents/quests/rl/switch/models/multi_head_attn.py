#!/usr/bin/env python3


import torch
import torch.nn as nn
import torch.nn.functional as F

import math


class MultiHeadAttention(nn.Module):
    """
    Implements MultiHeadAttention; this is the core workhorse of the Transformer.
    See Vaswani (2017) for an extensive description.
    """

    def __init__(self, n_heads, dim, dropout=0):
        super(MultiHeadAttention, self).__init__()
        self.n_heads = n_heads
        self.dim = dim

        self.attn_dropout = nn.Dropout(p=dropout)  # --attention-dropout
        self.q_lin = nn.Linear(dim, dim)
        self.k_lin = nn.Linear(dim, dim)
        self.v_lin = nn.Linear(dim, dim)
        # TODO: merge for the initialization step
        nn.init.xavier_normal_(self.q_lin.weight)
        nn.init.xavier_normal_(self.k_lin.weight)
        nn.init.xavier_normal_(self.v_lin.weight)
        # and set biases to 0
        self.out_lin = nn.Linear(dim, dim)
        nn.init.xavier_normal_(self.out_lin.weight)

        self.keys = nn.Embedding(50, dim)
        self.values = nn.Embedding(50, dim)

    def forward(self, query, mask=None):
        """Forward pass."""
        # TODO: there are a lot of parameters to document here.

        # Input is [B, dim]
        # Mask is [B, key_len] (selfattn) or [B, key_len, key_len] (enc attn)
        batch_size, dim = query.size()
        assert (
            dim == self.dim
        ), "Dimensions do not match: {} query vs {} configured".format(dim, self.dim)

        n_heads = self.n_heads
        dim_per_head = dim // n_heads
        scale = math.sqrt(dim_per_head)

        no_keys, dim = self.keys.size()

        q = self.q_lin(query)
        q = q.view(batch_size * n_heads, dim_per_head).unsqueeze(1)
        # q = prepare_head(self.q_lin(query))

        k = self.k_lin(self.keys)
        k = k.unsqueeze(0).expand(batch_size, no_keys, dim)
        k = k.view(batch_size * n_heads, k.size(1), dim_per_head)

        v = self.v_lin(self.values)
        v = v.unsqueeze(0).expand(batch_size, no_keys, dim)
        v = v.view(batch_size * n_heads, v.size(1), dim_per_head)

        # k = prepare_head(self.k_lin(self.keys))
        # v = prepare_head(self.v_lin(self.values))

        dot_prod = q.div_(scale).bmm(k.transpose(1, 2))
        # [B * n_heads, 1, no_keys]

        attn_weights = F.softmax(dot_prod, dim=-1).type_as(query)
        attn_weights = self.attn_dropout(attn_weights)  # --attention-dropout

        attentioned = attn_weights.bmm(v)  # batch_size*n_heads, 1, dim_per_head
        attentioned = attentioned.unsqueeze(1)
        attentioned = attentioned.view(batch_size, n_heads * dim_per_head)

        out = self.out_lin(attentioned)

        return out
