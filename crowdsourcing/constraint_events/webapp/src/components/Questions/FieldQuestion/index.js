import React, {useEffect, useRef} from "react";



const FieldQuestion = ({field})=>{
    const answerRef = useRef();
    const changeHandler = e=>{
        e.preventDefault()

    }
    return(
        <div className="form-container" >
            <div className="field-container">
                <p className="field-text">
                    {field}
                </p>
            </div>
            <div className="answer-container">
                <input
                    className="answer-text"
                    ref={answerRef}
                />
            </div>
        </div>
    )
}
export default FormQuestion;
