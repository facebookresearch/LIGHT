# LIGHT Souls

The LIGHT `Soul` class is responsible for inhabiting `GraphAgent`'s, observing events, and taking actions. In short, the `OOGraph` is constrained as a graph data model, wherein all nodes are static and take no actions. `GraphEvent`'s can make modifications to an `OOGraph`, but we need to have a class responsible for actually taking and observing those `GraphEvent`'s. This is where the `Soul` comes in, and is responsible for being the active element of the otherwise static `GraphAgents`.

## Lifecycle
`Soul`'s are tied to a `GraphAgent` upon initialization. They should be uniquely attached to that `target_node`, but can initialize any number of additional members required to keep track of actions and responses and such.

`Soul`'s will recieve `GraphEvent`'s to observe in calls to `observe_event`. These calls will be launched in the current asyncio event loop by `wrap_observe_event`, and can be seen in the `_observe_futures` property. They are launched in the background to allow the soul to respond to the event whenever they'd like, without blocking the main thread.

When a `Soul`'s time is up, either due to the `GraphAgent` being removed from the graph, or due to a disconnect, or a human inhabiting an agent filled by a model, the `reap` method will be called. This method should clean up any resources, and set any required flags such that any remaining `_observe_futures` will exit without taking additional action. It doesn't need to wait for them to exit before returning, but the default implementation calls `cancel` on outstanding futures.

## Important Flags

Some `Soul`'s set flags on `GraphAgent`'s to be able to be interpreted by other `Soul`'s or elements of the world. These generally should be prepended with an `_` such that they don't get compressed into the saved formats.

Current flags:
- `is_human`: Set by `PlayerSoul` to designate `GraphAgent`'s that are inhabited by a real player. Used by the world to ensure we don't doubly assign a `GraphAgent` to two different players, and by `ModelSoul`'s to differentiate between inter-model chat and chat with a human.
