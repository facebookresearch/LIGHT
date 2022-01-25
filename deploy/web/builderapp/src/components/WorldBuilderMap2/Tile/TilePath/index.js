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
    tileData,
    alignment,
    neighbors,
    neighboringTile,
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
        let tileNeighbors = Object.keys(neighbors)
        tileNeighbors.map((neighborId)=>{
            if(neighborId===neighboringTile.node_id){
                setActive(true)
            }
        })
    } ,[neighbors, neighboringTileNeighbors])
    /* HANDLERS */
    const pathClickHandler = ()=>{
        console.log("TILE DATA", tileData, neighboringTile)
        console.log("NEIGHBORS", neighbors)
        console.log("NEIGHBORTILENEIGHBORS", neighboringTileNeighbors)
        
        if(active){
            console.log("DISCONNECTING ROOMS")
            disconnectRooms(tileData, neighbors, neighboringTile, neighboringTileNeighbors, alignment)
            // let updatedRoomNode = tileData;
            // let updatedNeighbors = {...neighbors};
            // delete updatedNeighbors[neighboringTile.node_id];
            // updatedRoomNode ={...tileData, neighbors: updatedNeighbors};

            // let updatedNeighborNode = neighboringTile;
            // let updatedNeighboringTileNeighbors = {...neighboringTileNeighbors};
            // delete updatedNeighboringTileNeighbors[neighboringTile.node_id];
            // updatedNeighborNode ={...updatedNeighborNode, neighbors: updatedNeighboringTileNeighbors};

            // gridUpdateFunction(updatedRoomNode.node_id, updatedRoomNode);
            // gridUpdateFunction(updatedNeighborNode.node_id, updatedNeighborNode);
            
        }else{
            console.log("CONNECTING ROOMS")
            connectRooms(tileData, neighbors, neighboringTile, neighboringTileNeighbors, alignment)

            // let updatedRoomNode = tileData;
            // let updatedNeighbors = neighbors;
            // let neighborInfo = {
            //     examine_desc: null,
            //     label: `a path to ${alignment==="vertical" ? "the south": "the east"}`,
            //     locked_edge: null,
            //     target_id: neighboringTile.node_id
            // };
            // updatedNeighbors = {...neighbors, [neighboringTile.node_id]:neighborInfo};
            // updatedRoomNode = {...tileData, neighbors:updatedNeighbors};
                    
            // let updatedNeighborNode = neighboringTile;
            // let updatedNeighboringTileNeighbors = neighboringTileNeighbors;
            // let neighboringTileNeighborInfo = {
            //     examine_desc: null,
            //     label: `a path to ${alignment==="vertical" ? "the north": "the west"}`,
            //     locked_edge: null,
            //     target_id: tileData.node_id
            // };
            // updatedNeighboringTileNeighbors = {...neighboringTileNeighborInfo, [tileData.node_id]: neighboringTileNeighborInfo};
            // updatedNeighborNode = {...neighboringTile, neighbors:updatedNeighboringTileNeighbors};
            // gridUpdateFunction(updatedRoomNode.node_id, updatedRoomNode);
            // gridUpdateFunction(updatedNeighborNode.node_id, updatedNeighborNode);
            
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