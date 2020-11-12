#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""
py interactive_action_parser.py -mf /checkpoint/jase/projects/light/parser/parser2/34c_jobid=1/model
"""
from parlai.core.params import ParlaiParser
from parlai.core.worlds import create_task
from parlai.core.script import ParlaiScript, register_script
from parlai.utils.world_logging import WorldLogger
from parlai.agents.local_human.local_human import LocalHumanAgent
from parlai.core.message import Message

from light.world.action_parser import ActionParser
import random


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
    parser.add_argument(
        "--save-world-logs",
        type="bool",
        default=False,
        help="Saves a jsonl file containing all of the task examples and "
        "model replies. Must also specify --report-filename.",
    )
    parser.add_argument(
        "--parser-model-file",
        type=str,
        default="/checkpoint/jase/projects/light/parser/parser3/34c_jobid=1/model"
    )
    parser.set_defaults(interactive_mode=True, task="interactive")
    LocalHumanAgent.add_cmdline_args(parser)
    return parser


def interactive(opt):
    # Create model and assign it to the specified task
    parser = ActionParser(opt)
    human_agent = LocalHumanAgent(opt)
    world = create_task(opt, [human_agent, parser.agent])

    # Show some example dialogs:
    while not world.epoch_done():
        txt = input("Action> ")
        parse_txt = parser.parse(txt)
        print(parse_txt)


class Interactive(ParlaiScript):
    @classmethod
    def setup_args(cls):
        return setup_args()

    def run(self):
        return interactive(self.opt)


if __name__ == "__main__":
    random.seed(42)
    Interactive.main()
