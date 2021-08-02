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
    traitDescription,
    isCustom,
    updateFunction,
})=>{
    const {name, description} = trait;
    return(
        <div className="scalequestion-container">
            <ScaleQuestionHeader
                isCustom={isCustom}
                trait={name}
                traitDescription={traitDescription}
                updateFunction={( updateKey, updateValue)=>updateFunction(name,  updateKey, updateValue)}
            />
            <Scale
                scaleRange={scaleRange}
                selection={selection}
                dragFunction={isCustom ? ( updateValue)=>updateFunction(name,name, updateValue): updateFunction}
            />
        </div>
    )
}
export default ScaleQuestion;
