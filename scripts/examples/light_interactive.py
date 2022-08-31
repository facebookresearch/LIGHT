#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from parlai.core.params import ParlaiParser
from parlai.core.agents import create_agent
from parlai.core.worlds import create_task
from parlai.agents.local_human.local_human import LocalHumanAgent

import json
import random


personas_path = "/checkpoint/parlai/zoo/light/personas.json"
SETTING_NAME = "_setting_name "
SETTING_DESC = "_setting_desc "
SELF_NAME = "_self_name "
SELF_PERSONA = "_self_persona "
PARTNER_NAME = "_partner_name "
SELF_SAY = "_self_say "
PARTNER_SAY = "_partner_say "


def setup_args(parser=None):
    if parser is None:
        parser = ParlaiParser(True, True, "Interactive chat with a model")
    parser.add_argument("-d", "--display-examples", type="bool", default=False)
    parser.add_argument(
        "--display-prettify",
        type="bool",
        default=False,
        help="Set to use a prettytable when displaying "
        "examples with text candidates",
    )
    parser.add_argument(
        "--display-ignore-fields",
        type=str,
        default="label_candidates,text_candidates",
        help="Do not display these fields",
    )
    parser.add_argument(
        "-it",
        "--interactive-task",
        type="bool",
        default=True,
        help="Create interactive version of task",
    )
    parser.set_defaults(
        interactive_mode=True,
        task="interactive",
        model_file="/checkpoint/parlai/zoo/light/reddit_polyranker/model",  # change the model file if you have another pretrained model
    )
    LocalHumanAgent.add_cmdline_args(parser)
    return parser


def interactive(opt, print_parser=None):
    if print_parser is not None:
        if print_parser is True and isinstance(opt, ParlaiParser):
            print_parser = opt
        elif print_parser is False:
            print_parser = None
    if isinstance(opt, ParlaiParser):
        print("[ Deprecated Warning: interactive should be passed opt not Parser ]")
        opt = opt.parse_args()

    random.seed()

    # Create model and assign it to the specified task
    agent = create_agent(opt, requireModelExists=True)
    human_agent = LocalHumanAgent(opt)

    if print_parser:
        # Show arguments after loading model
        print_parser.opt = agent.opt
        print_parser.opt.log()

    # choose personas
    personas = json.loads(open(personas_path, "rb").read())
    p1, p2 = random.sample(personas, 2)
    p1_name, pers1, loc1 = p1
    p2_name, pers2, loc2 = p2
    # choose a random location from one of the provided locations
    loc = random.choice([loc1, loc2])
    loc_name, loc_desc = loc.split(". ", 1)

    # human persona
    p1_obs_string = "\n".join(
        [
            SETTING_NAME + loc_name,
            SETTING_DESC + loc_desc,
            PARTNER_NAME + p2_name,
            SELF_NAME + p1_name,
            SELF_PERSONA + pers1,
        ]
    )
    # bot persona
    p2_obs_string = "\n".join(
        [
            SETTING_NAME + loc_name,
            SETTING_DESC + loc_desc,
            PARTNER_NAME + p1_name,
            SELF_NAME + p2_name,
            SELF_PERSONA + pers2,
        ]
    )

    print("Please play the following persona and setting:\n\n{}".format(p1_obs_string))

    used_cands = []
    bot_obs = [p2_obs_string]  # used for tracking history
    cnt = 0
    last_act = None
    while True:
        new_act = {"episode_done": True}
        human_act = human_agent.act()
        bot_obs.append(PARTNER_SAY + human_act["text"])
        new_act["text"] = "\n".join(bot_obs)
        agent.observe(new_act)
        last_act = agent.act()
        # get a unique utterance among 100 available candidates
        if "text_candidates" in last_act:
            for cand in last_act["text_candidates"]:
                if cand not in used_cands:
                    used_cands.append(cand)
                    if type(last_act) == dict:
                        last_act["text"] = cand
                    else:
                        last_act.force_set("text", cand)
                    break
        bot_obs.append(SELF_SAY + last_act["text"])
        human_agent.observe(last_act)
        cnt += 1


if __name__ == "__main__":
    parser = setup_args()
    interactive(parser.parse_args(print_args=False), print_parser=parser)
