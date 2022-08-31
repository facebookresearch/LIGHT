/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React, {useState} from "react";
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import Scale from "./Scale";
import ScaleQuestionHeader from "./ScaleQuestionHeader"

// ScaleQuestion - form that allows worker to rate an attribute of a selection.
// On a scale from lowest to highest the worker can place a "flag" on where they believe the selections falls on the scale.
const ScaleQuestion = ({
    selection,//The values that will be rated
    scaleRange,// An array of ranges to divide the scale into sections.
    trait,
    isCustom,
    updateFunction,
})=>{
    const {name, description} = trait;

    return(
        <div className="scalequestion-container">
            <ScaleQuestionHeader
                isCustom={isCustom}
                trait={name}
                traitDescription={description}
                updateFunction={(fieldName, updateValue)=>updateFunction(fieldName,  "none", updateValue)}
            />
            <Scale
                scaleRange={scaleRange}
                selection={selection}
                dragFunction={isCustom ? ( updateKey, updateValue)=>updateFunction("vals", updateKey, updateValue): updateFunction}
            />
        </div>
    )
}
export default ScaleQuestion;
