#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import light.modeling.tasks.common_sense.constants as consts


def get_light_special_tokens():
    special_tokens = [consts.GRAPH_TUPLES_DELIM]
    for edge in consts.GraphEdges:
        special_tokens.append(edge.name)
    for mutation in consts.GraphMutations:
        special_tokens.append(mutation.name)
    return ",".join(special_tokens)
