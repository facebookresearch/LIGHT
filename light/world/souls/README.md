# LIGHT Souls

The LIGHT `Soul` class is responsible for inhabiting `GraphAgent`'s, observing events, and taking actions. In short, the `OOGraph` is constrained as a graph data model, wherein all nodes are static and take no actions. `GraphEvent`'s can make modifications to an `OOGraph`, but we need to have a class responsible for actually taking and observing those `GraphEvent`'s. This is where the `Soul` comes in, and is responsible for being the active element of the otherwise static `GraphAgents`. 

## Important Flags

Some `Soul`'s set flags on `GraphAgent`'s to be able to be interpreted by other `Soul`'s or elements of the world. These generally should be prepended with an `_` such that they don't get compressed into the saved formats.

Current flags:
- `is_human`: Set by `PlayerSoul` to designate `GraphAgent`'s that are inhabited by a real player. Used by the world to ensure we don't doubly assign a `GraphAgent` to two different players, and by `ModelSoul`'s to differentiate between inter-model chat and chat with a human.
