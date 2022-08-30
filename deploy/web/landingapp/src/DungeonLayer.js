/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { withLeaflet, GridLayer } from "react-leaflet";
import L from "leaflet";

class Grid extends GridLayer {
  createLeafletElement(opts) {
    const Grid = L.GridLayer.extend({
      createTile: (coords) => {
        // console.log(coords);
        // if (coords.x % 3 === 0) return null;
        console.log(coords);
        const rand = Math.floor(Math.random() * 3);
        const locationIdx = rand * 2;
        const colorIdx = locationIdx + 1;
        const info = [
          "Dungeon",
          "navajowhite",
          "Castle",
          "#ddd",
          "Pasture",
          "#daf5b1",
        ];

        const tile = document.createElement("div");
        tile.style.outline = "1px solid black";
        tile.innerHTML = info[locationIdx];
        tile.style.backgroundColor = info[colorIdx];
        tile.style.display = "flex";
        tile.style.alignItems = "center";
        tile.style.justifyContent = "center";
        return tile;
      },
    });
    return new Grid({ tileSize: 100 });
  }

  componentDidMount() {
    const { map } = this.props.leaflet;
    this.leafletElement.addTo(map);
  }
}

export default withLeaflet(Grid);
