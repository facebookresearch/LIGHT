/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import { Utils } from "@blueprintjs/core";
import React, {useState, useEffect} from "react";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import { updateRooms} from "../../../../features/rooms/rooms-slice.ts";
/* STYLES */
import "./styles.css"
/* CUSTOM COMPONENTS */

/* UTILS */

const TilePath = ({
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
    const pathClickHandler = ()=>{
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
        <div
            onClick={pathClickHandler}
            className={`path-container ${alignment} ${active ?  "active": "" }`}
        />
    )
}
export default TilePath;