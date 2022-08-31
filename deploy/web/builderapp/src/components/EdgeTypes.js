
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

// File containing map of edge types to strings, see
// light/data_model/light_database.py for matching onese
export const EDGE_TYPES = {
  NEIGHBORS_WEST: "neighbors to the west",
  NEIGHBORS_EAST: "neighbors to the east",
  NEIGHBORS_NORTH: "neighbors to the north",
  NEIGHBORS_SOUTH: "neighbors to the south",
  NEIGHBORS_ABOVE: "neighbors above",
  NEIGHBORS_BELOW: "neighbors below",
  CONTAINS: "contains",
};
