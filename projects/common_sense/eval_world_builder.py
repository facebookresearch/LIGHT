#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from parlai.core.params import ParlaiParser
from parlai.core.script import ParlaiScript, register_script
import parlai.utils.logging as logging
from common_sense_utils import CommonSenseAgent
from world_builder_eval_utils import calculate_room_kb_metrics, parse_errors
import light.modeling.tasks.common_sense.constants as consts
from light.modeling.tasks.common_sense.agents import generate_graph_tuples

import random
import jsonlines
import json
from time import time
import pandas as pd
import pickle
import copy


def setup_args(parser=None):
    if parser is None:
        parser = ParlaiParser(True, True, "Test common sense model for room building")
    parser.set_defaults(interactive_mode=True, task="interactive")
    return parser


def run_create_char_objs(graph, agent, count=3):
    original_characters = set([c["name"] for c in graph["characters"]])
    original_objects = set([c["name"] for c in graph["objects"]])
    new_graph = agent.add_character(graph, count=count)
    new_graph = agent.add_object(new_graph, count=count)

    new_characters = set([c["name"] for c in new_graph["characters"]])
    new_objects = set([c["name"] for c in new_graph["objects"]])

    char_diff = [c for c in new_characters if c not in original_characters]
    for c in char_diff:
        new_graph = agent.add_all_character_attributes(new_graph, c)

    obj_diff = [c for c in new_objects if c not in original_objects]
    for c in obj_diff:
        new_graph = agent.add_all_object_attributes(new_graph, c)
    return new_graph


def interactive(opt):
    # setup data
    just_desc_dropouts = {}
    for enum in consts.GraphDropoutOptions:
        if enum not in (
            consts.GraphDropoutOptions.ROOM_NAME,
            consts.GraphDropoutOptions.ROOM_DESCRIPTION,
            consts.GraphDropoutOptions.ROOM_BACKSTORY,
        ):
            just_desc_dropouts[enum] = 1

    element_types = [
        consts.ElementType.ROOM,
        consts.ElementType.OBJECT,
        consts.ElementType.CHARACTER,
    ]
    test_data = []

    # load in data to run test on
    with jsonlines.open(
        "/private/home/alexgurung/ParlAI/data/light_common_sense/rooms_and_contents/test.jsonl",
        "r",
    ) as f:
        for room_graph in f:
            input_txt = generate_graph_tuples(
                room_graph,
                element_types,
                only_in_edges=True,
                dropouts=just_desc_dropouts,
                label_tuples=set(),
                remove_reference=False,
            )
            output_txt = generate_graph_tuples(
                room_graph,
                element_types,
                only_in_edges=True,
                dropouts={},
                label_tuples=set(),
                remove_reference=False,
            )
            test_data.append((input_txt, output_txt, room_graph))

    # pick random element from test_data, use full set for eval
    save_res = True
    save_error = True
    test_data = test_data[3:4]
    # test_data = test_data[:5]
    # test_data = test_data[3:20]
    # test_data = test_data

    if isinstance(opt, ParlaiParser):
        logging.error("interactive should be passed opt not Parser")
        opt = opt.parse_args()

    for model_name in [
        "bart_all_simple_Sun_Jan_23/c9d",
        "bart_all_simple_Mon_Jan_24/09d",
        "bart_all_simple_Wed_Jan_26/317",
    ]:
        for force in [True]:
            # for model_name in ["bart_all_simple_Mon_Jan_24/09d"]:
            model_start = time()
            # agent = CommonSenseAgent(
            #     opt, model_name=model_name, force_add=True, verbose=False, count_errors=True
            # )
            agent = CommonSenseAgent(
                opt,
                model_name=model_name,
                force_add=force,
                verbose=False,
                count_errors=True,
            )
            # agent = CommonSenseAgent(opt, force_add=True, verbose=True)
            agent.opt.log()

            times = []
            # oos = []
            all_metrics = []
            for context, true_room, graph in test_data:
                # input_context, true_output_room, empty_room (aside from room descriptions)
                s = time()
                graph["characters"] = []
                graph["objects"] = []
                new_graph = agent.add_room_backstory(graph)
                new_graph = agent.add_room_description(new_graph)

                new_graph = run_create_char_objs(new_graph, agent, count=3)
                new_graph = run_create_char_objs(new_graph, agent, count=3)

                print(f"{time() - s:.02f} s")
                times.append(time() - s)

                metrics = calculate_room_kb_metrics(
                    true_room, agent.parse_room_graph(new_graph)
                )
                print(metrics)
                all_metrics.append(metrics)
            print("-" * 100)
            print(f"MODEL TOTAL TIME: {time() - model_start}")
            # print(agent.get_errors())

            errors = agent.get_errors()
            tasks = agent.get_tasks()
            graph_mods = agent.get_graph_mods()
            error_data = parse_errors(errors)
            error_data["raw_tasks"] = tasks
            error_data["raw_mods"] = graph_mods
            print(
                f"{len(error_data['raw_errors'])} vs {len(error_data['raw_tasks'])} vs {len(error_data['raw_mods'])}"
            )

            if save_res or save_error:
                split = model_name.split("/")
                folder = split[0]
                name = split[1]
                force_name = "force" if force else "noforce"
                if save_error:
                    with open(
                        f"/checkpoint/alexgurung/light/common_sense/add_format/{folder}/error_metrics_{name}_{force_name}_default.json",
                        "w",
                    ) as f:
                        json.dump(error_data, f)
                if save_res:
                    with open(
                        f"/checkpoint/alexgurung/light/common_sense/add_format/{folder}/builder_metrics_{name}_{force_name}_default.json",
                        "w",
                    ) as f:
                        json.dump(all_metrics, f)

            # print(error_data['edge_errors'])
            del error_data["edge_errors"]
            del error_data["raw_errors"]
            del error_data["raw_tasks"]
            del error_data["raw_mods"]
            df = pd.DataFrame(data=error_data.items(), columns=["key", "value"])
            print(df)
            print("-" * 100)


@register_script("interactive", aliases=["i"])
class Interactive(ParlaiScript):
    @classmethod
    def setup_args(cls):
        return setup_args()

    def run(self):
        return interactive(self.opt)


if __name__ == "__main__":
    random.seed(42)
    Interactive.main()
