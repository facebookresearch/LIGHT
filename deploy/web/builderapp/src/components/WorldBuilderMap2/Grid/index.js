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
    borders
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
    const [gridRows, setGridRows] = useState([])
    
    


    /* REACT LIFECYCLE */
    useEffect(()=>{
        let {rows} = gridData
        setGridRows(rows)
    },[gridData])

    return(
        <div className="grid-container">
            {
                gridRows.length
                ?
                gridRows.map(row=>(
                    <Row 
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