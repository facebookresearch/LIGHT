//REACT
import React, {useState} from "react";
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import Scale from "./Scale";
import ScaleQuestionHeader from "./ScaleQuestionHeader"

const ScaleQuestion = ({
    selection,
    scale,
    trait
})=>{

    return(
        <div className="scalequestion-container">
            <ScaleQuestionHeader
                trait={trait.name}
                traitDescription={trait.description}
            />
            <Scale
                scale={scale}
                selection={selection}
            />
        </div>
    )
}
export default ScaleQuestion;
