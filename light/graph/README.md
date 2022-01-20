# LIGHT Graph

The LIGHT graph is the core state of the environment over which LIGHT takes place. This folder contains the components for managing, building, and operating on Graphs.

## The LIGHT `OOGraph`

TODO define the format, structure, and functionality of the core LIGHT graph format.

## Subdirectories
- **`builders`**: `GraphBuilder`s are utility classes used to create and extend `OOGraph`s with content.
- **`elements`**: `GraphNode`s are the the contents of a graph, and comprise the information stored within.
- **`events`**: `GraphEvent`s define the types of operations and manipulations that can be performed on an `OOGraph`.
- **`tests`**: Some testing to ensure that the graph is acting as expected.
- **`viz`**: Visualization tooling that allows inspection of an `OOGraph`.
