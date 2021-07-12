//REACT
import React, {useEffect, useState} from "react";
//KONVA
import { Stage, Layer, Line} from 'react-konva';
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import ScaleRange from "./ScaleRange"
import OptionBlock from "./OptionBlock"
//Utils
import GetWindowDimensions from "../../../../utils/GetDimensions.js"
//Scale - Component that contains actual scale UI for ScaleQuestion component.  Allows user to drag and drop name plates on a range that will supply rating to the backend.
const Scale = ({trait, actors}) => {
    const [dimensions, setDimensions]= useState(GetWindowDimensions())
    useEffect(()=>{
        const handleResize = ()=>{
            setDimensions(GetWindowDimensions())
        }
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, [])
    const {width, height}= dimensions
    return (
        <div className="scale-container">
            <div style={{width:"100%", height:"50%" }}>
                <div style={{width:"260px", backgroundColor:"white"}}>
                    <p style={{textAlign:"center", borderColor:"blue", borderWidth: "3px", borderStyle:"solid", padding:"2px", fontWeight:"bold", color:"blue"}}>
                        ACTORS
                    </p>
                </div>
                <div >
                    <Stage width={width} height={height/2}>
                        <Layer>
                            <OptionBlock
                                width={width}
                                height={height/4}
                                actors={actors}
                            />
                            <Line closed points={[100, 0, 100, -100, 0, 0]} fill="red" />
                        </Layer>
                    </Stage>
                    <ScaleRange trait={trait} />
                </div>
            </div>
        </div>
    );
};

export default Scale;
