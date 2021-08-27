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
    isComplete,
    hasToolTip,
    toolTipText,
    hasCheckbox
})=>{
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [answerList, setAnswerList] = useState([])
    useEffect(()=>{
        setAnswerList(answers)
    }, [])
    const clickHandler = (e)=>{
        const {target} = e
        const {value} = target;
        console.log("selectedAnswer", value)
        console.log("ANSWER", value)
        setSelectedAnswer(value);
        selectFunction(value)
    }


    return(
        <div className="mcquestion-container" >
            <div className="mcquestion-header">
                {hasCheckbox ? <Checkbox isComplete={isComplete}/> : null }
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
                answerList.length
                ?
                answerList.map((answer, index)=>{
                    const {label, value} = answer;
                    return(
                        <TaskButton
                            key={index}
                            unselectedContainer={"mc-button__container"}
                            selectedContainer={"mc-selectedbutton__container"}
                            unselectedText={"mc-button__text"}
                            selectedText={"mc-selectedbutton__text"}
                            name={label}
                            selectFunction={clickHandler}
                            isSelected ={selectedAnswer==value}
                        />
                    )
                })
                :
                null
            }
            </div>
        </div>
    )
}
export default MultipleChoiceQuestion;
