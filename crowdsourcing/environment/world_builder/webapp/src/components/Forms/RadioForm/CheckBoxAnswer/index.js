/* REACT */
import React, {useState, useEffect} from "react";
/* STYLES */
import "./styles.css";
/* BOOTSTRAP COMPONENTS */
import Form from 'react-bootstrap/Form';
/* CUSTOM COMPONENTS */
import ChatInputOption from "../../../ChatInputOption";

const CheckBoxAnswer = ({
    selectedQuestion,
    answer,
    answerUpdateHandler
})=>{
    /*---------------LOCAL STATE----------------*/
    const [currentlySelectedAnswers, setCurrentlySelectedAnswers] = useState([])
    const [isSelected, setIsSelected] = useState(false)
    /*---------------HANDLERS----------------*/
    const SelectionHandler = e => {
        answerUpdateHandler(answer)
        if(isSelected){
            setIsSelected(false)
        }else {
            setIsSelected(true)
        }
    }
    /*---------------LIFECYCLE----------------*/

    useEffect(() => {
        if(selectedQuestion.selectedAnswers!== undefined){
            setCurrentlySelectedAnswers(selectedQuestion.selectedAnswers);
        }else {
            setCurrentlySelectedAnswers([]);
        }
    }, [selectedQuestion])

    useEffect(() => {
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
