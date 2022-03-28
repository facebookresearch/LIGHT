//REACT
import React, {useEffect, useState} from "react";
//STYLES
import "./styles.css"
//CUSTOM COMPONENT
import InfoToolTip from "../../InfoToolTip";
import Checkbox from "../../Checkbox";

//FormQuestion - a question who's answer is gathered from simple text input
const FormQuestion = ({
    question,//Actual text of question
    placeholder,// Placeholder if needed
    questionColor, //Text color
    upperCaseQuestion, // boolean that makes question entirely uppercase
    formVal,// Initial form value
    formFunction,// setState function that connects answer to payload state
    toolTipCopy,// Text that will appear in tooltip
    hasToolTip,// boolean that adds tooltip icon and text if true
    isComplete// completion condition
})=>{
    /*------STATE------*/
    const [description, setDescription] = useState("")
     /*------LIFECYCLE------*/
    //Sets initial value on render
    /*------HANDLERS------*/
    //Updates both local and payload state with answer
    const changeHandler = e=>{
        e.preventDefault()
        setDescription(e.target.value)
        formFunction(e.target.value)
    }
    return(
        <div className="form-container" >
            <InfoToolTip
            tutorialCopy={toolTipCopy}
            hasToolTip={hasToolTip}
            >
                <div style={{display:"flex", flexDirection:"row"}}>
                    {hasToolTip ? <Checkbox isComplete={isComplete} />:null}
                    <h1 className="form-header" style={{color: (questionColor ?  questionColor : "black")}}>
                        {upperCaseQuestion ? question.toUpperCase() : question}
                    </h1>
                </div>
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
                placeholder={placeholder}
            />
        </div>
        </div>
    )
}
export default FormQuestion;
