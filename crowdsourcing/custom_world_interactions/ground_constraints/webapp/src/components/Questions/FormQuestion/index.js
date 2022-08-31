//REACT
import React, { useEffect, useState } from "react";
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
    isComplete,// completion condition
    disabled // whether this form question has been disabled (completed by previous task)
}) => {
    /*------STATE------*/
    const [description, setDescription] = useState("")
    /*------LIFECYCLE------*/
    //Sets initial value on render
    useEffect(() => {
        setDescription(formVal)
    }, [])
    /*------HANDLERS------*/
    //Updates both local and payload state with answer
    const changeHandler = e => {
        e.preventDefault()
        setDescription(e.target.value)
        formFunction(e.target.value)
    }
    return (
        <div className="form-container" >
            <InfoToolTip
                tutorialCopy={toolTipCopy}
                hasToolTip={hasToolTip}
            >
                <div style={{ display: "flex", flexDirection: "row" }}>
                    {/* {hasToolTip ? <Checkbox isComplete={isComplete} />:null} */}
                    <h1 className="form-header" style={{ color: (questionColor ? questionColor : "black") }}>
                        {upperCaseQuestion ? question.toUpperCase() : question}
                    </h1>
                </div>
            </InfoToolTip>
            <p >
            </p>
            {disabled ? <div className="answer-container">
                <p
                    // className="answer-form"
                    style={{ textAlign: "center", fontWeight: "bold" }}
                    onChange={() => { }}
                    value={description}
                    rows="7"
                    type="text"
                    readOnly="readonly"
                    placeholder={placeholder}
                > {description} </p>
            </div> : null}
            {!disabled ?
                <div className="answer-container">
                    <textarea
                        className="answer-form"
                        onChange={changeHandler}
                        value={description}
                        rows="7"
                        type="text"
                        placeholder={placeholder}
                    />
                </div> : null
            }
        </div>
        // <div className="form-container" >
        //     <InfoToolTip
        //         tutorialCopy={toolTipCopy}
        //         hasToolTip={hasToolTip}
        //     >
        //         <div style={{ display: "flex", flexDirection: "row" }}>
        //             <h1 className="form-header" style={{ color: (questionColor ? questionColor : "black") }}>
        //                 {upperCaseQuestion ? question.toUpperCase() : question}
        //             </h1>
        //         </div>
        //     </InfoToolTip>
        //     <div className="answer-container">

        //         {disabled ? <p
        //             // className="answer-form"
        //             style={{textAlign:"center", fontWeight:"bold"}}
        //             onChange={() => { }}
        //             value={description}
        //             rows="7"
        //             type="text"
        //             readOnly="readonly"
        //             placeholder={placeholder}
        //         > {description} </p> : <textarea
        //             className="answer-form"
        //             onChange={changeHandler}
        //             value={description}
        //             rows="7"
        //             type="text"
        //             placeholder={placeholder}
        //         />}

        //     </div>
        // </div>
    )
}
export default FormQuestion;
