//REACT
import React, {useEffect, useState} from "react";
//STYLES
import "./styles.css";
//CUSTOM COMPONENTS
import TaskButton from "../../TaskButton";
import Tooltip from "../../ToolTip"
//ICONS



// MultipleChoiceQuestion - Form type that allows user to select single answer from multiple option to answer question
const MultipleChoiceQuestion = ({
    question,
    answers,
    selectFunction,
    selection,
    isComplete
})=>{
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [answerList, setAnswerList] = useState([])
    useEffect(()=>{
        setAnswerList(answers)
    }, [])
    const clickHandler = (answer)=>{
        console.log("selectedAnswer", answer)
        console.log("ANSWER", answer)
        setSelectedAnswer(answer);
        answerList.map((ans)=>{
            const {value} = ans;
            console.log("Comparison", answer==value)
            if(answer==value){
                selectFunction(value, true);
            }else{
                selectFunction(value, false);
            }

        })
    }


    return(
        <div className="question-container" >
            <div>

                <ToolTip
                    hasToolTip={hasToolTip}
                    tipText={toolTipText}
                >
                    <h1 className="question-text">
                        {question}
                    </h1>
                </ToolTip>
            </div>
            <div className="answer-container">
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
