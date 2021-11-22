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
    data, 
    borders
})=>{
    const [rowData, setRowData] = useState([])
    console.log("ROW", data)
    useEffect(()=>{
        setRowData(data)
    }, data)
    return (
        <div
            className="row-container"
        >
            {
                rowData.length
                ?
                rowData.map((tileData)=>(
                    <Tile 
                        data={tileData}
                        borders={borders}
                    />
                ))
                :
                null
            }
        </div>
    );
}

export default Row;