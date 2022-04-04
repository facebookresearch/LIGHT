/* REACT */
import react, {useState, useEffect} from "react";
/* STYLES */
import "./styles.css";
/* BOOTSTRAP COMPONENTS */
import Form from 'react-bootstrap/form';
/* CUSTOM COMPONENTS */
import ChatInputOption from "../../../ChatInputOption";

const CheckBoxAnswer = ({
    selectedQuestion,
    answer,
    answerUpdateHandler,
    selectedAnswers
})=>{
    /*---------------LOCAL STATE----------------*/
    const [isSelected, setIsSelected] = useState(false)
    /*---------------HANDLERS----------------*/
    const SelectionHandler = e => {
        console.log("CLICKED ANSWER DATA:  ", answer)
        answerUpdateHandler(answer)
        if(isSelected){
            setIsSelected(false)
        }else {
            setIsSelected(true)
        }
    }
    /*---------------LIFECYCLE----------------*/

    useEffect(() => {
        console.log("CURRENTLY SELECTED ANSWERS:  ", selectedAnswers)
        if(selectedAnswers.length){
            let answerSelected = selectedAnswers.filter(ans => answer.id===ans.id);
                if(answerSelected.length){
                    setIsSelected(true);
                }else{
                    setIsSelected(false);
                }
        }
    }, [selectedAnswers, selectedQuestion])

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
