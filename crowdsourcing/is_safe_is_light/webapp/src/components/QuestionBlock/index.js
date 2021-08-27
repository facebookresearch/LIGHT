//REACT
import React, {useState, useEffect} from "react";
//STYLE
import "./styles.css";
//CUSTOM COMPONENTS
import MultipleChoiceQuestion from "../../../../components/Questions/MultipleChoiceQuestion";
//UTILS
import FormatQuestion from "../../../../utils/FormatQuestion";
// QuestionBlock - Renders a list of questions for a pertaining to a single node
const QuestionBlock = ({
    selectionNode,
    headerText,
    defaultQuestions,
    updateFunction// the function to update the attributes for the objects
})=>{


    const Question = ({questionInfo, updateFunction})=>{
        console.log("selectionNode:  ", selectionNode, "QUESTION:  ", questionInfo)
        const {question, options, questionType}= questionInfo;
        const {sentence}= selectionNode;
        let formattedQuestion = FormatQuestion(question, [])
        switch(questionType) {
            case "multipleChoice":
                return(
                    <MultipleChoiceQuestion
                        question={formattedQuestion}
                        answers={options}
                        selectFunction={(updateKey, updateValue)=>updateFunction(updateKey, updateValue)}
                        selection={selection}
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
                    <h5>
                        {headerText}
                    </h5>
                </div>
                :
                null
            }
            <div>
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
