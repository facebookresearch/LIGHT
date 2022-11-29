//REACT
import React, {useEffect, useState} from "react";
//STYLING
import "./styles.css";
//CUSTOM COMPONENTS
import TaskButton from "../../TaskButton"
import InfoToolTip from "../../InfoToolTip";
import Checkbox from "../../Checkbox";
import FormatQuestion from "../../Utils/FormatQuestion";


//MultipleSelectQuestion - Question where answer comes from clicking a button and more than one button may be selected at a time
const MultipleSelectQuestion = ({
    question, //Question Text
    answers, //Array of answers
    colors, // array of colors for each answer
    selectFunction, // setState function connected to payload state
    toolTipCopy, // Copy for desired tooltip
    hasToolTip, // Boolean stating whether or not this component has a tooltip
    isComplete, // Completion condition for question to be satisfactorily answered
    onlySelectOne,
})=>{
    //Local State
    const [selectedAnswers, setSelectedAnswers] = useState([]);
    const [answerList, setAnswerList] = useState([]);
    
    if (colors === undefined) {
        colors = answers.map(a => undefined);
    }

    //clickHandler - handles selection and unselection of answers
    const clickHandler = (id, answer)=>{
        let updatedAnswers;
        //Selecting answer
        if(selectedAnswers.indexOf(answer)<0){
            if (onlySelectOne) {
                updatedAnswers = [answer];
            } else {
                updatedAnswers = [...selectedAnswers, answer];
            }
            setSelectedAnswers(updatedAnswers)
            selectFunction(updatedAnswers)
        }
        //Unselecting answer
        if(selectedAnswers.indexOf(answer)>=0){
            updatedAnswers = selectedAnswers.filter(ans => (ans!==answer))
            setSelectedAnswers(updatedAnswers)
            selectFunction(updatedAnswers);
        }
    }

    useEffect(()=>{
        setAnswerList(answers)
    }, [answers])
    return(
        <div className="multipleselectquestion-container" >
            <InfoToolTip
                tutorialCopy={toolTipCopy}
                hasToolTip={hasToolTip}
            >
                <div style={{display:"flex", flexDirection:"row"}}>
                    {hasToolTip?<Checkbox isComplete={isComplete} />:null}
                    <FormatQuestion
                        question={question}
                        containerStyle="multipleselectquestion-text"
                    />
                </div>
            </InfoToolTip>
            <div className="multipleselectanswer-container">
            {
                [answerList].length
                ?
                answerList.map((answer, index)=>(
                    <TaskButton
                        key={index}
                        name={answer}
                        selectFunction={()=>clickHandler(index, answer)}
                        isSelected={(selectedAnswers.indexOf(answer)>=0)}
                        color={colors[index]}
                        selectedContainer="mc-button__container"
                        unselectedContainer="mc-selectedbutton__container"
                        selectedText="mc-button__text"
                        unselectedText="mc-selectedbutton__text"
                    />
                ))
                :
                null
            }
            </div>
        </div>
    )
}
export default MultipleSelectQuestion;
