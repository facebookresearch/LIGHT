import React, {useEffect, useState} from "react";
import "./styles.css";

//CUSTOM COMPONENTS
import ObjectButton from "./ObjectButton";

const MultipleChoiceQuestion = ({question, answers})=>{
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [answerList, setAnswerList] = useState([])

    const clickHandler = (id, selection)=>{
        setSelectedItem(id);
        selectFunction(selection);
    }
    useEffect(()=>{
        setObjectList(items)
    }, [items])
    return(
        <div className="question-container" >
            <h1 className="question-text">
                {question}
            </h1>
            <div className="answer-container">
            {
                [answerList].length
                ?
                answerList.map((answer, index)=><ObjectButton key={index} name={item} selectFunction={()=>clickHandler(index, item)} isSelected={selectedItem==index} />)
                :
                null
            }
            </div>
        </div>
    )
}
export default MultipleChoiceQuestion;
