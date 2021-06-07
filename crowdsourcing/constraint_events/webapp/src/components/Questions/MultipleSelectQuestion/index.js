import React, {useEffect, useState} from "react";
import "./styles.css";

//CUSTOM COMPONENTS
import TaskButton from "../../TaskButton"

const MultipleSelectQuestion = ({question, answers, selectFunction})=>{
    const [selectedAnswers, setSelectedAnswers] = useState([]);
    const [answerList, setAnswerList] = useState([])

    const clickHandler = (id, answer)=>{
        let updatedAnswers;
        if(selectedAnswers.indexOf(id)<0){
            updatedAnswers = [...selectedAnswers, id];
            setSelectedAnswers(updatedAnswers)
        }
        if(selectedAnswers.indexOf(id)>=0){
            updatedAnswers = selectedAnswers.filter(answer => (answer!==id))
            setSelectedAnswers(updatedAnswers)
            selectFunction(answer);
        }
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
                answerList.map((answer, index)=>(
                <TaskButton
                    key={index}
                    name={answer}
                    selectFunction={()=>clickHandler(index, answer)}
                    isSelected={(selectedAnswers.indexOf(index)>=0)}
                    unselectedContainer="mc-button__container"
                    selectedContainer="mc-selectedbutton__container"
                    unselectedText="mc-button__text"
                    selectedText="mc-selectedbutton__text"
                />
                ))
                :
                null
            }
            </div>
        </div>
    )
}
export default MultipleSelectQuestion;
