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
    tileClickFunction
})=>{
    /* ------ LOCAL STATE ------ */
    const [data, setData] = useState([])

    /* --- LIFE CYCLE FUNCTIONS --- */
    useEffect(()=>{
        setData(rowData)
    }, rowData)
    return (
        <div
            className="row-container"
        >
            {
                data.length
                ?
                data.map((tileData, index)=>{
                    let leftTile = data[index-1] ? data[index-1]: false;
                    let topTile = previousRowData ? previousRowData[index] : false

                    return(
                        <Tile 
                            key={index}
                            data={tileData}
                            borders={borders}
                            tileClickFunction={tileClickFunction}
                            leftNeighbor={leftTile}
                            topNeighbor={topTile}
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