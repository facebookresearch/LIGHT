#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""
Convert a dataset into the ParlAI text format.

## Examples

```shell
parlai convert_data_to_parlai_format -t babi:task1k:1 --outfile /tmp/dump
```
"""

from parlai.core.params import ParlaiParser
from parlai.agents.repeat_label.repeat_label import RepeatLabelAgent
from parlai.core.worlds import create_task
from parlai.utils.misc import msg_to_str, TimeLogger
import parlai.utils.logging as logging
from parlai.core.script import ParlaiScript, register_script
import random
import tempfile
import copy


def clean(msg):
    msg = copy.deepcopy(msg)
    txt = msg["text"]
    res = []
    app = ""
    convo_has_started = False
    for t in txt.split("\n"):
        if "_self_say " in t:
            convo_has_started = True
        if "_partner_say " in t:
            convo_has_started = True
        if "_partner_name " in t:
            partner_name = t.replace("_partner_name ", "")

    first_convo_line = True
    for t in txt.split("\n"):
        if t.startswith("_") and "_object_desc" not in t:
            if (
                t.startswith("_self_act")
                or t.startswith("_self_emote")
                or t.startswith("_partner_act")
                or t.startswith("_partner_emote")
            ):
                t = t.replace("_self_act ", "")
                t = t.replace("_partner_act ", "")
                t = t.replace("_self_emote ", "")
                t = t.replace("_partner_emote ", "")
                app = app + " *" + t + "*"
            else:
                # if ("_partner_say " in t) or ("_self_say" in t):
                #    #import pdb; pdb.set_trace()
                if ("_partner_say " in t) or ("_self_say" in t):
                    first_convo_line = False
                t = t.replace("_self_say ", "")
                t = t.replace("_partner_say ", "")
                res.append(t + app)
                app = ""

    if not convo_has_started:
        res.append("START " + partner_name)
    else:
        res.append("CONTINUE " + partner_name)

    msg.force_set("text", "\n".join(res))
    # print(res)
    return msg


def dump_data(opt):
    # create repeat label agent and assign it to the specified task
    agent = RepeatLabelAgent(opt)
    world = create_task(opt, agent)
    opt.log()
    ignorefields = opt.get("ignore_fields", "")
    if opt["outfile"] is None:
        outfile = tempfile.mkstemp(
            prefix="{}_{}_".format(opt["task"], opt["datatype"]), suffix=".txt"
        )[1]
    else:
        outfile = opt["outfile"]

    if opt["num_examples"] == -1:
        num_examples = world.num_examples()
    else:
        num_examples = opt["num_examples"]
    log_timer = TimeLogger()

    logging.debug("starting to convert...")
    logging.info(f"saving output to {outfile}")
    fw = open(outfile, "w")
    for _ in range(num_examples):
        world.parley()
        acts = world.get_acts()
        value = acts[0].get("labels", acts[0].pop("eval_labels", None))
        acts[0].force_set("labels", value)

        msg = clean(acts[0])

        txt = msg_to_str(msg, ignore_fields=ignorefields)
        fw.write(txt + "\n")
        if acts[0].get("episode_done", False):
            fw.write("\n")

        if log_timer.time() > opt["log_every_n_secs"]:
            text, _log = log_timer.log(world.total_parleys, world.num_examples())
            logging.info(text)

        if world.epoch_done():
            logging.info("epoch done")
            break
    fw.close()


def setup_args():
    # Get command line arguments
    parser = ParlaiParser(description="Dump a task to a standardized format")
    parser.add_argument(
        "-n",
        "--num-examples",
        default=-1,
        type=int,
        help="Total number of exs to convert, -1 to convert all examples",
    )
    parser.add_argument(
        "-of",
        "--outfile",
        default=None,
        type=str,
        help="Output file where to save, by default will be created in tmp",
    )
    parser.add_argument(
        "-if",
        "--ignore-fields",
        default="id",
        type=str,
        help="Ignore these fields from the message (returned with .act() )",
    )
    parser.add_argument("-ltim", "--log-every-n-secs", type=float, default=2)
    parser.set_defaults(datatype="train:stream")
    return parser


@register_script("convert_to_parlai", hidden=True)
class ConvertDataToParlaiFormat(ParlaiScript):
    @classmethod
    def setup_args(cls):
        return setup_args()

    def run(self):
        return dump_data(self.opt)


if __name__ == "__main__":
    random.seed(42)
    ConvertDataToParlaiFormat.main()
