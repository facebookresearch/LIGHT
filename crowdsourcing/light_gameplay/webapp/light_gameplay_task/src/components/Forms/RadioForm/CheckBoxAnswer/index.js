/* REACT */
import react, {useState} from "react";
/* STYLES */
import "./styles.css";
/* BOOTSTRAP COMPONENTS */
import Form from 'react-bootstrap/form';
/* CUSTOM COMPONENTS */
import ChatInputOption from "../../../ChatInputOption";

const CheckBoxAnswer = ({
    answer,
    answerUpdateHandler
})=>{
    //LOCAL STATE
    const [selectedAnswer, setSelectedAnswer] = useState(false);

    const SelectionHandler = e => {
        if(selectedAnswer){
            setSelectedAnswer(false);
        }else {
        setSelectedAnswer(true);
        }
    }

    return(
        <div
        className="answer-container"
        >
            <div className="answer-checkbox_container">
                <Form.Check
                inline
                type={'checkbox'}
                onChange={SelectionHandler}
                checked={selectedAnswer}
                />
            </div>
            <div className="answer-chatinput_container">
                <ChatInputOption
                    answer= {answer}
                />
            </div>
    </div>
    )
}

export default CheckBoxAnswer;
