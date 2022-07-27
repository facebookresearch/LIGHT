#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import light.modeling.tasks.common_sense.constants as consts
from collections import Counter

def calc_f1(truth, gen):
    # calculate f1 for item lists
    # truth: true list of item names
    # gen: list of generated item names

    truth_tokens = " ".join(truth).split()
    gen_tokens = " ".join(gen).split()
    # truth and gen should be sets of items
    if len(truth_tokens) == 0 or len(gen_tokens) == 0:
        return int(truth_tokens == gen_tokens)
    num_same = len([o for o in truth_tokens if o in gen_tokens])
    if num_same == 0:
        # otherwise f1 score will be undefined
        return 0
    precision = 1.0 * num_same / len(gen_tokens)
    recall = 1.0 * num_same / len(truth_tokens)
    return (2 * precision * recall) / (precision + recall)


def room_to_obj_chars(room):
    # go from room tuples to objects, characters, and secondary objects

    objs = set()
    chars = set()
    secondary_objs = set()
    tuple_list = room.split(consts.GRAPH_STATES_DELIM)
    inside_edges = set()
    room_name = None
    for tuple in tuple_list:
        try:
            v1, edge, v2 = tuple.split(consts.GRAPH_TUPLES_DELIM)
            if edge == "IS_TYPE":
                if v2 == "OBJECT":
                    objs.add(v1)
                elif v2 == "CHARACTER":
                    chars.add(v1)
                elif v2 == "ROOM":
                    room_name = v1

            if edge in ("IS_CARRYING", "IS_WIELDING", "IS_WEARING"):
                secondary_objs.add(v2)
            if edge == "IS_INSIDE":
                inside_edges.append((v1, v2))
        except:
            # error reading edge
            pass
    inside_edges = set([v1 for v1, v2 in inside_edges if v2 != room_name])
    secondary_objs.update(inside_edges)
    return objs, chars, secondary_objs


def objs_to_static_attribute_count(room, objs):
    # search a room for static object attributes corresponding to the passed objects
    # returns number of such attributes, for use in calculating pct of potential attributes
    attr_count = 0
    tuple_list = room.split(consts.GRAPH_STATES_DELIM)
    for tuple in tuple_list:
        try:
            v1, edge, v2 = tuple.split(consts.GRAPH_TUPLES_DELIM)
            if edge in (
                "IS_GETTABLE",
                "IS_DRINK",
                "IS_FOOD",
                "IS_CONTAINER",
                "IS_SURFACE",
                "IS_WEARABLE",
                "IS_WIELDABLE",
            ):
                if v1 in objs:
                    attr_count += 1
        except:
            # error reading edge
            pass
    return attr_count


def calculate_room_kb_metrics(truth_room, generated_room):
    # compare true room and generated room and return dict of metrics
    gen_objs, gen_chars, gen_secondary = room_to_obj_chars(generated_room)
    attr_pct = -1
    all_objs = gen_objs.union(gen_secondary)
    if len(all_objs) > 0:
        static_attr_count = objs_to_static_attribute_count(generated_room, all_objs)
        # right now there are 7 static attributes
        attr_pct = float(static_attr_count) / (len(all_objs) * 7)
    truth_objs, truth_chars, truth_secondary = room_to_obj_chars(truth_room)

    gen_primary = gen_objs.difference(gen_secondary)
    truth_primary = truth_objs.difference(truth_secondary)

    metrics = {
        "obj_f1": calc_f1(truth_objs, gen_objs),
        "num_objs": len(gen_objs),
        "true_num_objs": len(truth_objs),
        "num_secondary_objs": len(gen_secondary),
        "true_num_secondary_objs": len(truth_secondary),
        "obj_primary_f1": calc_f1(truth_primary, gen_primary),
        "obj_secondary_f1": calc_f1(truth_secondary, gen_secondary),
        "char_f1": calc_f1(truth_chars, gen_chars),
        "num_chars": len(gen_chars),
        "true_num_chars": len(truth_chars),
        "static_pct": attr_pct,
    }

    return metrics

def parse_errors(errors):
    # errors: list of error strings from commonsense agent validation
    # return dict of each error type's counts
    edge_count = 0
    start_count = 0
    correct_count = 0
    match_count = 0
    name_count = 0
    value_count = 0
    room_count = 0
    size_count = 0
    other = 0

    edge_errors = {}

    for error in errors:
        if error == "start":
            start_count += 1
        elif error == "no match":
            match_count += 1
        elif error == "correct":
            correct_count += 1
        elif error.startswith("incorrect edge:"):
            edge_count += 1
            names = error.split("incorrect edge: ")[1]
            names = names.split(" -=--=- ")
            if len(names) == 2:
                pred, corr = names
                if corr not in edge_errors:
                    edge_errors[corr] = []
                edge_errors[corr].append(pred)
            else:
                print(names)

        elif error.startswith("incorrect size:"):
            size_count += 1
        elif error.startswith("incorrect name:"):
            name_count += 1
        elif error.startswith("incorrect value:"):
            value_count += 1
        elif error.startswith("incorrect room name:"):
            room_count += 1
        else:
            other += 1

    error_counts = {}
    for cor, preds in edge_errors.items():
        error_counts[cor] = Counter(preds)

    return {
        'edge_count':edge_count,
        'start_count':start_count,
        'match_count':match_count,
        'name_count':name_count,
        'value_count':value_count,
        'room_count':room_count,
        'size_count':size_count,
        'correct': correct_count,
        'other':other,
        'total': len(errors),
        'edge_errors': error_counts,
        'raw_errors': errors
    }
