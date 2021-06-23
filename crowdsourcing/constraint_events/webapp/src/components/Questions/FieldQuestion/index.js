import React, {useEffect, useRef} from "react";

import "./styles.css"

//CUSTOM COMPONENTS
import FieldRow from "./FieldRow";

const FieldQuestion = ({
    question,
    fields,
    formFunction,
    formState
})=>{
    const ChangeHandler = (formName, formVal)=>{
        let updatedState = {...formState, [formName]:formVal}
        console.log("UPDATE", updatedState)
        formFunction(updatedState)
    }
    return(
        <div className="fieldquestion-container" >
            <p className="fieldquestion-header">{question}</p>
            <div className="fieldlist-container">
                {
                    fields ?
                    fields.map((field, index)=>(
                    <FieldRow
                        key={index}
                        field={field}
                        dropdown={field.dropdown}
                        options={field.options}
                        changeFunction={val=>ChangeHandler(field.name, val)}
                        formState={formState}
                        />
                        ))
                    :null
                }
            </div>
        </div>
    )
}
export default FieldQuestion;
