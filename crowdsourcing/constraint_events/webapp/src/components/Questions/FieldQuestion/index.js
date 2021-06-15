import React, {useEffect, useRef} from "react";

import "./styles.css"

//CUSTOM COMPONENTS
import FieldRow from "./FieldRow";

const FieldQuestion = ({question, fields})=>{
    const answerRef = useRef();
    return(
        <div className="fieldquestion-container" >
            <p className="fieldquestion-header">{question}</p>
            <div className="fieldlist-container">
                {
                    fields ?
                    fields.map((field, index)=><FieldRow key={index} field={field.name.toUpperCase()} dropdown={field.dropdown} options={field.options} />)
                    :null
                }
            </div>
        </div>
    )
}
export default FieldQuestion;
