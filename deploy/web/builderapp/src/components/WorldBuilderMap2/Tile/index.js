
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, {useState, useEffect} from "react";
/* STYLES */
import "./styles.css"
/* CUSTOM COMPONENTS */
import TilePath from "./TilePath";
import TileFooter from "./TileFooter";
/* ICONS */
import { Gi3DStairs } from "react-icons/gi";
import { BsArrowDownShort, BsArrowUpShort } from "react-icons/bs";
/* UTILS */


const Tile = ({
    tileData,
    borders,
    tileClickFunction,
    leftNeighbor,
    topNeighbor,
    aboveNeighbor,
    belowNeighbor,
    connectRooms,
    disconnectRooms
})=> {
    /* ------ LOCAL STATE ------ */
    const [tileContentNodes, setTileContentNodes] = useState([])
    const [hasLeftPath, setHasLeftPath] = useState(false)
    const [hasTopPath, setHasTopPath] = useState(false)
    const [hasAboveNeighbor, setHasAboveNeighbor] = useState(false)
    const [hasBelowNeighbor, setHasBelowNeighbor] = useState(false)

    /* ------ LIFE CYCLE ------ */

    useEffect(()=>{
        let updatedTileContent =[]
        if(tileData.node_id){
            const {contained_nodes}= tileData;
            const tileContentNodeKeys = Object.keys(contained_nodes)
            updatedTileContent = [...tileContentNodeKeys]
            if(updatedTileContent.length){
                setTileContentNodes(updatedTileContent);
            }else{
                setTileContentNodes([])
            }
        }
    },[tileData])

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
    
    useEffect(()=>{
        if(leftNeighbor){
            let updatedHasLeftPath = (leftNeighbor.node_id && tileData.node_id) ? true : false;
            setHasLeftPath(updatedHasLeftPath)
        }
    },[leftNeighbor, tileData])

    useEffect(()=>{
        if(topNeighbor){
            let updatedHasTopPath = (topNeighbor.node_id && tileData.node_id) ? true : false;
            setHasTopPath(updatedHasTopPath)
        }
    },[topNeighbor, tileData])

    /* ------ UTILS ------ */
    const xBorderChecker = () =>{
        const {grid_location} = tileData;
        let xPosition = grid_location[0];
        let LeftBorder = borders.left;
        if(LeftBorder < xPosition){
            return true;
        }
        else {
            return false;
        }
    }
    const yBorderChecker = () =>{
        const {grid_location} = tileData
        let yPosition = grid_location[1]
        let TopBorder = borders.top;
        if(TopBorder > yPosition){
            return true;
        }
        else {
            return false;
        }
    }

    //HANDLERS
    const handleTileClick = ()=>{
        console.log("TILE DATA", tileData)
        tileClickFunction(tileData)
    }
  return (
    <div className="tile-area">
        <div className="tile-row top">
            <div style={{width:"25%"}}/>
            {
                yBorderChecker() 
                ?
                <div className={`ypath-container`}>
                    {
                        hasTopPath
                        ?
                        <TilePath
                            tileData={tileData}
                            alignment="vertical"
                            neighbors={tileData.neighbors}
                            neighboringTileData={topNeighbor}
                            neighboringTileNeighbors={topNeighbor.neighbors}
                            connectRooms={connectRooms}
                            disconnectRooms={disconnectRooms}
                        />
                        :
                        null
                    }
                </div>
                :
                null
            }
        </div>
        <div className="tile-row bottom">
            {
                xBorderChecker() 
                ?
                <div  className="xpath-container">
                    {
                    hasLeftPath
                    ?
                    <TilePath
                        tileData={tileData}
                        alignment="horizontal"
                        neighbors={tileData.neighbors}
                        neighboringTileData={leftNeighbor}
                        neighboringTileNeighbors={leftNeighbor.neighbors}
                        connectRooms={connectRooms}
                        disconnectRooms={disconnectRooms}
                    />
                    :
                    null
                    }
                </div>
                :
                <div  className="xpath-container"/>
            }
            <div
                style={{backgroundColor: (tileData.color ? tileData.color: "white")}}
                className="tile-container"
                onClick={handleTileClick}
            >
                {
                tileData.node_id
                ?
                <>
                    <div className="tile-label">
                        <p>{tileData.name ? tileData.name.toUpperCase() : ""}</p>
                    </div>
                    <div className="tile-body">
                        {
                            tileContentNodes.length
                            ?
                            <ul className="tile-content__list">
                                {
                                    tileContentNodes.map(node => {
                                        let formattedNode = node.replaceAll("_", " ")
                                        return (
                                            <li key={node} className="tile-content__list--item">
                                                {formattedNode.toUpperCase()}
                                            </li>
                                        )
                                    })
                                }
                            </ul>
                            :null
                        }
                    </div>
                        {
                            (hasAboveNeighbor || hasBelowNeighbor)
                            ?
                              <TileFooter 
                                tileData={tileData}
                                aboveNeighbor={aboveNeighbor}
                                belowNeighbor={belowNeighbor}
                                connectRooms={connectRooms}
                                disconnectRooms={disconnectRooms}
                              />
                            :
                            null
                            }
                </>
                :null
            }
            </div>

        </div>
    </div>
  );
}

export default Tile;