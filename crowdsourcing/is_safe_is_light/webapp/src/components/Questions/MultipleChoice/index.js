//REACT
import React, {useEffect, useState} from "react";
//STYLES
import "./styles.css";
//CUSTOM COMPONENTS
import TaskButton from "../../TaskButton";
import ToolTip from "../../ToolTip"
//ICONS
import Checkbox from "../../Checkbox"


// MultipleChoiceQuestion - Form type that allows user to select single answer from multiple option to answer question
const MultipleChoiceQuestion = ({
    question,
    answers,
    selectFunction,
    hasToolTip,
    toolTipText,
    hasCheckbox
})=>{
/*------------------------------------STATE------------------------------------*/
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [answerList, setAnswerList] = useState([])
/*------------------------------------LIFE CYCLE------------------------------------*/
    useEffect(()=>{
        setAnswerList(answers)
    }, [])

/*------------------------------------HANDLERS------------------------------------*/
    const clickHandler = (value)=>{
        console.log("selectedAnswer", value)
        console.log("ANSWER", value)
        setSelectedAnswer(value);
        selectFunction(value)
    }


    return(
        <div className="mcquestion-container" >
            <div className="mcquestion-header">
            {hasCheckbox ? <Checkbox isComplete={selectedAnswer!==null}/> : null }
                <ToolTip
                    hasToolTip={hasToolTip}
                    tipText={toolTipText}
                >
                    <h1 className="mcquestion-text">
                        {question}
                    </h1>
                </ToolTip>
            </div>
            <div className="mcanswer-container">
            {
                answers.map((answer, index)=>{
                    const {label, value} = answer;
                    console.log("TYPEOF:  ", typeof value)
                    console.log("selectedAnswer:  ", selectedAnswer)
                    let isSelected = selectedAnswer==value
                    return(
                        <TaskButton
                            key={index}
                            unselectedContainer={"mc-button__container"}
                            selectedContainer={"mc-selectedbutton__container"}
                            unselectedText={"mc-button__text"}
                            selectedText={"mc-selectedbutton__text"}
                            name={label}
                            selectFunction={()=>clickHandler(value)}
                            isSelected ={isSelected}
                        />
                    )
                })
            }
            </div>
        </div>
    )
}
export default MultipleChoiceQuestion;
