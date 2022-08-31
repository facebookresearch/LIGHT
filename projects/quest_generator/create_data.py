#!/usr/bin/env python3


# Copyright (c) Meta Platforms, Inc. and affiliates.
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
from parlai.utils.misc import msg_to_str

from light.world.action_parser import ActionParser
from light.world.quest_loader import QuestLoader
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
        default="/checkpoint/jase/projects/light/parser/parser3/34c_jobid=1/model",
    )
    parser.set_defaults(interactive_mode=True, task="interactive")
    LocalHumanAgent.add_cmdline_args(parser)
    return parser


def gen_quest(q):
    msg = {}

    motivation = random.choice(
        ["mid_motivation", "short_motivation", "long_motivation"]
    )
    motivation_txt = q[motivation]
    partner_name = "unknown"
    object_name = "unknown"
    goals = [q["goal"]]
    for g in q["timeline"]:
        goals.append(g["action"])
    goal_txt = random.choice(goals)

    msg["text"] = "\n".join(
        [
            "character: " + q["character"].replace("the ", ""),
            "persona: " + random.choice([q["persona"], "unknown"]),
            #'partner: ' + partner_name,
            #'object:' + object_name,
            "goal: " + goal_txt,
            "task: " + motivation,
        ]
    )
    lab = motivation_txt
    msg["labels"] = [lab]
    msg["episode_done"] = True
    # print(msg['text'])
    # print(lab)
    # import pdb; pdb.set_trace()
    return msg


def interactive(opt):
    # quests = QuestLoader('/checkpoint/light/data/quests/quest_stems/')
    quests = QuestLoader("/tmp/q/approved/")

    fw = open("/tmp/train.txt", "w")
    for j in range(0, len(quests.quests)):
        if (j % 40) != 0:
            for i in range(0, 10):
                msg = gen_quest(quests.quests[j])
                txt = msg_to_str(msg)
                fw.write(txt + "\n\n")
    fw.close()

    fw = open("/tmp/valid.txt", "w")
    for j in range(0, len(quests.quests)):
        if (j % 40) == 0:
            for i in range(0, 10):
                msg = gen_quest(quests.quests[j])
                txt = msg_to_str(msg)
                fw.write(txt + "\n\n")
    fw.close()


class Interactive(ParlaiScript):
    @classmethod
    def setup_args(cls):
        return setup_args()

    def run(self):
        return interactive(self.opt)


if __name__ == "__main__":
    random.seed(42)
    Interactive.main()
