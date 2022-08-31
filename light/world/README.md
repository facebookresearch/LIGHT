# LIGHT World

The LIGHT World operates on a level above the LIGHT Graph, and it is responsible for maintaining track of agents within the world, listening to their actions, parsing them, and executing them on the underlying graph. While this directory contains other classes, the core unifying principle is that they operate on top of a live `OOGraph`.

## World

The world class itself is a wrapper around an `OOGraph` that keeps track of session-dependent attributes and provides helpful functions for interacting on a graph live. It delegates some of this responsiblity to the `Purgatory`, `WorldViewer` classes described below. This section covers an overview on other core functionality. Additional functionality of the `World` has been deprecated and marked as such.

### Parsing Text to `GraphEvent`s
The `World`'s parsing methods are responsible for executing the construction methods for a `GraphEvent` in the correct order, and handling errors properly along the way. This is handled by the `parse_exec` function, which extracts the target `GraphEvent` type and uses `attempt_parse_event` to try and create the event if it's valid.

The `World` is also able to determine all possible `GraphEvent`s for an agent with `get_possible_events`.

### Broadcasting executed events
Once an event is executed on a LIGHT graph, it's the `World`'s responsiblity to ensure that expected listeners (including loggers) are able to observe what just occurred. These responsibilities are handled with the `broadcast_to_room`, `broadcast_to_agents`, and `broadcast_to_all_agents` methods. These ultimately rely on `send_action` and `send_msg` to direct the observations to the correct `Soul`s.

### Removing corpses
One issue with a text world, especially one where characters can die in, is that eventually it becomes filled with corpses if they aren't removed. The LIGHT `World` takes up this responsibility with `clean_corpses_and_respawn`, ensuring that nodes can be removed and replaced with new characters as death inevitably occurs.

## Content Loggers

`content_loggers` attach to `player_souls` and `rooms`, and are used to log events which take place with a human/player.  The important opts to use when building a graph for loggers are

    - `log_path`, which specifies the top level directory to write logs

    - `is_logging`, which determines wether loggers should be recording events or not

Files ending in `event.log` record a meta episode from the POV of the room or agent (depending on where the log was attached).  Such log files have the following structure, where each pair of three lines is a new event:

    graph_uuid event_hash
    timestamp
    event_to_json

All event logs are in the `log_path/light_event_dumps` directory.  The graph_uuid references a graph in the `log_path/light_graph_dumps` directory

## Subdirectories
- **`souls`**: Directory containing `Soul`s, which are used as the layer allowing models or players to assume the role of a `GraphAgent` and observe and interact within a LIGHT `World`.
- **`tests`**: Testing to ensure that the `World` is functional.
- **`utils`**: Utility classes for `World`-related code.

## Other Classes:
- [**`PlayerProvider`**](https://github.com/facebookresearch/LIGHT/tree/main/light/world/player_provider.py): Abstraction defining required functions for a human agent to be able to interact within LIGHT.
- [**`Purgatory`**](https://github.com/facebookresearch/LIGHT/tree/main/light/world/purgatory.py): `Purgatory` is responsible for managing `Soul`'s. It should be created as a member of a `World` when the world is created. Whatever created that world can then register souls to fill up the `World`'s agents by using `register_filler_soul_provider` and `fill_soul`.
- [**`WorldViewer`**](https://github.com/facebookresearch/LIGHT/tree/main/light/world/quest_loader.py): Class used to load in saved 'motivations' and quests for characters, as well as to generate new ones after one has been completed.
- [**`QuestLoader`**](https://github.com/facebookresearch/LIGHT/tree/main/light/world/views.py): Baseline implementation of a class defining how contents of the world should _look_ to an observer. May be overwritten for special cases.
