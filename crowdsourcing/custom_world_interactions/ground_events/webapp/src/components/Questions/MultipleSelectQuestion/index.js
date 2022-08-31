
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React, {useEffect, useState} from "react";
//STYLING
import "./styles.css";
//CUSTOM COMPONENTS
import TaskButton from "../../TaskButton"


//MultipleSelectQuestion - Question where answer comes from clicking a button and more than one button may be selected at a time
const MultipleSelectQuestion = ({
    question, //Question Text
    answers, //Array of answers
    selectFunction, // setState function connected to payload state
    hasSecondaryInput
})=>{
    //Local State
    const [selectedAnswers, setSelectedAnswers] = useState([]);
    const [answerList, setAnswerList] = useState([])

    //clickHandler - handles selection and unselection of answers
    const clickHandler = (id, answer)=>{
        let updatedAnswers;
        //Selecting answer
        if(selectedAnswers.indexOf(answer)<0){
            updatedAnswers = [...selectedAnswers, answer];
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
            <h1 className="multipleselectquestion-text">
                {question}
            </h1>
            <div className="multipleselectanswer-container">
            {
                [answerList].length
                ?
                answerList.map((answer, index)=>(
                <>
                    <TaskButton
                        key={index}
                        name={answer}
                        selectFunction={()=>clickHandler(index, answer)}
                        isSelected={(selectedAnswers.indexOf(answer)>=0)}
                        selectedContainer="mc-button__container"
                        unselectedContainer="mc-selectedbutton__container"
                        selectedText="mc-button__text"
                        unselectedText="mc-selectedbutton__text"
                    />
                </>
                ))
                :
                null
            }
            </div>
        </div>
    )
}
export default MultipleSelectQuestion;
