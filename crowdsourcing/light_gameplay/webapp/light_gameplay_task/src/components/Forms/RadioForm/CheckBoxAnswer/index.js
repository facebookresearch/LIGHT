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
    const [currentlySelectedAnswers, setCurrentlySelectedAnswers] = useState([])
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
        console.log("CHECKBOX SELECTED QUESTION CHANGED!")
        if(selectedQuestion.selectedAnswers!== undefined){
            console.log("CHECKBOX ANSWER IN ARRAY:  ", selectedQuestion.selectedAnswers)
            setCurrentlySelectedAnswers(selectedQuestion.selectedAnswers);
        }else {
            console.log("CHECKBOX NO ANSWERS IN ARRAY:  ", selectedQuestion.selectedAnswers, isSelected)
            setCurrentlySelectedAnswers([]);
        }
    }, [selectedQuestion])

    useEffect(() => {
        console.log("CURRENTLY SELECTED ANSWERS:  ", currentlySelectedAnswers)
            let answerSelected = currentlySelectedAnswers.filter(ans => answer.id===ans.id);
                if(answerSelected.length){
                    setIsSelected(true);
                }else{
                    setIsSelected(false);
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
