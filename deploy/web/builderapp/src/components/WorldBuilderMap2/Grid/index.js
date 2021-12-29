/* REACT */
import React, {useState, useEffect} from "react";
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import { fetchWorlds, selectWorld } from "../../../features/playerWorlds/playerworlds-slice.ts";
/* STYLES */
import "./styles.css"
/* CUSTOM COMPONENTS */
import Row from "../Row"


const Grid = ({
    gridData,
    gridUpdateFunction,
    borders,
    xOffset,
    yOffset,
    tileClickFunction
})=>{
  
    /* ------ LOCAL STATE ------ */
    const [gridRows, setGridRows] = useState([]);
    const [gridWidth, setGridWidth] = useState(0);
    const [gridHeight, setGridHeight] = useState(0);
    
    /* REACT LIFECYCLE */
    useEffect(()=>{
       
        console.log("GRID DATA:  ", gridData)
        let {rows} = gridData;
        if(rows.length){
            let columns = rows[0];
            setGridRows(rows);
            let rowCount = rows.length;
            let columnCount = columns.length;
            console.log("ROW AND COLUMN COUNTS", rowCount , columnCount);
            let height = rowCount * 250;
            let width = columnCount * 250;
            console.log("HEIGHT AND WIDTH", height , width);
            setGridWidth(width);
            setGridHeight(height);
        }
    },[gridData])

    return(
        <div 
            style={{
                left:xOffset, 
                top:yOffset,
                width: gridWidth,
                height: gridHeight,
            }} 
            className="grid-container"
        >
            {
                gridRows.length
                ?
                gridRows.map((row, index)=>{
                    let previousRowData= gridRows[index-1] ? gridRows[index-1]:[]
                    return(
                        <Row 
                            key={borders.top-index}
                            previousRowData={previousRowData}
                            rowData={row}
                            borders={borders}
                            gridUpdateFunction={gridUpdateFunction}
                            tileClickFunction={tileClickFunction}
                        />
                    )}
                )
                :
                null
            }
        </div>
    )
}
export default Grid;