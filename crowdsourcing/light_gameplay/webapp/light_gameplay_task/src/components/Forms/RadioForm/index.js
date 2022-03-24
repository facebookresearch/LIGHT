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
                        {
                            <div className="answers-container">
                                {
                                    answerData.map((answer, index)=>(
                                        <div
                                            key={index}
                                            className="answer-container"
                                        >
                                            <div className="answer-checkbox_container">
                                                <Form.Check
                                                inline
                                                type={'radio'}
                                                />
                                            </div>
                                            <div className="answer-chatinput_container">
                                                <ChatInputOption
                                                    answer= {answer}
                                                />
                                            </div>
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
