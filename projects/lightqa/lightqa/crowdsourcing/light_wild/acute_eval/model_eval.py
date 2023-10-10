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
import parlai.utils.logging as logging

import os
import json
import random
from tqdm import tqdm


def generate_dialogue_from_light_dialog_context(
    context: str, teacher_name: str, model_name: str
):
    kword_mapping = {
        "_task_speech": "skip",
        "_setting_name": teacher_name,
        "_setting_desc": teacher_name,
        "_self_name": model_name,
        "_partner_name": teacher_name,
        "_self_persona": model_name,
        "_self_say": model_name,
        "_partner_say": teacher_name,
    }
    prefix_for_line = {
        "_self_name": "My name is: ",
        "_partner_name": "My name is: ",
        "_setting_name": "You are located in: ",
    }
    dialogue = []
    for line in context.split("\n"):
        line_type = line.split()[0]
        if not line.startswith("_") or kword_mapping[line_type] == "skip":
            continue
        text = prefix_for_line.get(line_type, "") + " ".join(line.split()[1:]).strip()
        dialogue.append(
            {
                "id": kword_mapping[line_type],
                "text": text,
            }
        )
    return dialogue


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
        if "knowledge_response_model_path" in opt:
            model_id += "_" + opt["knowledge_response_model_path"]

    pbar = tqdm(total=max_cnt, desc=model_id)
    while not world.epoch_done() and cnt < max_cnt:
        cnt += opt.get("batchsize", 1)
        world.parley()

        dialogue_history = generate_dialogue_from_light_dialog_context(
            context=world.acts[0]["text"],
            teacher_name=opt["task"],
            model_name=model_id,
        )

        dialogue_dicts.append(
            {
                "id": cnt,
                "speakers": [opt["task"], model_id],
                "labels": world.acts[0].get("eval_labels", ""),
                "dialogue": dialogue_history
                + [
                    {
                        "id": model_id,
                        "text": world.acts[1]["text"],
                    },
                ],
            }
        )
        pbar.update(1)
    pbar.close()

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
        os.makedirs("/".join(opt["report_filename"].split("/")[:-1]), exist_ok=True)
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
