/* REACT */
import React, {useState, useEffect} from "react";
/* STYLES */
import "./styles.css"
/* CUSTOM COMPONENTS */
import TilePath from "./TilePath"
/* UTILS */


const Tile = ({
    tileData,
    borders,
    tileClickFunction,
    leftNeighbor,
    topNeighbor,
    gridUpdateFunction
})=> {
    /* ------ LOCAL STATE ------ */
    const [hasLeftPath, setHasLeftPath] = useState(false)
    const [hasTopPath, setHasTopPath] = useState(false)

    /* ------ LIFE CYCLE ------ */
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
                            neighboringTile={topNeighbor}
                            neighboringTileNeighbors={topNeighbor.neighbors}
                            gridUpdateFunction={gridUpdateFunction}
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
                        neighboringTile={leftNeighbor}
                        neighboringTileNeighbors={leftNeighbor.neighbors}
                    />
                    :
                    null
                    }
                </div>
                :
                <div  className="xpath-container"/>
            }
            <div
                className="tile-container"
                onClick={handleTileClick}
            >
            {tileData.name ? tileData.name : ""}
        </div>
        </div>
    </div>
  );
}

export default Tile;