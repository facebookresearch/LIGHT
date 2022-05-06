# light

Contains the core LIGHT game engine and data model. Includes the `OOGraph` data model, descriptions of all of the node types, actions and manipulations on the graph (`GraphEvent`s), and the abstract API (`Soul`s) for creating agents that can act in LIGHT.

**Subdirectories:**
- **`modeling`**: A directory of code for agents and teachers that can be trained to work in LIGHT.
- **`data_model`**: Classes that represent LIGHT data in _cold storage_, absent of a specific LIGHT world. At the moment this is mostly centralized in the `LIGHTDatabase`, which uses SQLite storage, but given new data types and systems this is definitely subject to change.
- **`graph`**: Classes that represent a LIGHT Graph (the state of a LIGHT world), the elements inside, builders to create a new Graph, events that modify Graphs, and related tooling.
- **`registry`**: Classes that allow registering LIGHT models to an active LIGHT world, allowing them to interact and fill certain decisions in the LIGHT setup. Currently in development as we transition models out from being initialized at their usage locations.
- **`world`**: Contains all the higher-level code that is required to run an _active_ LIGHT graph, including processing agent actions into events, executing them on the graph, and handling logging.
