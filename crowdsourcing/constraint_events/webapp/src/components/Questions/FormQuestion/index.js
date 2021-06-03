import React, {useEffect, useRef} from "react";

import "./styles.css"


const FormQuestion = ({question, placeholder, formVal, formFunction})=>{
    const changeHandler = e=>{
        e.preventDefault()
        //formFunction(e.target.value)

    }
    return(
        <div className="form-container" >
            <h1 className="form-header">
                {question}
            </h1>
        <p >

        </p>
            <textarea
                className="answer-form"
                onChange={changeHandler}
                value={formVal}
                rows="7"
                type="text"
                placeholder={placeholder}
            />
        </div>
    )
}
export default FormQuestion;
