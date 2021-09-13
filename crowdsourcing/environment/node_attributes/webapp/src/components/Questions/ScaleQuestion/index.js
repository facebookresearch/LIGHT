//REACT
import React, {useState} from "react";
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import Scale from "./Scale";
import ScaleQuestionHeader from "./ScaleQuestionHeader"
//COPY
import TaskCopy from "../../../TaskCopy"
const {customAttributeQuestionToolTip} = TaskCopy
// ScaleQuestion - form that allows worker to rate an attribute of a selection.
// On a scale from lowest to highest the worker can place a "flag" on where they believe the selections falls on the scale.
const ScaleQuestion = ({
    selection,//The values that will be rated
    scaleRange,// An array of ranges to divide the scale into sections.
    trait,
    isCustom,
    updateFunction,
})=>{
    const {name, description, toolTip} = trait;

    return(
        <div className="scalequestion-container">
            <ScaleQuestionHeader
                isCustom={isCustom}
                trait={name}
                traitDescription={description}
                updateFunction={(fieldName, updateValue)=>updateFunction(fieldName,  "none", updateValue)}
                toolTip={isCustom ? customAttributeQuestionToolTip : toolTip}
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