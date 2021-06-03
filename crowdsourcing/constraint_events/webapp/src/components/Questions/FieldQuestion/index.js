import React, {useEffect, useRef} from "react";

import "./styles.css"

//CUSTOM COMPONENTS
import FieldRow from "./FieldRow";

const FieldQuestion = ({question, fields})=>{
    const answerRef = useRef();
    return(
        <div className="form-container" >
            <p className="form-header">{question}</p>
            {
                fields ?
                fields.map((field, index)=><FieldRow key={index} field={field} />)
                :null
            }
        </div>
    )
}
export default FieldQuestion;
