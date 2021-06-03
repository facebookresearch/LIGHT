import React, {useEffect, useState} from "react";
import "./styles.css";

//CUSTOM COMPONENTS
import TaskButton from "../../TaskButton"

const BooleanQuestion = ({question, trueAnswer, falseAnswer, children})=>{
    const [answer, setAnswer] = useState(null);

    const trueHandler = ()=>{
        setAnswer(true)
    }
    const falseHandler = ()=>{
        setAnswer(false)
    }

    return(
        <div className="question-container" >
            <h1 className="question-text">
                {question}
            </h1>
            <div className="answer-container">
                <TaskButton name={trueAnswer.name} isSelected={answer} onClick={trueHandler}/>
                <TaskButton name={falseAnswer.name} isSelected={answer===false} onClick={falseHandler} />
            </div>
            {
                answer && children ?
                children
                :
                null
            }
        </div>
    )
}
export default BooleanQuestion;
