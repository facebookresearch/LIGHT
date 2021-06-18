import React, {useEffect, useState, useRef} from "react";

import "./styles.css"

//CUSTOM COMPONENT
import InfoToolTip from "../../InfoToolTip";


const FormQuestion = ({question, placeholder, questionColor, upperCaseQuestion, formVal, formFunction})=>{
    const [description, setDescription] = useState("")
    useEffect(()=>{
        setDescription(formVal)
    },[])
    const changeHandler = e=>{
        e.preventDefault()
        setDescription(e.target.value)
        formFunction(description)
    }
    return(
        <div className="form-container" >
            <InfoToolTip tutorialCopy={"TESTING TESTING 123"}>
                <h1 className="form-header" style={{color: (questionColor ?  questionColor : "black")}}>
                    {upperCaseQuestion ? question.toUpperCase() : question}
                </h1>
            </InfoToolTip>
        <p >

        </p>
        <div className="answer-container">
            <textarea
                className="answer-form"
                onChange={changeHandler}
                value={description}
                rows="7"
                type="text"
            />
        </div>
        </div>
    )
}
export default FormQuestion;
