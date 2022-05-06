/* REACT */
import { Utils } from "@blueprintjs/core";
import React, {useState, useEffect} from "react";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../../../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import { updateRooms} from "../../../../../../features/rooms/rooms-slice.ts";
/* STYLES */
import "./styles.css"
/* CUSTOM COMPONENTS */

/* ICONS */
import { Gi3DStairs } from "react-icons/gi";
import { BsArrowDownShort, BsArrowUpShort } from "react-icons/bs";
/* UTILS */

const TileStair = ({
    alignment,
    tileData,
    neighbors,
    neighboringTileData,
    neighboringTileNeighbors,
    connectRooms,
    disconnectRooms
})=>{
    /* ------ REDUX STATE ------ */
    //ROOMS
    const worldRooms = useAppSelector((state) => state.worldRooms.worldRooms);
    /* ------ REDUX ACTIONS ------ */
    /* ------ LOCAL STATE ------ */
    const [active, setActive] = useState(false);

    /* REACT LIFECYCLE */
    useEffect(()=>{
        console.log("UPDATE INCOMIING")
        let tileNeighbors = Object.keys(neighbors)
        if(tileNeighbors.indexOf(neighboringTileData.node_id)<0){
            setActive(false)
        } else {
            setActive(true)
        }
    } ,[tileData])
    /* HANDLERS */
    const stairClickHandler = ()=>{
        console.log("IN PATH TILE DATA", tileData)
        console.log("IN PATH NEIGHBORS", neighbors)
        console.log("IN PATH NEIGHBORING TILE DATA", neighboringTileData)
        console.log("IN PATH NEIGHBORTILENEIGHBORS", neighboringTileNeighbors)
        if(active){
            console.log("DISCONNECTING ROOMS")
            disconnectRooms(tileData, neighbors, neighboringTileData, neighboringTileNeighbors, alignment)
        }else{
            console.log("CONNECTING ROOMS")
            connectRooms(tileData, neighbors, neighboringTileData, neighboringTileNeighbors, alignment)
        }
    }


    return(
        <>
            {(alignment=="below") ? <BsArrowDownShort size="16"/> : <BsArrowUpShort size="16"/> }
            <Gi3DStairs size="16" color={active ? "black" : "lightgrey"} onClick={stairClickHandler}/>
        </>
)
}
export default TileStair;
