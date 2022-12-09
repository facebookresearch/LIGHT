/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React, { useEffect, useState } from "react";
//STYLING
import "./styles.css";
//CUSTOM COMPONENTS
import TaskButton from "../../TaskButton";
import FormatQuestion from "../../Utils/FormatQuestion";
import InfoToolTip from "../../InfoToolTip";
import Checkbox from "../../Checkbox";
//BooleanQuestion - a component that renders a question that expects a boolean answer.  If a component is wrapped by this component under the "true" answer it will conditionally render that child.
const BooleanQuestion = ({
    question, // The Question posed by the question
    trueAnswer, //Object that will have a name attribute which will be the text rendered on the "true" button
    falseAnswer,//Object that will have a name attribute which will be the text rendered on the "false" button
    keywords, //key words will replace any # in the header text being formatted by the formatQuestion function
    inverted,// Will render children based on a false answer rather that true if this value is true
    formFunction,// setState function that connects the answer to the payload state
    toolTipCopy,// Copy for desired tooltip
    hasToolTip,// Boolean stating whether or not this component has a tooltip
    isComplete,// Completion condition for question to be satisfactorily answered
    defaultOption,
    children,
    disabled
}) => {
    //local state for question answer
    // const [answer, setAnswer] = useState(null);
    const [answer, setAnswer] = useState(defaultOption ? defaultOption : null);

    //sets both local and payload state to true
    const trueHandler = () => {
        if (disabled) {
            return;
        }
        setAnswer(true)
        formFunction(true)
    }
    //sets both local and payload state to false
    const falseHandler = () => {
        if (disabled) {
            return;
        }
        setAnswer(false)
        formFunction(false)
    }
    console.log(`${question}: ${defaultOption};;;;; ${defaultOption === false}`)

    return (
        <div className="booleanquestion-container" >
            <InfoToolTip
                tutorialCopy={toolTipCopy}
                hasToolTip={hasToolTip}
            >
                <div style={{ display: "flex", flexDirection: "row" }}>
                    {hasToolTip && !disabled ? <Checkbox isComplete={isComplete} /> : null}
                    <FormatQuestion
                        question={question}
                        keywords={keywords}
                        containerStyle="booleanquestion-text"
                    />
                </div>
            </InfoToolTip>
            <div className="booleananswer-container">
                {!disabled ? <TaskButton
                    name={trueAnswer.name}
                    isSelected={answer}
                    selectFunction={trueHandler}
                    unselectedContainer="b-button__container true"
                    selectedContainer="b-selectedbutton__container true"
                    unselectedText="b-button__text true"
                    selectedText=" b-selectedbutton__text"
                    disabled={disabled}
                /> : null }
                {!disabled ? <TaskButton name={falseAnswer.name}
                    isSelected={answer === false}
                    selectFunction={falseHandler}
                    unselectedContainer="b-button__container false"
                    selectedContainer="b-selectedbutton__container false"
                    unselectedText="b-button__text false"
                    selectedText=" b-selectedbutton__text"
                    disabled={disabled}
                /> : null }

                {/* {!disabled || answer ? <TaskButton
                    name={trueAnswer.name}
                    isSelected={answer}
                    selectFunction={trueHandler}
                    unselectedContainer="b-button__container true"
                    selectedContainer="b-selectedbutton__container true"
                    unselectedText="b-button__text true"
                    selectedText=" b-selectedbutton__text"
                    disabled={disabled}
                /> : null}
                {!disabled || !answer ? <TaskButton name={falseAnswer.name}
                    isSelected={answer === false}
                    selectFunction={falseHandler}
                    unselectedContainer="b-button__container false"
                    selectedContainer="b-selectedbutton__container false"
                    unselectedText="b-button__text false"
                    selectedText=" b-selectedbutton__text"
                    disabled={disabled}
                /> : null} */}

            </div>
            <div style={{ width: "100%", marginTop: "10px" }}>
                {   //if inverted it will only render child if answer is false not if answer == null
                    ((!!inverted ? (!answer && answer !== null) : answer) && children) ?
                        children
                        :
                        null
                }
            </div>
        </div>
    )
}
export default BooleanQuestion;
