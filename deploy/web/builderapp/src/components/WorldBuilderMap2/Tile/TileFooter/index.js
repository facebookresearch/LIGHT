
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, {useState, useEffect} from "react";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import TileStair from "./TileStair";
/* UTILS */

const TileStairs = ({
    tileData,
    aboveNeighbor,
    belowNeighbor,
    connectRooms,
    disconnectRooms
})=>{
    /* ------ REDUX STATE ------ */
    //ROOMS
    const worldRooms = useAppSelector((state) => state.worldRooms.worldRooms);
    /* ------ REDUX ACTIONS ------ */
    /* ------ LOCAL STATE ------ */
    const [hasAboveNeighbor, setHasAboveNeighbor] = useState(false)
    const [hasBelowNeighbor, setHasBelowNeighbor] = useState(false)

    /* REACT LIFECYCLE */
    useEffect(()=>{
        if(aboveNeighbor){
            let updatedHasAboveNeighbor = (aboveNeighbor.node_id && tileData.node_id) ? true : false;
            setHasAboveNeighbor(updatedHasAboveNeighbor)
        }
    },[aboveNeighbor, tileData])

    useEffect(()=>{
        if(belowNeighbor){
            let updatedHasBelowNeighbor = (belowNeighbor.node_id && tileData.node_id) ? true : false;
            setHasBelowNeighbor(updatedHasBelowNeighbor)
        }
    },[belowNeighbor, tileData])

    /* HANDLERS */


    return(
        <div className="tile-footer">
            <span>
            {
                hasBelowNeighbor
                ?
                <TileStair
                    alignment={"below"}
                    tileData={tileData}
                    neighbors={tileData.neighbors}
                    neighboringTileData={belowNeighbor}
                    neighboringTileNeighbors={belowNeighbor.neighbors}
                    connectRooms={connectRooms}
                    disconnectRooms={disconnectRooms}
                />
                :
                <span/>
            }
            </span>
            <span>
            {
                hasAboveNeighbor
                ?
                <TileStair
                    alignment={"above"}
                    tileData={tileData}
                    neighbors={tileData.neighbors}
                    neighboringTileData={aboveNeighbor}
                    neighboringTileNeighbors={aboveNeighbor.neighbors}
                    connectRooms={connectRooms}
                    disconnectRooms={disconnectRooms}
                />
                :
                <span/>
            }
            </span>
        </div>
    )
}
export default TileStairs;