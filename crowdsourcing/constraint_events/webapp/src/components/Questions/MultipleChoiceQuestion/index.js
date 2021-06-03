import React, {useEffect, useState} from "react";
import "./styles.css";

//CUSTOM COMPONENTS
import TaskButton from "../../TaskButton"

const MultipleChoiceQuestion = ({question, answers, selectFunction})=>{
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [answerList, setAnswerList] = useState([])

    const clickHandler = (id, answer)=>{
        setSelectedAnswer(id);
        selectFunction(answer);
    }
    useEffect(()=>{
        setAnswerList(answers)
    }, [answers])
    return(
        <div className="question-container" >
            <h1 className="question-text">
                {question}
            </h1>
            <div className="answer-container">
            {
                [answerList].length
                ?
                answerList.map((answer, index)=><TaskButton key={index} name={answer} selectFunction={()=>clickHandler(index, answer)} isSelected={selectedItem==index} />)
                :
                null
            }
            </div>
        </div>
    )
}
export default MultipleChoiceQuestion;
