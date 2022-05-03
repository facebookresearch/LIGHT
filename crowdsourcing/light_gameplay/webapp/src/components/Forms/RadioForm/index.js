/* REACT */
import React, {useState, useEffect} from "react";
/* STYLES */
import "./styles.css";
/* BOOTSTRAP COMPONENTS */
import Form from 'react-bootstrap/Form';
/* CUSTOM COMPONENTS */
import CheckBoxAnswer from "./CheckBoxAnswer"

const RadioForm = ({
    questionBank,
    selectedQuestion,
    answerCollectionHandler,
})=>{
    /*---------------LOCAL STATE----------------*/
    const [formQuestion, setFormQuestion]= useState(null)
    const [possibleAnswers, setPossibleAnswers] = useState([]);
    const [selectedAnswers, setSelectedAnswers] = useState([]);
    /*---------------LIFECYCLE----------------*/
    useEffect(() => {
        setFormQuestion(selectedQuestion)
    }, [selectedQuestion, questionBank])

    useEffect(() => {
        setPossibleAnswers(selectedQuestion.answers)
    }, [formQuestion])

    useEffect(() => {
        if(selectedQuestion.selectedAnswers===undefined){
            setSelectedAnswers([])
        }else {
            setSelectedAnswers(selectedQuestion.selectedAnswers)
        }
    }, [selectedQuestion, questionBank, possibleAnswers])
    /*---------------HANDLERS----------------*/
    const answerUpdateHandler = (answer)=>{
        let updatedAnswers = [...selectedAnswers];
        let sameAnswersFound = updatedAnswers.filter(ans => answer.id===ans.id);
        if(sameAnswersFound.length){
            updatedAnswers = updatedAnswers.filter(ans => answer.id!==ans.id);
        } else {
            updatedAnswers = [...updatedAnswers, answer];
        }
        answerCollectionHandler(updatedAnswers)
    }
    return (
    <Form className="radioform-container">
        {formQuestion
        ?
        <div className="question-container">
            {
                <div className="answers-container">
                    {
                        possibleAnswers.map((answer, index)=>{
                            return (
                                <CheckBoxAnswer
                                    key={index}
                                    selectedQuestion={formQuestion}
                                    answer={answer}
                                    answerUpdateHandler={answerUpdateHandler}
                                />
                            )
                        })
                    }
                </div>
            }
        </div>
        :null
        }
    </Form>
    )
}

export default RadioForm;
