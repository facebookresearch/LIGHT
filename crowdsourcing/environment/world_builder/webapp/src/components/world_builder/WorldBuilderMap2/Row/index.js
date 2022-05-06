/* REACT */
import React, {useState, useEffect} from "react";
import { Popover, Icon, Tooltip } from "@blueprintjs/core";
import { isEmpty, cloneDeep } from "lodash";
/* STYLES */
import "./styles.css"
/* CUSTOM COMPONENTS */
import Tile from "../Tile"
/* UTILS */
import { invertColor } from "../Utils";

const Row = ({
    previousRowData,
    aboveRowData,
    belowRowData,
    rowData,
    borders,
    tileClickFunction,
    connectRooms,
    disconnectRooms
})=>{
    /* ------ LOCAL STATE ------ */

    /* --- LIFE CYCLE FUNCTIONS --- */

    return (
        <div
            className="row-container"
        >
            {
                rowData.length
                ?
                rowData.map((tileData, index)=>{
                    let leftTileData= rowData[index-1];
                    let topTileData= previousRowData[index];
                    let aboveTileData= aboveRowData[index];
                    let belowTileData= belowRowData[index];
                    return(
                        <Tile
                            key={index}
                            tileData={tileData}
                            borders={borders}
                            tileClickFunction={tileClickFunction}
                            leftNeighbor={leftTileData}
                            topNeighbor={topTileData}
                            aboveNeighbor={aboveTileData}
                            belowNeighbor={belowTileData}
                            connectRooms={connectRooms}
                            disconnectRooms={disconnectRooms}
                        />
                    )}
                )
                :
                null
            }
        </div>
    );
}

export default Row;
