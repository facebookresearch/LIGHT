#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Generate dialogue of a provided model and save it as format required for an acute eval
task.
"""

from parlai.core.params import ParlaiParser
from parlai.core.agents import create_agent
from parlai.core.worlds import create_task
from parlai.core.script import ParlaiScript
from parlai.utils.io import PathManager
import parlai.utils.logging as logging

import json
import random
from tqdm import tqdm


def setup_args(parser=None):
    if parser is None:
        parser = ParlaiParser(True, True, "Evaluate a model")
    # Get command line arguments
    parser.add_argument(
        "-rf",
        "--report-filename",
        type=str,
        default="",
        help="Filename to save the dialogue dict.",
    )
    parser.add_argument("-ne", "--num-examples", type=int, default=-1)
    parser.set_params(datatype="valid")
    return parser


def _eval_single_world(opt, agent, task):
    logging.info(f'Evaluating task {task} using datatype {opt.get("datatype")}.')
    # set up world logger
    task_opt = opt.copy()  # copy opt since we're editing the task
    task_opt["task"] = task

    world = create_task(task_opt, agent)  # create worlds for tasks

    # max number of examples to evaluate
    max_cnt = opt["num_examples"] if opt["num_examples"] > 0 else float("inf")
    cnt = 0

    dialogue_dicts = []
    model_id = opt["model_file"]
    if not model_id:
        model_id = opt["model"]

    cs_cnt = 0

    pbar = tqdm(total=max_cnt, desc=model_id)
    while not world.epoch_done() and cnt < max_cnt:
        cnt += opt.get("batchsize", 1)
        world.parley()

        cs_cnt += int(bool(world.acts[0]["checked_sentence"]))

        dialogue_dicts.append(
            {
                "id": cnt,
                "speakers": [opt["task"], model_id],
                "knowledge": world.acts[0].get("checked_sentence", ""),
                "title": world.acts[0].get("title", ""),
                "labels": world.acts[0].get("eval_labels", ""),
                "history": world.acts[0].get("history", ""),
                "dialogue": [
                    {
                        "id": opt["task"],
                        "text": world.acts[0]["text"],
                    },
                    {
                        "id": model_id,
                        "text": world.acts[1]["text"],
                    },
                ],
            }
        )
        pbar.update(1)
    pbar.close()
    print(cs_cnt, cnt)

    world.reset()
    return dialogue_dicts


def eval_model(opt):
    """
    Evaluates a model.
    """
    random.seed(42)
    if "train" in opt["datatype"] and "evalmode" not in opt["datatype"]:
        raise ValueError(
            "You should use --datatype train:evalmode if you want to evaluate on "
            "the training set."
        )

    # load model and possibly print opt
    agent = create_agent(opt, requireModelExists=True)
    agent.opt.log()

    task = opt["task"]
    data = _eval_single_world(opt, agent, task)

    # Write the data to json.
    if opt["report_filename"]:
        with open(opt["report_filename"], "w") as outf:
            json.dump(data, outf)
        print(f'Saved to "{opt["report_filename"]}".')


class EvalModel(ParlaiScript):
    @classmethod
    def setup_args(cls):
        return setup_args()

    def run(self):
        return eval_model(self.opt)


if __name__ == "__main__":
    EvalModel.main()
