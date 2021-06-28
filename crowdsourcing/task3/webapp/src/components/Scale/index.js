//REACT
import React, {useState} from "react";
//KONVA
import { Stage, Layer, Line} from 'react-konva';
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import ScaleRange from "./ScaleRange"
import OptionBlock from "./OptionBlock"

const Scale = ({trait, actors}) => {

  return (
    <div style={{width:"100%", height:"50%" }}>
        <div style={{width:"260px", backgroundColor:"white"}}>
            <p style={{textAlign:"center", borderColor:"blue", borderWidth: "3px", borderStyle:"solid", padding:"2px", fontWeight:"bold", color:"blue"}}>
                ACTORS
            </p>
        </div>
        <Stage width={window.innerWidth} height={window.innerHeight/2}>
            <Layer>
                <OptionBlock
                    width={window.innerWidth}
                    height={window.innerHeight/4}
                    actors={actors}
                />
                <Line closed points={[100, 0, 100, -100, 0, 0]} fill="red" />
            </Layer>
        </Stage>
        <ScaleRange trait={trait} />
    </div>
  );
};

export default Scale;
