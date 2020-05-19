#!/usr/bin/env python3
# Builds a LIGHT map using a StarSpace model to connect locations.
# Is not currently connected to the LIGHT text adventure game API
#  (but should be straight-forward).


from light.graph.builders.starspace_neighbor import (
    StarspaceNeighborBuilder,
)

from light.world.world import World
import random
import copy
import numpy as np

random.seed(6)
np.random.seed(6)


# TODO deprecate in favor of graph builders
class BuildLightMap():
    def __init__(self, debug=True):
        self.world = StarspaceNeighborBuilder()
        self.world.build_world()

    def get_graph(self):
        return World.from_graph(self.world.get_graph())


    def add_agent(self, g, agent_id):
        g._node_npcs.add(agent_id)


if __name__ == '__main__':
    random.seed(6)
    m = BuildLightMap()
