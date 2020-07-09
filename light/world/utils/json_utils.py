#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
from light.graph.elements.graph_nodes import (
    GraphNode,
    GraphEdge,
)

class GraphEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return sorted(list(o))
        if isinstance(o, list):
            return sorted(o)
        if isinstance(o, GraphEdge):
            return {k: v for k, v in o.__dict__.copy().items() if not k.startswith('_')}
        if not isinstance(o, GraphNode):
            return super().default(o)
        use_dict = {k: v for k, v in o.__dict__.copy().items() if not k.startswith('_')}
        return use_dict
