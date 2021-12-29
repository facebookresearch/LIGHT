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

        let updatedRooms
        if(active){
            updatedRooms = worldRooms.map((roomNode, index)=>{
                let updatedRoomNode = roomNode;
                if(roomNode.node_id == tileData.node_id){
                    let updatedNeighbors = {...neighbors};
                    delete updatedNeighbors[neighboringTile.node_id];
                    updatedRoomNode ={...roomNode, neighbors: updatedNeighbors};
                }
                if(roomNode.node_id == neighboringTile.node_id){
                    let updatedNeighboringTileNeighbors = {...neighboringTileNeighbors};
                    delete updatedNeighboringTileNeighbors[neighboringTile.node_id];
                    updatedRoomNode ={...roomNode, neighbors: updatedNeighboringTileNeighbors};

                }
                return updatedRoomNode
            })
            updateRooms(updatedRooms)
            setActive(false)
        }else{
            updatedRooms = worldRooms.map((roomNode, index)=>{
                let updatedRoomNode = roomNode;
                if(roomNode.node_id == tileData.node_id){
                    let updatedNeighbors = neighbors;
                    let neighborInfo = {
                        examine_desc: null,
                        label: `a path to ${alignment==="vertical" ? "the south": "the east"}`,
                        locked_edge: null,
                        target_id: neighboringTile.node_id
                    }
                    updatedNeighbors = {...neighbors, [neighboringTile.node_id]:neighborInfo};
                    updatedRoomNode = {...roomNode, neighbors:updatedNeighbors};
                }
                if(roomNode.node_id == neighboringTile.node_id){
                    let updatedNeighboringTileNeighbors = neighboringTileNeighbors;
                    let neighboringTileNeighborInfo = {
                        examine_desc: null,
                        label: `a path to ${alignment==="vertical" ? "the north": "the west"}`,
                        locked_edge: null,
                        target_id: tileData.node_id
                    }
                    updatedNeighboringTileNeighbors = {...neighboringTileNeighborInfo, [tileData.node_id]: neighboringTileNeighborInfo};
                    updatedRoomNode = {...roomNode, neighbors:updatedNeighboringTileNeighbors};
                }
                return updatedRoomNode
            })
            console.log(updatedRooms)
            updateRooms(updatedRooms)
            setActive(true)
        }
    }

    let pathClickHandler2 = ()=>{
        
    }

    return(
        <div
            onClick={pathClickHandler}
            className={`path-container ${alignment} ${active ?  "active": "" }`}
        />
    )
}
export default TilePath;