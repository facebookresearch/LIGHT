//REACT
import React, {useState, useEffect} from "react";
//STYLE
import "./styles.css";
//CUSTOM COMPONENTS
import MultipleChoiceQuestion from "../Questions/MultipleChoice";
//UTILS
import FormatQuestion from "../../utils/FormatQuestion";
// QuestionBlock - Renders a list of questions for a pertaining to a single node
const QuestionBlock = ({
    headerText,
    defaultQuestions,
    updateFunction// the function to update the attributes for the objects
})=>{


    const Question = ({questionInfo, updateFunction})=>{
        const {question, questionType, questionField, options, hasToolTip, toolTipText, hasCheckbox}= questionInfo;
        let formattedQuestion = FormatQuestion(question, [])
        switch(questionType) {
            case "multipleChoice":
                return(
                    <MultipleChoiceQuestion
                        question={formattedQuestion}
                        answers={options}
                        selectFunction={(updateValue)=>updateFunction(questionField, updateValue)}
                        hasToolTip={hasToolTip}
                        toolTipText={toolTipText}
                        hasCheckbox={hasCheckbox}
                    />
                )
            default:
                    return null
        }
    }

    return(
        <div className="questionblock-container">
            {
                headerText ?
                <div className="questionblock-header">
                    <h5 className="questionblock-header__text">
                        {headerText}
                    </h5>
                </div>
                :
                null
            }
            <div className="questionblock-body">
            {
                defaultQuestions.map((defaultQuestion, index)=>{
                    const {question, questionType, questionField, options, hasToolTip, toolTipText, hasCheckbox}= defaultQuestion;
                    let formattedQuestion = FormatQuestion(question, [])
                    return (
                        <MultipleChoiceQuestion
                        question={formattedQuestion}
                        answers={options}
                        selectFunction={(updateValue)=>updateFunction(questionField, updateValue)}
                        hasToolTip={hasToolTip}
                        toolTipText={toolTipText}
                        hasCheckbox={hasCheckbox}
                    />
                    )
                })
            }
            </div>
        </div>
    )
}
export default QuestionBlock;
