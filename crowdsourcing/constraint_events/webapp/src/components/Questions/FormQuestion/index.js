//REACT
import React, {useEffect, useState, useRef} from "react";
//STYLES
import "./styles.css"

//CUSTOM COMPONENT
import InfoToolTip from "../../InfoToolTip";
import Checkbox from "../../Checkbox";

const FormQuestion = ({
    question,
    placeholder,
    questionColor,
    upperCaseQuestion,
    formVal,
    formFunction,
    toolTipCopy,
    hasToolTip,
    isComplete
})=>{
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
            {
            hasToolTip
            ?
            <InfoToolTip
            tutorialCopy={toolTipCopy}
            >
                <div style={{display:"flex", flexDirection:"row"}}>
                    <Checkbox isComplete={isComplete} />
                    <h1 className="form-header" style={{color: (questionColor ?  questionColor : "black")}}>
                        {upperCaseQuestion ? question.toUpperCase() : question}
                    </h1>
                </div>
            </InfoToolTip>
            :
            <h1 className="form-header" style={{color: (questionColor ?  questionColor : "black")}}>
                {upperCaseQuestion ? question.toUpperCase() : question}
            </h1>
            }
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
