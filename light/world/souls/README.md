# LIGHT Souls

The LIGHT `Soul` class is responsible for inhabiting `GraphAgent`'s, observing events, and taking actions. In short, the `OOGraph` is constrained as a graph data model, wherein all nodes are static and take no actions. `GraphEvent`'s can make modifications to an `OOGraph`, but we need to have a class responsible for actually taking and observing those `GraphEvent`'s. This is where the `Soul` comes in, and is responsible for being the active element of the otherwise static `GraphAgents`.

## Lifecycle
`Soul`'s are tied to a `GraphAgent` upon initialization. They should be uniquely attached to that `target_node`, but can initialize any number of additional members required to keep track of actions and responses and such.

`Soul`'s will recieve `GraphEvent`'s to observe in calls to `observe_event`. These calls will be launched in the current asyncio event loop by `wrap_observe_event`, and can be seen in the `_observe_futures` property. They are launched in the background to allow the soul to respond to the event whenever they'd like, without blocking the main thread.

When a `Soul`'s time is up, either due to the `GraphAgent` being removed from the graph, or due to a disconnect, or a human inhabiting an agent filled by a model, the `reap` method will be called. This method should clean up any resources, and set any required flags such that any remaining `_observe_futures` will exit without taking additional action. It doesn't need to wait for them to exit before returning, but the default implementation calls `cancel` on outstanding futures.

## Important Flags

Some `Soul`'s set flags on `GraphAgent`'s to be able to be interpreted by other `Soul`'s or elements of the world. These generally should be prepended with an `_` such that they don't get compressed into the saved formats.

Current flags:
- `is_player`: Set by `PlayerSoul` to designate `GraphAgent`'s that are inhabited by a real player. Used by the world to ensure we don't doubly assign a `GraphAgent` to two different players, and by `ModelSoul`'s to differentiate between inter-model chat and chat with a human.

## Current Souls:
- [**`Soul`**](https://github.com/facebookresearch/LIGHT/tree/main/light/world/souls/soul.py): Abstract class defining the minimum API for an agent-attached interaction layer into a LIGHT world.
- [**`BaseSoul`**](https://github.com/facebookresearch/LIGHT/tree/main/light/world/souls/base_soul.py): Extension on the basic `Soul` class including various helpers and state that are useful for both player and model-based interactions.
- [**`ModelSoul`**](https://github.com/facebookresearch/LIGHT/tree/main/light/world/souls/model_soul.py): Basic `Soul` that is defines an interface where models can be loaded in and used as agents.
- [**`OnEventSoul`**](https://github.com/facebookresearch/LIGHT/tree/main/light/world/souls/on_event_soul.py): Extended `ModelSoul` class that is able to handle some basic scripted heuristic events as well as the more general `on_event` types that can be linked to a `GraphNode`.
- [**`PlayerSoul`**](https://github.com/facebookresearch/LIGHT/tree/main/light/world/souls/player_soul.py): Simple `Soul` class that allows for a human player to take control of the `GraphAgent`. Requires use of a `PlayerProvider` containing the abstractions for sending observations and receiving actions.
- [**`RepeatSoul`**](https://github.com/facebookresearch/LIGHT/tree/main/light/world/souls/repeat_soul.py): Bare-bones `Soul` class for use in demonstrations. Simply speaks back the observations it sees with a `SayEvent`.
- [**`TestSoul`**](https://github.com/facebookresearch/LIGHT/tree/main/light/world/souls/test_soul.py): Core soul for being able to run tests on the LIGHT `World` classes. Has a directly accessible `observations` field and a `do_act` function allowing scripted execution of actions.
