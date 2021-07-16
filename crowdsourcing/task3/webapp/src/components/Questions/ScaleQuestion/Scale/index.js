//REACT
import React, {useEffect, useState} from "react";
//KONVA
import { Stage, Layer, Line, RegularPolygon} from 'react-konva';
//STYLING
import "./styles.css";
//CUSTOM COMPONENTS
import ScaleRange from "./ScaleRange";
import ScaleField from "./ScaleField";
//Utils;
import GetWindowDimensions from "../../../../utils/GetWindowDimensions.js";

//Scale - Component that contains actual scale UI for ScaleQuestion component.  Allows user to drag and drop name plates on a range that will supply rating to the backend.
const Scale = ({scale, actors}) => {
    const [dimensions, setDimensions]= useState(GetWindowDimensions())
    useEffect(()=>{
        const handleResize = ()=>{
            console.log("RESIZE WORKING")
            setDimensions(GetWindowDimensions())
        }
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, [])
    const {width, height}= dimensions
    return (
        <div className="scale-container">
            <Stage width={width} height={height/2}>
                <ScaleField
                    width={width}
                    height={height/2}
                    actors={actors}
                    scale={scale}
                />
            </Stage>
            <ScaleRange scale={scale} />
        </div>
    );
};

export default Scale;

{/* <div style={{width:"100%", height:"100%" }}>
<div className="scalelabels-container">
    <div className="optionblock-label__container">
        <p className="optionblock-label__text">
            ACTORS
        </p>
    </div>
    <div className="scalefield-label__container">
        <p className="scalefield-label__text">
            Scale
        </p>
    </div>
</div>
<div > */}
