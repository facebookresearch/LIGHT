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

    const clickHandler = (id)=>{
        console.log("CLICK HANDLER:  ID:", id)
        setSelectedAnswer(id);
        answerList.map((ans, index)=>{
            const {value} = ans;
            console.log("CLICK HANDLER:  ", id==index,  "ans:  ", ans, "index:", index)
            if(id==index){
                selectFunction(value, true);
            }else{
                selectFunction(value, false);
            }

        })
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
                answerList.length
                ?
                answerList.map((answer, index)=>{
                    const {name} =answer;
                    return(
                        <Form.Check
                            inline
                            key={index}
                            label={name}
                            name={name}
                            type={"radio"}
                            checked={selectedAnswer==index}
                            onChange={()=>clickHandler(index, answer)}
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
