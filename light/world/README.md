# LIGHT World

The LIGHT World operates on a level above the LIGHT Graph, and it is responsible for maintaining track of agents within the world, listening to their actions, parsing them, and executing them on the underlying graph.

## Purgatory

`Purgatory` is responsible for managing `Soul`'s. It should be created as a member of a `World` when the world is created. Whatever created that world can then register souls to fill up the `World`'s agents by using `register_filler_soul_provider` and `fill_soul`.

## Content Loggers

`content_loggers` attach to `player_souls` and `rooms`, and are used to log events which take place with a human/player.  The important opts to use when building a graph for loggers are

    - `log_path`, which specifies the top level directory to write logs

    - `is_logging`, which determines wether loggers should be recording events or not

Files ending in `event.log` record a meta episode from the POV of the room or agent (depending on where the log was attached).  Such log files have the following structure, where each pair of two lines is a new event:

    graph_uuid event_hash timestamp
    event_to_json

All event logs are in the `log_path/light_event_dumps` directory.  The graph_uuid references a graph in the `log_path/light_graph_dumps` directory
