//REACT
import React, { useEffect, useState } from "react";
//STYLES
import "./styles.css"
//CUSTOM COMPONENT
import InfoToolTip from "../../InfoToolTip";
import Checkbox from "../../Checkbox";

const Entry = ({name, text, updateText}) => {
    return (
        <li>
            <b>{name}:</b>
            <textarea
                className="answer-form"
                onChange={(e) => updateText(e.target.value)}
                value={text}
                rows="1"
                type="text"
                placeholder={'enter an item'}
            />
        </li>
    );
}

// MultiFormQuestion - a question that requires an answer for multiple values in a map
const MultiFormQuestion = ({
    question,//Actual text of question
    questionColor, //Text color
    entryMap,// Initial item list
    updateEntry,// setState function that connects answer to payload state
    toolTipCopy,// Text that will appear in tooltip
    hasToolTip,// boolean that adds tooltip icon and text if true
    isComplete// completion condition
}) => {
    const entryForms = Object.fromEntries(Object.entries(entryMap).map(([label, value], idx) => <Entry 
        key={"multi-form-entry-"+idx} 
        name={label}
        text={value}
        updateText={(t) => updateEntry(label, t)}
    />));
    return (
        <div className="form-container" >
            <InfoToolTip
                tutorialCopy={toolTipCopy}
                hasToolTip={hasToolTip}
            >
                <div style={{ display: "flex", flexDirection: "row" }}>
                    {hasToolTip ? <Checkbox isComplete={isComplete} /> : null}
                    <h1 className="form-header" style={{ color: (questionColor ? questionColor : "black") }}>
                        {question}
                    </h1>
                </div>
            </InfoToolTip>
            <p >
            </p>
            <div className="answer-container">
                <ul>
                    {entryForms}
                </ul>
            </div>
        </div>
    )
}
export default MultiFormQuestion;
