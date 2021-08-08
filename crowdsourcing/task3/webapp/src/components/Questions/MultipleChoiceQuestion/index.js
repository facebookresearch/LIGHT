//REACT
import React, {useEffect, useState} from "react";
//STYLE
import "./styles.css";
//BOOSTRAP
import Form from 'react-bootstrap/Form';
//CUSTOM COMPONENTS
import TaskButton from "../../TaskButton"

// MultipleChoiceQuestion - Form type that allows user to select single answer from multiple option to answer question
const MultipleChoiceQuestion = ({question, answers, selectFunction})=>{
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [answerList, setAnswerList] = useState([])

    const clickHandler = (id, answer)=>{
        if(selectedAnswer==index){
            setSelectedAnswer(null);
            selectFunction(answer.value, false);
        }
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
                answerList.map((answer, index)=>{
                    const {name, value} =answer;
                    return(
                        <Form.Check
                            key={index}
                            label={name}
                            name={name}
                            type={"radio"}
                            checked={selectedAnswer==index}
                            onChange={()=>clickHandler(index, value)}
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
