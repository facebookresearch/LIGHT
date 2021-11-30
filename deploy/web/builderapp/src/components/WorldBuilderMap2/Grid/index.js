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
import Tile from "../Tile";

const SIZE = 150;
const MARGIN = 24;

const Grid = ({
    gridData,
    borders,
    xOffset,
    yOffset
})=>{
    //REACT ROUTER
    const history = useHistory();
    let { worldId } = useParams();
    //let { path, url } = useRouteMatch();
    /* REDUX DISPATCH FUNCTION */
    const dispatch = useAppDispatch();
    /* ------ REDUX STATE ------ */
    //ROOMS
    const worldRooms = useAppSelector((state) => state.worldRooms.worldRooms);
    /* REDUX ACTIONS */
  
    /* ------ LOCAL STATE ------ */
    const [gridRows, setGridRows] = useState([]);
    const [gridWidth, setGridWidth] = useState(0);
    const [gridHeight, setGridHeight] = useState(0);
    
    /* REACT LIFECYCLE */
    useEffect(()=>{
        let {rows} = gridData
        let columns = rows[0]
        setGridRows(rows)
        let rowCount = rows.length;
        let columnCount = columns.length;
        console.log("ROW AND COLUMN COUNTS", rowCount , columnCount)
        let height = rowCount * 200;
        let width = columnCount * 250;
        console.log("HEIGHT AND WIDTH", height , width)
        setGridWidth(width);
        setGridHeight(height);
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
                gridRows.map((row, index)=>(
                    <Row 
                        key={borders.top-index}
                        data={row}
                        borders={borders}  
                    />
                ))
                :
                null
            }
        </div>
    )
}
export default Grid;