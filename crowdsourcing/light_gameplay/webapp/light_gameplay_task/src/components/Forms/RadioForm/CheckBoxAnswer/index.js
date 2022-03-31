/* REACT */
import react, {useState, useEffect} from "react";
/* STYLES */
import "./styles.css";
/* BOOTSTRAP COMPONENTS */
import Form from 'react-bootstrap/form';
/* CUSTOM COMPONENTS */
import ChatInputOption from "../../../ChatInputOption";

const CheckBoxAnswer = ({
    answer,
    answerUpdateHandler,
    currentlySelectedAnswers
})=>{
    /*---------------LOCAL STATE----------------*/
    const [isSelected, setIsSelected] = useState([])
    /*---------------HANDLERS----------------*/
    const SelectionHandler = e => {
        console.log("CLICKED ANSWER DATA:  ", answer)
        answerUpdateHandler(answer)
    }
    /*---------------LIFECYCLE----------------*/

    useEffect(() => {
        if(currentlySelectedAnswers){
            currentlySelectedAnswers.map(selectedAnswer =>{
                if(selectedAnswer.id === answer.id){
                    setIsSelected(true);
                }else{
                    setIsSelected(false);
                }
            })
        }
    }, [currentlySelectedAnswers])

    return(
        <div
        className="answer-container"
        >
            <div className="answer-checkbox_container">
                <Form.Check
                inline
                type={'checkbox'}
                onChange={SelectionHandler}
                checked={isSelected}
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
