/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, {useState, useEffect} from "react";
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import { fetchWorlds, selectWorld } from "../../../../features/playerWorlds/playerworlds-slice.ts";
/* STYLES */
import "./styles.css"
/* CUSTOM COMPONENTS */
import Row from "../Row"
import { GiConsoleController } from "react-icons/gi";


const Grid = ({
    gridData,
    borders,
    xOffset,
    yOffset,
    tileClickFunction,
    connectRooms,
    disconnectRooms
})=>{

    /* ------ LOCAL STATE ------ */
    //ROWS
    const [gridRows, setGridRows] = useState([]);
    const [gridBelowRows, setGridBelowRows] = useState([]);
    const [gridAboveRows, setGridAboveRows] = useState([]);
    //DIMENSIONS
    const [gridWidth, setGridWidth] = useState(0);
    const [gridHeight, setGridHeight] = useState(0);

    /* REACT LIFECYCLE */
    useEffect(()=>{
        let {floors} = gridData;
        //ROWS
        let belowFloorRows = floors[0];
        let currentFloorRows = floors[1]
        let aboveFloorRows = floors[2]
        if(currentFloorRows.length){
            let columns = currentFloorRows[0];
            setGridRows(currentFloorRows);
            let rowCount = currentFloorRows.length;
            let columnCount = columns.length;
            let height = rowCount * 250;
            let width = columnCount * 250;
            setGridWidth(width);
            setGridHeight(height);
        }
        if(belowFloorRows.length){
            setGridBelowRows(belowFloorRows)
        }
        if(aboveFloorRows.length){
            setGridAboveRows(aboveFloorRows)
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
                            aboveRowData= {gridAboveRows[index]}
                            belowRowData= {gridBelowRows[index]}
                            rowData={row}
                            borders={borders}
                            tileClickFunction={tileClickFunction}
                            connectRooms={connectRooms}
                            disconnectRooms={disconnectRooms}
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
