
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React, {useState, useEffect} from "react";
//STYLE
import "./styles.css";
//CUSTOM COMPONENTS
import MultipleSelectQuestion from "../../../../components/Questions/MultipleSelectQuestion";
import MultipleChoiceQuestion from "../../../../components/Questions/MultipleChoiceQuestion";
import NumberForm from "../../../../components/NumberForm";
//UTILS
import FormatQuestion from "../../../../utils/FormatQuestion";
// AttributeQuestionRow - Renders correct question componen
const AttributeQuestionRow = ({
    selection,// Objects who's attributes are being added and removed
    defaultQuestions,
    updateFunction// the function to update the attributes for the objects
})=>{

    const Question = ({questionInfo, updateFunction})=>{
        console.log("SELECTION:  ", selection, "QUESTION:  ", questionInfo)
        const {question, toolTip, options, questionType}= questionInfo;
        const {name}= selection;
        let formattedQuestion = FormatQuestion(question, [name])
        switch(questionType) {
            case "multipleSelect":
            return (
                <MultipleSelectQuestion
                    question={formattedQuestion}
                    answers={options}
                    selectFunction={(updateKey, updateValue)=>updateFunction(updateKey, updateValue)}
                    toolTip={toolTip}
                />
            )
            case "numeric":
                return (
                    <NumberForm
                        header={formattedQuestion}
                        formFunction={(updateValue)=>updateFunction(questionInfo.field, updateValue)}
                        startingVal={0}
                        toolTip={toolTip}
                    />
                )
            case "multipleChoice":
                return(
                    <MultipleChoiceQuestion
                        question={formattedQuestion}
                        answers={options}
                        selectFunction={(updateKey, updateValue)=>updateFunction(updateKey, updateValue)}
                        selection={selection}
                        toolTip={toolTip}
                    />
                )
            default:
                    return null
        }
    }

    return(
        <div className="attributequestionrow-container" >
            {
                defaultQuestions
                ?
                defaultQuestions.map((defaultQuestion, index)=>{
                    return <Question key={index} questionInfo={defaultQuestion} updateFunction={updateFunction}/>
                })
                :
                null
            }
        </div>
    )
}
export default AttributeQuestionRow;
