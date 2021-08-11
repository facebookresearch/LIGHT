//REACT
import React, {useEffect, useState} from "react";
//STYLE
import "./styles.css";
//BOOSTRAP
import Form from 'react-bootstrap/Form';

// MultipleChoiceQuestion - Form type that allows user to select single answer from multiple option to answer question
const MultipleChoiceQuestion = ({question, answers, selectFunction, selection})=>{
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
            <h1 className="question-text">
                {question}
            </h1>
            <div className="answer-container">
            {
                answerList.length
                ?
                answerList.map((answer, index)=>{
                    const {name, value} =answer;
                    return(
                        <Form.Check
                            inline
                            key={index}
                            label={name}
                            name={selection.name}
                            type={"radio"}
                            checked={selectedAnswer==value}
                            onChange={(e)=>clickHandler(value)}
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
