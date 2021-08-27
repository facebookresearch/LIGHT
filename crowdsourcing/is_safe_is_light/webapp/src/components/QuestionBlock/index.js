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
    payloadData,
    headerText,
    defaultQuestions,
    updateFunction// the function to update the attributes for the objects
})=>{


    const Question = ({questionInfo, updateFunction})=>{
        const {question, questionType, questionField, options, hasToolTip, toolTipText, hasCheckbox}= questionInfo;
        let formattedQuestion = FormatQuestion(question, [])

        console.log("TRUE:  ", payloadData[questionField]===false, "FALSE:  ", payloadData[questionField]);
        switch(questionType) {
            case "multipleChoice":
                return(
                    <MultipleChoiceQuestion
                        question={formattedQuestion}
                        answers={options}
                        selectFunction={(updateValue)=>updateFunction(questionField, updateValue)}
                        isComplete={payloadData[questionField]===false || payloadData[questionField]}
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
                defaultQuestions
                ?
                defaultQuestions.map((defaultQuestion, index)=>{
                    return (
                        <Question
                            key={index}
                            questionInfo={defaultQuestion}
                            updateFunction={updateFunction}

                        />
                    )
                })
                :
                null
            }
            </div>
        </div>
    )
}
export default QuestionBlock;
