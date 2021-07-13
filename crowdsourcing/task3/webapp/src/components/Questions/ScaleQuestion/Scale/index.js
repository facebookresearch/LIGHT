//REACT
import React, {useEffect, useState} from "react";
//KONVA
import { Stage, Layer, Line, RegularPolygon} from 'react-konva';
//STYLING
import "./styles.css";
//CUSTOM COMPONENTS
import ScaleRange from "./ScaleRange";
import OptionBlock from "./OptionBlock";
import ScaleFlag from "./ScaleFlag";
//Utils;
import GetWindowDimensions from "../../../../utils/GetDimensions.js";

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
                        <Layer width={(width*.89)+5}>
                        <Line
                            points={[width*.252, 0, width*.253, height]}
                            stroke={"blue"}
                            strokeWidth={5}
                        />
                            <OptionBlock
                                width={width*.89}
                                height={height/2}
                                actors={actors}
                                boundary={(width*.165)}
                            />
                            {
                            scale.map((label, index)=>{
                                let xOffset =(width*.27)
                                let xPosition = ((width*.23)*index) +xOffset
                                return(
                                    <ScaleFlag
                                        key={index}
                                        xPosition={xPosition}
                                        yPosition={200}
                                        width={width}
                                        height={height}
                                        label={label}
                                        color={index}
                                    />
                                )}
                            )
                            }
                            <Line
                                x={width*.253}
                                y={height/2}
                                points={[0, 0, width, 0, width, height*-.15]}
                                tension={0}
                                closed
                                stroke="black"
                                fillLinearGradientStartPoint={{ x: 0, y: 0 }}
                                fillLinearGradientEndPoint={{ x: width*.13, y: height*-.075 }}
                                fillLinearGradientStartPoint={{ x: width*.13, y: height*-.075 }}
                                fillLinearGradientEndPoint={{ x: width*.6, y: height*-.15 }}
                                fillLinearGradientColorStops={[0, 'green', 0.3, "blue", 1, 'red']}
                            />
                        </Layer>
                    </Stage>
                    <ScaleRange scale={scale} />
                </div>
            </div>
        </div>
    );
};

export default Scale;
