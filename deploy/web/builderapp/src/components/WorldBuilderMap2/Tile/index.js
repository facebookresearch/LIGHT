/* REACT */
import React, {useState, useEffect} from "react";
/* STYLES */
import "./styles.css"
/* CUSTOM COMPONENTS */
import TilePath from "./TilePath"
/* UTILS */


const Tile = ({
    data,
    borders
})=> {
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
  return (
    <div className="tile-area">
        <div className="tile-row top">
            <div style={{width:"25%", backgroundColor:"green"}}/>
            {
                yBorderChecker() 
                ?
                <div className={`ypath-container`}>
                    <TilePath
                        data={data}
                        alignment="vertical"
                    />
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
                    <TilePath
                        data={data}
                        alignment="horizontal"
                    />
                </div>
                :
                <div  className="xpath-container"/>
            }
            <div
                className="tile-container"
            >
            {data.name ? data.name : ""}
        </div>
        </div>
    </div>
  );
}

export default Tile;