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
const Scale = ({scale, actors}) => {
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
            <div style={{width:"100%", height:"100%" }}>
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
                <div >
                    <Stage width={width} height={height/2}>
                        <Layer width={width}>
                        <Line
                            points={[width*.25, 0, width*.25, height]}
                            stroke={"blue"}
                            strokeWidth={5}
                        />
                            <OptionBlock
                                width={width*.9}
                                height={height/2}
                                actors={actors}
                            />
                            <Line closed points={[100, 0, 100, -100, 0, 0]} fill="red" />
                        </Layer>
                    </Stage>
                    <ScaleRange actorBlockMargin={"260px"} scale={scale} />
                </div>
            </div>
        </div>
    );
};

export default Scale;
