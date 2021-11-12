import React from "react";
import { Popover, Icon, Tooltip } from "@blueprintjs/core";
import { isEmpty, cloneDeep } from "lodash";

import { invertColor } from "../Utils";

/**
 * Component for each Tile in the map grid
 */
function Tile({
    tile,
    tileStyle,
    xPosition,
    yPosition,
    tileData
}) {
    console.log("TILE DATA", tileData)
  return (
    <div
    >
      {tileData.name ? tileData.name : ""}
      {xPosition}
      {yPosition}
  </div>
  );
}

export default Tile;