# Builders

Core folder containing the LIGHT `GraphBuilder` classes. A `GraphBuilder` is used to directly construct or modify a LIGHT `OOGraph` in a controllable way. The core types are the `GraphBuilder` and the `SingleSuggestionGraphBuilder`. The former exposes an API where you can simply create a graph or add agents to it (to fill for dying agents). The latter provides an abstract API for a graph builder that can later be used to make suggestions for modifications to the graph.

**Contents:**
- **`base.py`**: Underlying base `GraphBuilder` class definitions.
- **`base_elements.py`**: Utility classes representing the contents retrieved from the `LIGHTDatabase` as would be useful for a `GraphBuilder`.
- **`db_utils.py`**: Utility classes to access graph-construction-related content from a `LIGHTDatabase`.
- **`external_map_json_builder.py`**: Graph builder using a _deprecated_ format (from an early world builder tool) to load a graph directly from that json format.
- **`one_room_builder.py`**: Graph builder that creates a single room and populates it with the desired number of characters. Often used to create dialogue tasks.
- **`starspace_all.py`**, **`starspace_assisted.py`**, and **`starspace_neighbor.py`**: Various starspace-based graph builders that use a `starspace` model to make large graphs from knowledge on local connections. Nearly deprecated by Commonsense-based agents, and will likely be deprecated once a `GraphBuilder` is created from them.
- **`user_world_builder.py`**: Creates a LIGHT Graph based on contents saved in the `LIGHTDatabase` for a given user. Likely to be deprecated when we start saving the new world format.
