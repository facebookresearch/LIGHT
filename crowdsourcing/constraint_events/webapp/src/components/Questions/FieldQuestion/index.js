import React, {useEffect, useRef} from "react";

import "./styles.css"

//CUSTOM COMPONENTS
import FieldRow from "./FieldRow";

const FieldQuestion = ({question, fields})=>{
    const answerRef = useRef();
    return(
        <div className="question-container" >
            <p className="question-header">{question}</p>
            <div className="fieldlist-container">
                {
                    fields ?
                    fields.map((field, index)=><FieldRow key={index} field={field.toUpperCase()} />)
                    :null
                }
            </div>
        </div>
    )
}
export default FieldQuestion;
