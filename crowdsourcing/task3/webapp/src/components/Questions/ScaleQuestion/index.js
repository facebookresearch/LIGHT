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
    trait
})=>{
    const {name, description} = trait;
    return(
        <div className="scalequestion-container">
            <ScaleQuestionHeader
                trait={name}
                traitDescription={description}
            />
            <Scale
                scaleRange={scaleRange}
                selection={selection}
            />
        </div>
    )
}
export default ScaleQuestion;
