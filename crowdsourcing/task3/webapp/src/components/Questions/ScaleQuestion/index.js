import React, {useState} from "react";

import "./styles.css"
//CUSTOM COMPONENTS
import Scale from "./Scale";
import ScaleHeader from "./ScaleHeader"

const ScaleQuestion = ({
    actors,
    scale,
    trait
})=>{

    return(
        <div className="scalequestion-container">
            <ScaleHeader
                trait={trait.name}
                traitDescription={trait.description}
            />
            <Scale
                scale={scale}
                actors={actors}
            />
        </div>
    )
}
export default ScaleQuestion;
