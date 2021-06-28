//REACT
import React, {useState} from "react";
//KONVA
import { Stage, Layer} from 'react-konva';
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import OptionBlock from "./OptionBlock"

const Scale = ({trait, actors}) => {

  return (
    <div style={{width:"100%", height:"25%", backgroundColor:"green"}}>
        <Stage width={window.innerWidth} height={window.innerHeight/4}>
            <Layer>
                <OptionBlock
                    width={window.innerWidth}
                    height={window.innerHeight/4}
                    actors={actors}
                />
            </Layer>
        </Stage>
        <div style={{width:"75%", height:"25%", backgroundColor:"yellow"}}>
                SCALE
        </div>
    </div>
  );
};

export default Scale;
