/* REACT */
import react from "react";

/* STYLES */
import "./styles.css";
/* BOOTSTRAP COMPONENTS */
import Form from 'react-bootstrap/form'

const RadioForm = ({questionData})=>{
    let {question, answers}= questionData
    return (
    <Form className="radioform-container">
                    <div className="question-container">
                        <Form.Label>{}</Form.Label>
                        <img className="question-img" src={question} />
                        {
                            <div className="answers-container">
                                {
                                    answers.map(answer=>(
                                        <div className="answer-container">
                                            <Form.Check
                                            inline
                                            type={'radio'}
                                            />
                                            <img className="answer-img" src={answer} />
                                        </div>
                                    ))
                                }
                            </div>
                        }
                    </div>
    </Form>
    )
}

export default RadioForm;
