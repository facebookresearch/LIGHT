#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""

After running this, to build cands:
py  ~/src/ParlAI/parlai/scripts/build_candidates.py -t fromfile -ffdp /tmp/valid.txt 
Then add cands to loading.

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
import os
import torch

def setup_args(parser=None):
    if parser is None:
        parser = ParlaiParser(True, True, "Interactive chat with a model")
    parser.add_argument(
        "--cands-file",
        type=str,
        default="/tmp/cands.txt"
    )
    parser.set_defaults(interactive_mode=True, task="interactive")
    LocalHumanAgent.add_cmdline_args(parser)
    return parser


def gen_quest(q):
    msg = {}
    
    motivation = random.choice(['mid_motivation', 'short_motivation', 'long_motivation'])
    motivation_txt = q[motivation]
    partner_name = 'unknown'
    object_name = 'unknown'
    goals = [ q['goal'] ]
    #import pdb; pdb.set_trace()
    for g in q['timeline']:
        goals.append(g['action'])
    goal_txt = random.choice(goals)
    
    msg['text'] = '\n'.join([
        'character: ' + q['character'].replace('the ', ''),
        'persona: ' + random.choice([q['persona'], 'unknown']),
        #'partner: ' + partner_name,
        #'object:' + object_name,
        #'goal: ' + goal_txt,
        'goal: ' + random.choice([motivation_txt, 'unknown'])
    ])
    lab = motivation_txt
    msg['labels'] = [ goal_txt ]
    msg['episode_done'] = True
    #print(msg['text'])
    #print(lab)
    #import pdb; pdb.set_trace()
    return msg


def add_cands(msg, cands):
    p = torch.randperm(len(cands))
    c = []
    ind = 1
    c.append(msg['labels'][0])
    for i in range(0, 100):
        while True:
            txt = cands[ind]
            if txt != msg['labels'][0]:
                c.append(txt)
                ind += 1
                break
            else:
                ind += 1
    msg['label_candidates'] = c
                
def interactive(opt):
    quests = QuestLoader('/checkpoint/light/data/quests/quest_stems/')
    # try to load cands
    if os.path.isfile(opt['cands_file']):
        f = open(opt['cands_file'], "r")
        cands = []
        for w in f.readlines():
            cands.append(w.rstrip('\n'))
        f.close()
    else:
        cands = None

    fw = open('/tmp/train.txt', 'w')
    for j in range(0, len(quests.quests)):
        if (j % 40) != 0:
            for i in range(0, 10):
                msg = gen_quest(quests.quests[j])
                txt = msg_to_str(msg)
                fw.write(txt + '\n\n')
    fw.close()

    fw = open('/tmp/valid.txt', 'w')
    for j in range(0, len(quests.quests)):
        if (j % 40) == 0:
            for i in range(0, 10):
                msg = gen_quest(quests.quests[j])
                if cands is not None:
                    add_cands(msg, cands)
                txt = msg_to_str(msg)
                fw.write(txt + '\n\n')
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
