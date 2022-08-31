# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

if __name__ == "__main__":
    import argparse
    import pickle
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from light.modeling.agents.quests.rl.base.models.topkmodel import TopKPolicy
    from light.modeling.agents.quests.rl.base.environments.environment import (
        Environment,
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--rl_or_sup", default="rl")
    parser.add_argument("--data_path", default="")
    parser.add_argument("--niters", type=int, default=10000)
    parser.add_argument("--N", type=int, default=100)
    parser.add_argument("--d", type=int, default=128)
    parser.add_argument("--K", type=int, default=50)
    parser.add_argument("--verbose", default=50)
    parser.add_argument("--entropy_weight", type=float, default=0.00001)
    parser.add_argument(
        "--lr", type=float, default=0.001
    )  # for Margaret's .pkl use .0001
    args = parser.parse_args()

    RL = args.rl_or_sup == "rl"
    cuda = True

    RL = args.rl_or_sup == "rl"
    if args.data_path != "":
        f = open(args.data_path, "rb")
        X = pickle.load(f)
        f.close()
        env = Environment(None)
        env.set_attrs(X[0])
        d = env.embeddings.shape[1]
        K = env.embeddings.shape[0] - 1
        N = len(X)
        data = torch.zeros(N, K + 1, d)
        labels = torch.zeros(N).long()
        for i in range(N):
            env.set_attrs(X[i])
            data[i] = env.embeddings
            labels[i] = env.output_label

    else:
        N, K, d = (args.N, args.K, args.d)
        contexts = torch.randn(N, d)
        candidates = torch.randn(N, K, d)
        data = torch.zeros(N, K + 1, d)
        data[:, 0, :] = contexts
        data[:, 1:, :] = candidates
        labels = torch.randint(K, (N,))

    P = TopKPolicy([K + 1, d], K + 1)
    model = P.base
    if cuda:
        model = model.cuda()
    model.train()
    loss = 0

    if cuda:
        labels = labels.cuda()
        data = data.cuda()
    nll = nn.NLLLoss()
    optimizer = optim.RMSprop(model.parameters(), lr=args.lr)
    #    optimizer = optim.Adagrad(model.parameters(), lr=args.lr)
    lsmx = nn.LogSoftmax()
    smx = nn.LogSoftmax()

    def rl_step():
        logits = model(data)[1]
        C = torch.distributions.categorical.Categorical(logits=logits)
        actions = C.sample()
        actions = actions.long()
        rewards = (actions.squeeze() == labels).float() - 0.5
        z = lsmx(logits)
        p = smx(logits)
        action_lsm = z.gather(1, actions.long())
        loss = -(rewards * action_lsm.squeeze()).mean()
        entropy = (z * p).sum(1)
        return logits, actions, rewards, z, loss, entropy.mean()

    for i in range(args.niters):
        optimizer.zero_grad()
        if RL:
            logits, actions, rewards, z, rl_loss, entropy = rl_step()
            loss = rl_loss + args.entropy_weight * entropy
        else:
            z = lsmx(model(data)[1])
            loss = nll(z, labels)
        loss.backward()
        optimizer.step()
        if i % args.verbose == 0:
            if RL:
                print(
                    i,
                    " loss is "
                    + str(loss.item())
                    + " reward is "
                    + str(rewards.sum().item()),
                )
            else:
                print(i, " loss is " + str(loss.item()))
