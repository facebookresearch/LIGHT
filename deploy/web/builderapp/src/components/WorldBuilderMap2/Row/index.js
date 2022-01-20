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
    rowData, 
    borders,
    tileClickFunction,
    connectRooms,
    disconnectRooms
})=>{
    /* ------ LOCAL STATE ------ */
    const [data, setData] = useState([])

    /* --- LIFE CYCLE FUNCTIONS --- */
    useEffect(()=>{
        setData(rowData)
    }, [rowData])
    return (
        <div
            className="row-container"
        >
            {
                data.length
                ?
                data.map((tileData, index)=>{
                    let leftTileData= data[index-1];
                    let isLeftTile = leftTileData ? true: false;
                    let topTileData= previousRowData[index];
                    let isTopTile = topTileData ? true: false;
                    return(
                        <Tile 
                            key={index}
                            tileData={tileData}
                            borders={borders}
                            tileClickFunction={tileClickFunction}
                            leftNeighbor={leftTileData}
                            topNeighbor={topTileData}
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