
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React, {useEffect, useState, useRef} from "react";
//KONVA
import { Stage, Layer, Line, RegularPolygon} from 'react-konva';
//STYLING
import "./styles.css";
//CUSTOM COMPONENTS
import ScaleFooter from "./ScaleFooter";
import ScaleField from "./ScaleField";
//Utils;
import GetWindowDimensions from "../../../../utils/GetWindowDimensions.js";

//Scale - Component that contains actual scale UI for ScaleQuestion component.  Allows user to drag and drop name plates on a range that will supply rating to the backend.
const Scale = ({
    scaleRange,
    selection,
    dragFunction
}) => {
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
                    selection={selection}
                    scaleRange={scaleRange}
                    dragFunction={dragFunction}
                />
            </Stage>
            <ScaleFooter scaleRange={scaleRange} />
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
