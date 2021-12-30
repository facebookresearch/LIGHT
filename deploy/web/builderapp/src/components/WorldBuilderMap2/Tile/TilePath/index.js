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
    gridUpdateFunction
})=>{
    /* ------ REDUX STATE ------ */
    //ROOMS
    const worldRooms = useAppSelector((state) => state.worldRooms.worldRooms);
    /* ------ REDUX ACTIONS ------ */

    const dispatch = useAppDispatch();

    const updateRooms = (update) => dispatch(updateRooms(update))
    ;
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
    } ,[tileData])
    /* HANDLERS */
    const pathClickHandler = ()=>{
        if(active){

            let updatedRoomNode = tileData;
            let updatedNeighbors = {...neighbors};
            delete updatedNeighbors[neighboringTile.node_id];
            updatedRoomNode ={...tileData, neighbors: updatedNeighbors};

            let updatedNeighborNode = neighboringTile;
            let updatedNeighboringTileNeighbors = {...neighboringTileNeighbors};
            delete updatedNeighboringTileNeighbors[neighboringTile.node_id];
            updatedNeighborNode ={...updatedNeighborNode, neighbors: updatedNeighboringTileNeighbors};

            gridUpdateFunction(updatedRoomNode.node_id, updatedRoomNode);
            gridUpdateFunction(updatedNeighborNode.node_id, updatedNeighborNode);
            setActive(false);
        }else{
            let updatedRoomNode = tileData;
            let updatedNeighbors = neighbors;
            let neighborInfo = {
                examine_desc: null,
                label: `a path to ${alignment==="vertical" ? "the south": "the east"}`,
                locked_edge: null,
                target_id: neighboringTile.node_id
            };
            updatedNeighbors = {...neighbors, [neighboringTile.node_id]:neighborInfo};
            updatedRoomNode = {...tileData, neighbors:updatedNeighbors};
                    
            let updatedNeighborNode = neighboringTile;
            let updatedNeighboringTileNeighbors = neighboringTileNeighbors;
            let neighboringTileNeighborInfo = {
                examine_desc: null,
                label: `a path to ${alignment==="vertical" ? "the north": "the west"}`,
                locked_edge: null,
                target_id: tileData.node_id
            };
            updatedNeighboringTileNeighbors = {...neighboringTileNeighborInfo, [tileData.node_id]: neighboringTileNeighborInfo};
            updatedNeighborNode = {...neighboringTile, neighbors:updatedNeighboringTileNeighbors};
            gridUpdateFunction(updatedRoomNode.node_id, updatedRoomNode);
            gridUpdateFunction(updatedNeighborNode.node_id, updatedNeighborNode);
            setActive(true);
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