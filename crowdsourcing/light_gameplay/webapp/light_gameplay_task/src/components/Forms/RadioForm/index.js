/* REACT */
import react from "react";

/* STYLES */
import "./styles.css";
/* BOOTSTRAP COMPONENTS */
import Form from 'react-bootstrap/form';
/* CUSTOM COMPONENTS */
import ChatInputOption from "../../ChatInputOption";

const RadioForm = ({
    answerData
})=>{
    return (
    <Form className="radioform-container">
                    <div className="question-container">
                        <Form.Label>{}</Form.Label>

                        {
                            <div className="answers-container">
                                {
                                    answerData.map(answer=>(
                                        <div className="answer-container">
                                            <Form.Check
                                            inline
                                            type={'radio'}
                                            />
                                            <ChatInputOption
                                                answer= {answer}
                                            />
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
