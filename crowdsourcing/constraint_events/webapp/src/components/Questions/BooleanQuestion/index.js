import React, {useEffect, useState} from "react";
import "./styles.css";

//CUSTOM COMPONENTS
import TaskButton from "../../TaskButton"
import FormQuestion from "../../Utils/FormatQuestion";

const BooleanQuestion = ({question, trueAnswer, falseAnswer, keywords, children})=>{
    const [answer, setAnswer] = useState(null);

    const trueHandler = ()=>{
        setAnswer(true)
    }
    const falseHandler = ()=>{
        setAnswer(false)
    }

    return(
        <div className="question-container" >
                <FormQuestion
                    question={question}
                    keywords={keywords}
                    containerStyle="question-text"
                />
            <div className="answer-container">
                <TaskButton
                    name={trueAnswer.name}
                    isSelected={answer}
                    selectFunction={trueHandler}
                    unselectedContainer="b-button__container true"
                    selectedContainer="b-selectedbutton__container true"
                    unselectedText="b-button__text true"
                    selectedText=" b-selectedbutton__text"

                    />
                <TaskButton name={falseAnswer.name}
                    isSelected={answer===false}
                    selectFunction={falseHandler}
                    unselectedContainer="b-button__container false"
                    selectedContainer="b-selectedbutton__container false"
                    unselectedText="b-button__text false"
                    selectedText=" b-selectedbutton__text"

                    />
            </div>
            {
                answer && children ?
                children
                :
                null
            }
        </div>
    )
}
export default BooleanQuestion;
