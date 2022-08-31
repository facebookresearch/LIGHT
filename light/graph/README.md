# LIGHT Graph

The LIGHT graph is the core state of the environment over which LIGHT takes place. This folder contains the components for managing, building, and operating on Graphs.

## The LIGHT `OOGraph`

Generally, the LIGHT `OOGraph` is constructed of `GraphNode`s and `GraphEdge`s. Nodes contained in or containing other nodes use the `GraphEdge` class. We use a special `NeighborEdge` class to note the connections between rooms, as these may have additional attributes. All of the contents of a graph should be json-serializable, so you can see a JSON representation of a simple graph [here](https://github.com/facebookresearch/LIGHT/tree/main/scripts/examples/simple_world.json).

### Special Conditions
Beyond the basic structure of nodes and edges, the `OOGraph` keeps track of a few special considerations.

#### The Void
As all nodes must have a container, we create a special `GraphVoidNode` which is the default continer for all nodes. When creating a node, all nodes are initially created in the void, and can later be moved to their correct containers with `move_to` functions. Room nodes generally will remain in the void.

#### Deletion Lifecycles
Node deletion is somewhat tricky in LIGHT, as it's possible that an action leads to the deletion of a node that, in the same timestep, needs to be used for a description, log, or otherwise. For this, we can instead mark a node for deletion with `mark_node_for_deletion` and later use `delete_nodes` to clear these. Further, even when a node is deleted, we still maintain a reference to it in `_deleted_nodes` for logging purposes. (This may eventually be removed for memory usage reasons)

#### Agent Death
Death in the LIGHT world, in a base sense, is the transition from a node being a `GraphAgent` that can be inhabited by a `Soul` to a `GraphNode`. As of now this transition is managed by the _to be deprecated_ `agent_die` function, which makes an object copy of the agent, transfers over the contents to the copy, and then delete the agent node. These special post-death nodes are tracked in the `dead_nodes` array.

#### Node searching
It is important in many cases (especially parsing) to try and find nodes that match a specific description in the graph. Accessors of this type are bundled in the `desc_to_nodes` function, which can either search the whole graph or can use a `nearby_node` and `nearbytype` to search with a specific strategy.

`nearbytype` is a string of `+` separated options, having the following effects:
- `'all'`: include the contents of `nearby_node`, its parent, and its parent's neighbors.
- `'sameloc'`: searches over all nodes sharing the same parent container as `nearby_node`.
- `'carrying'`: searches over all nodes contained by `nearby_node`.
- `'path'`: searches over rooms attached to the container of `nearby_node`.
- `'contains'`: includes the container of `nearby_node`.
- `'other_agents'`: includes nodes carried by agents in the same **room** as `nearby_node`.
- `'others'`: extend search to recursively include anything contained in the search list already.

#### Nodes vs IDs
Some functions in the `OOGraph` still refer to using a node's `node_id` rather than using the reference to the `node` directly. In general, this access pattern is deprecated, but remaining usage tends to very clearly note whether an access is getting a `GraphNode` or is `node_id`. To convert `node_id` to `GraphNode`, you can use `OOGraph.get_node(node_id)`. To get a node's id, you can just use `GraphNode.node_id`.

## Subdirectories
- **`builders`**: `GraphBuilder`s are utility classes used to create and extend `OOGraph`s with content.
- **`elements`**: `GraphNode`s are the the contents of a graph, and comprise the information stored within.
- **`events`**: `GraphEvent`s define the types of operations and manipulations that can be performed on an `OOGraph`.
- **`tests`**: Some testing to ensure that the graph is acting as expected.
- **`viz`**: Visualization tooling that allows inspection of an `OOGraph`.
