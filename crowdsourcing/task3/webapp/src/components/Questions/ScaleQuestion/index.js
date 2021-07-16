//REACT
import React, {useState} from "react";
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import Scale from "./Scale";
import ScaleQuestionHeader from "./ScaleQuestionHeader"

const ScaleQuestion = ({
    selection,
    scaleRange,
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
