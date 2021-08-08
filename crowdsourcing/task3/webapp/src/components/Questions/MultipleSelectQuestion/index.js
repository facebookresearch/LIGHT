//REACT
import React, {useEffect, useState} from "react";
//STYLES
import "./styles.css";
//BOOTSTRAP COMPONENTS
import Form from 'react-bootstrap/Form'
import FormCheck from 'react-bootstrap/FormCheck'

// MultipleSelectQuestion - Form type that allows user to select multiple options to answer question
const MultipleSelectQuestion = ({question, answers, selectFunction})=>{

    const [selectedAnswers, setSelectedAnswers] = useState([]);
    const [answerList, setAnswerList] = useState([])

    useEffect(()=>{
        setAnswerList(answers)
    }, [answers])

    const clickHandler = (id, field)=>{
        let updatedAnswers;
        if(selectedAnswers.indexOf(id)<0){
            updatedAnswers = [...selectedAnswers, id];
            setSelectedAnswers(updatedAnswers)
            selectFunction(field, true)
        }
        if(selectedAnswers.indexOf(id)>=0){
            updatedAnswers = selectedAnswers.filter(answer => (answer!==id))
            setSelectedAnswers(updatedAnswers)
            selectFunction(field, false)
        }
    }
    return(
        <div className="multipleselectquestion-container" >
            <h1 className="multipleselectquestion-text">
                {question}
            </h1>
            <div className="multipleselectanswer-container">
                {
                    [answerList].length
                    ?
                    answerList.map((answer, index)=>{
                        const {name, value} =answer;
                        return(
                            <Form.Check
                                key={index}
                                inline
                                label={name}
                                name={name}
                                checked={selectedAnswers.indexOf(index)>=0}
                                type={"checkbox"}
                                onChange={()=>clickHandler(index, value)}
                            />
                    )}
                    )
                    :
                    null
                }
            </div>
        </div>
    )
}
export default MultipleSelectQuestion;
