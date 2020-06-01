import React from "react";
import { Popover, Icon, Tooltip } from "@blueprintjs/core";
import { isEmpty, cloneDeep } from "lodash";

import TileForm from "../forms/TileForm";
import { invertColor } from "./utils";

/**
 * Component for each Tile in the map grid
 */
function Tile({
  x,
  y,
  tile,
  selected,
  setSelected,
  showAdvanced,
  setShowAdvanced,
  tileStyle,
  state
}) {
  const handleSubmit = data => {
    state.setTile(x, y, { ...tile, ...data });
    setSelected(null);
  };

  const handleClear = () => {
    state.clearTile(x, y);
    setSelected(null);
  };

  // toggle stairs on the tile clicked, and this tile and on the other floor
  const toggleStairs = (event, key) => {
    event.stopPropagation(); // prevent the popup firing
    const toggleTo = !tile[key];
    const newTile = cloneDeep(tile);
    newTile[key] = toggleTo;
    state.setTile(x, y, newTile);
    const otherFloor = state.currFloor + (key === "stairDown" ? -1 : 1);
    const newConnectedTile = cloneDeep(state.getTileAt(x, y, otherFloor));
    newConnectedTile[key === "stairDown" ? "stairUp" : "stairDown"] = toggleTo;
    state.setTile(x, y, newConnectedTile, otherFloor);
  };

  const contentColor = invertColor(
    tile && !isNaN(tile.room) && tile.color ? tile.color : "#ced9e0"
  );

  return (
    <>
      <Icon
        color={contentColor}
        className={`react-grid-item-handle + ${
          isEmpty(tile) ? "disabled" : ""
        }`}
        icon="drag-handle-horizontal"
      />
      {!isEmpty(state.getTileAt(x, y, state.currFloor - 1)) && (
        <Icon
          color={contentColor}
          onClick={
            !isEmpty(tile) ? e => toggleStairs(e, "stairDown") : undefined
          }
          className={isEmpty(tile) ? "disabled" : ""}
          style={{
            opacity: !isEmpty(tile) && tile.stairDown ? 1 : 0.35,
            position: "absolute",
            bottom: "5px",
            left: "5px"
          }}
          icon="arrow-bottom-left"
        />
      )}
      {!isEmpty(state.getTileAt(x, y, state.currFloor + 1)) && (
        <Icon
          color={contentColor}
          onClick={!isEmpty(tile) ? e => toggleStairs(e, "stairUp") : undefined}
          className={isEmpty(tile) ? "disabled" : ""}
          style={{
            opacity: !isEmpty(tile) && tile.stairUp ? 1 : 0.35,
            position: "absolute",
            top: "5px",
            right: "5px"
          }}
          icon="arrow-top-right"
        />
      )}
      <Popover
        isOpen={
          !!selected && selected.x === x && selected.y === y && !showAdvanced
        }
        onClose={() => {
          if (!showAdvanced) {
            setSelected(null);
          }
        }}
        usePortal={true}
      >
        {/* Popover target */}
        <div
          className="react-grid-item-content"
          style={{
            ...tileStyle,
            backgroundColor: tile && tile.color ? tile.color : ""
          }}
        >
          <div
            className="center"
            style={{
              color: contentColor,
              width: "100%",
              maxHeight: tileStyle.maxHeight - 20,
              overflow: "hidden"
            }}
          >
            <p>{!isEmpty(tile) ? state.entities.room[tile.room].name : ""}</p>
            <p>
              {!isEmpty(tile)
                ? tile.characters.map(char => (
                    <Tooltip content={state.entities.character[char].name}>
                      {state.entities.character[char].emoji}
                    </Tooltip>
                  ))
                : ""}
            </p>
            <p>
              {!isEmpty(tile)
                ? tile.objects.map(obj => (
                    <Tooltip content={state.entities.object[obj].name}>
                      {state.entities.object[obj].emoji}
                    </Tooltip>
                  ))
                : ""}
            </p>
          </div>
        </div>
        {/* Popover content */}
        <div style={{ padding: "20px" }}>
          <TileForm
            initialInputs={tile}
            onSubmit={handleSubmit}
            onClear={handleClear}
            entities={state.entities}
            findOrAddEntity={state.findOrAddEntity}
            setSelected={setSelected}
            selected={selected}
            setShowAdvanced={setShowAdvanced}
          />
        </div>
      </Popover>
    </>
  );
}

export default Tile;
