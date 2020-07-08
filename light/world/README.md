# LIGHT World

The LIGHT World operates on a level above the LIGHT Graph, and it is responsible for maintaining track of agents within the world, listening to their actions, parsing them, and executing them on the underlying graph.

## Purgatory

`Purgatory` is responsible for managing `Soul`'s. It should be created as a member of a `World` when the world is created. Whatever created that world can then register souls to fill up the `World`'s agents by using `register_filler_soul_provider` and `fill_soul`.