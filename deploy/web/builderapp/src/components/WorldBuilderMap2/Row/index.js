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
    borders,
    tileClickFunction
})=>{
    /* ------ LOCAL STATE ------ */
    const [rowData, setRowData] = useState([])

    /* --- LIFE CYCLE FUNCTIONS --- */
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
                rowData.map((tileData, index)=>(
                    <Tile 
                        key={index}
                        data={tileData}
                        borders={borders}
                        tileClickFunction={tileClickFunction}
                    />
                ))
                :
                null
            }
        </div>
    );
}

export default Row;