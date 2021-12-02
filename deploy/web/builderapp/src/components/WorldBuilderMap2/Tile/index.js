/* REACT */
import React, {useState, useEffect} from "react";
/* STYLES */
import "./styles.css"
/* CUSTOM COMPONENTS */
import TilePath from "./TilePath"
/* UTILS */


const Tile = ({
    data,
    borders,
    tileClickFunction,
    leftNeighbor,
    topNeighbor
})=> {
    /* ------ LOCAL STATE ------ */
    const [hasLeftPath, setHasLeftPath] = useState(false)
    const [hasTopPath, setHasTopPath] = useState(false)

    /* ------ LIFE CYCLE ------ */
    useEffect(()=>{
        if(leftNeighbor){
            let updatedHasLeftPath = leftNeighbor.node_id ? true : false;
            setHasLeftPath(updatedHasLeftPath)
        }
    },[leftNeighbor])

    useEffect(()=>{
        if(topNeighbor){
            let updatedHasTopPath = topNeighbor.node_id ? true : false;
            setHasTopPath(updatedHasTopPath)
        }
    },[topNeighbor])

    /* ------ UTILS ------ */
    const xBorderChecker = () =>{
        const {grid_location} = data;
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
        const {grid_location} = data
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
        console.log("TILE DATA", data)
        tileClickFunction(data)
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
                            data={data}
                            alignment="vertical"
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
                        data={data}
                        alignment="horizontal"
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
            {data.name ? data.name : ""}
        </div>
        </div>
    </div>
  );
}

export default Tile;