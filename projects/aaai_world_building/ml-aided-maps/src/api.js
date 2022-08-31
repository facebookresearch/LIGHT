/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

var getUrl = window.location;
var URL = "https://arcane-beyond-12630.herokuapp.com";
// const URL = "https://www.mocky.io/v2/5d64601632000075a5ba2047";

function augmentState(state, draft) {
  const { selectedTile, location, characters, objects } = draft;
  if (!selectedTile) {
    return state;
  }
  state = state.map((row, rowIdx) =>
    row.map((tile, colIdx) => {
      if (rowIdx === selectedTile[0] && colIdx === selectedTile[1]) {
        return {
          location: location,
          chars: characters,
          objs: objects
        };
      } else {
        return tile;
      }
    })
  );

  return state;
}

export function useMLSuggestions(state, connections, enabled = true, draft) {
  const [suggestions, setSuggestions] = React.useState([]);

  state = augmentState(state, draft);

  const roomsUrl = JSON.stringify(
    state.map(row => row.map(tile => tile.location && tile.location.id))
  );

  connections = convertConnections(connections);
  const connectionsUrl = JSON.stringify(connections);

  React.useEffect(() => {
    if (!enabled) return;
    fetch(URL + "/query?state=" + roomsUrl + "&connections=" + connectionsUrl)
      .then(res => res.json())
      .then(res => {
        setSuggestions(res.suggestions);
      });
  }, [roomsUrl, connectionsUrl, enabled]);
  return suggestions;
}

export function convertConnections(connections) {
  connections = connections.map(([row, col, orientation]) => {
    if (orientation === "h") {
      return 3 + row * 5 + col;
    } else {
      return 1 + row * 5 + col;
    }
  });

  connections = new Array(12).fill(1).map((_, idx) => {
    if (connections.indexOf(idx + 1) >= 0) {
      return 1;
    } else {
      return 0;
    }
  });
  return connections;
}

export function submit(state, connections, title, timeToFinish) {
  const payload = {
    state: state.map(row =>
      row.map(tile => ({
        ...tile,
        location: tile.location && tile.location.id
      }))
    ),
    connections: convertConnections(connections),
    title: title,
    timeToFinishSeconds: timeToFinish
  };
  return fetch(URL + "/submit", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
