#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import parlai.utils.logging as logging
from parlai.core.message import Message
import copy
import threading
import asyncio
from light.registry.model_pool import ModelTypeName

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from light.registry.model_pool import ModelPool

args = {}
args["help"] = 0
args["inventory"] = 0
args["look"] = 0
args["wait"] = 0
emotes = "applaud,blush,cry,dance,frown,gasp,grin,groan,growl,laugh,nod,nudge,ponder,pout,scream,shrug,sigh,smile,stare,wave,wink,yawn".split(
    ","
)
for e in emotes:
    args[e] = 0
arg1 = [
    "follow",
    "unfollow",
    "open",
    "close",
    "go",
    "get",
    "drop",
    "hit",
    "hug",
    "eat",
    "drink",
    "wear",
    "wield",
    "remove",
    "examine",
]
for a in arg1:
    args[a] = 1
arg2 = ["get_from", "put", "give", "steal"]
for a in arg2:
    args[a] = 2


def num_args(v):
    return args[v]


def get_verb_and_divider(v):
    verb = v
    if verb == "get_from":
        return "get", "from"
    divider = ""
    if verb == "put":
        divider = "in"
    if verb == "give":
        divider = "to"
    if verb == "steal":
        divider = "from"
    return verb, divider


def get_input_cands(x, y2, y):
    words = x.split()
    args = num_args(y2)
    if args == 0:
        return set()
    verb, divider = get_verb_and_divider(y2)
    acts = set()
    for ngram_sz in range(1, 4):
        for start in range(0, len(words) - (ngram_sz - 1)):
            arg1 = " ".join(words[start : start + ngram_sz])
            act = verb + " " + arg1
            if args == 1:
                act = act.lower()
                acts.add(act)
            else:
                for ngram_sz2 in range(1, 4):
                    for start2 in range(start + ngram_sz, len(words) - (ngram_sz2 - 1)):
                        arg2 = " ".join(words[start2 : start2 + ngram_sz2])
                        act2 = act + " " + divider + " " + arg2
                        act2 = act2.lower()
                        acts.add(act2)

    # print(x, "|", y2, "|", y)
    # print(acts)
    # import pdb; pdb.set_trace()
    return acts


class ActionParser:
    def __init__(self, model_pool: "ModelPool"):
        if model_pool.has_model(ModelTypeName.PARSER):
            self.agent = model_pool.get_model(ModelTypeName.PARSER)
        else:
            self.agent = None
        # Lock to handle concurrency, fixed better with asycio
        self.parse_lock = threading.Condition()

    async def parse(self, txt, actor=None):
        if self.agent is None:
            # No model installed, return an empty string.
            return ""

        with self.parse_lock:
            # Predict verb first.
            txt = txt.lower()
            verbs = list(args.keys())
            query = Message(
                {
                    "id": "context",
                    "text": txt,
                    "label_candidates": verbs,
                    "episode_done": True,
                }
            )
            self.agent.observe(query)
            res = await self.agent.act()
            verb = res["text"]

        with self.parse_lock:
            # Given verb, predict the args (unless it's a no-arg action(.
            if args[verb] > 0:
                cands = list(get_input_cands(txt, verb, txt))
                query2 = Message(
                    {
                        "id": "context",
                        "text": txt,
                        "label_candidates": cands,
                        "episode_done": True,
                    }
                )
                self.agent.observe(query2)
                res2 = await self.agent.act()
                txt = res2["text"]
            else:
                txt = verb
        txt = self.post_process(txt, actor)

        return txt

    def post_process(self, txt, actor=None):
        txt = txt.rstrip("\n").rstrip("\r")
        txt = txt.replace("“", '"').replace("”", '"')
        if '"' in txt:
            return txt

        txts = txt.strip().split()
        new_txts = []
        postprocess_blacklist = ["the", "a", "an"]
        for idx, t in enumerate(txts):
            if t not in postprocess_blacklist or idx > 4:
                new_txts.append(t)
        new_txt = " ".join(new_txts)
        for (val_old, val_new) in [("go to ", "go "), ("to the ", "to "), ("from the ", "from "), ("to a ", "to "), ("from a ", "from "), ("with the ", "with "), ("with a ", "with ")]:
            new_txt = new_txt.replace(val_old, val_new)

        if new_txts[0] == "use" and "with" not in new_txts and actor is not None:
            # If no 'with' argument to 'use' is given, it is assumed to 'use' with yourself.
            new_txt += " with " + actor.name

        if new_txt in emotes:
            new_txt = "emote " + new_txt

        if new_txt.startswith("point at"):
            new_txt = new_txt.replace("point at", "point")
        if new_txt.startswith("point to"):
            new_txt = new_txt.replace("point to", "point")

        return new_txt
