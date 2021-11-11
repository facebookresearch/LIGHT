import React from "react";
import { Popover, Icon, Tooltip } from "@blueprintjs/core";
import { isEmpty, cloneDeep } from "lodash";

import { invertColor } from "../Utils";

/**
 * Component for each Tile in the map grid
 */
function Tile({
  x,
  y,
  tile,
  tileStyle,
  state,
}) {

  return (
    <>
      <Icon
        className={`react-grid-item-handle`}
        icon="drag-handle-horizontal"
      />
        <Icon
    
          style={{
            position: "absolute",
            bottom: "5px",
            left: "5px",
          }}
          icon="arrow-bottom-left"
        />
        <Icon
          style={{
            position: "absolute",
            top: "5px",
            right: "5px",
          }}
          icon="arrow-top-right"
        />
      {/*
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
            <div
            className="react-grid-item-content"
            style={{
                ...tileStyle,
                backgroundColor: tile && tile.color ? tile.color : "",
            }}
            >
                <div
                    className="center"
                    style={{
                    color: contentColor,
                    width: "100%",
                    maxHeight: tileStyle.maxHeight - 20,
                    overflow: "hidden",
                    }}
                >
                    <p>{!isEmpty(tile) ? state.entities.room[tile.room].name : ""}</p>
                    <p>
                    {!isEmpty(tile)
                        ? tile.characters.map((char) => (
                            <Tooltip content={state.entities.character[char].name}>
                            {state.entities.character[char].emoji}
                            </Tooltip>
                        ))
                        : ""}
                    </p>
                    <p>
                    {!isEmpty(tile)
                        ? tile.objects.map((obj) => (
                            <Tooltip content={state.entities.object[obj].name}>
                            {state.entities.object[obj].emoji}
                            </Tooltip>
                        ))
                        : ""}
                    </p>
                </div>
            </div>
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
                neighbor={neighbor}
            />
            </div>
        </Popover>
        */}
    </>
  );
}

export default Tile;