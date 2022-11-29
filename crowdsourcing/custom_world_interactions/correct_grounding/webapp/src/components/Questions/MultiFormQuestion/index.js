//REACT
import React, { useEffect, useState } from "react";
//STYLES
import "./styles.css"
//CUSTOM COMPONENT
import InfoToolTip from "../../InfoToolTip";
import Checkbox from "../../Checkbox";

const Entry = ({name, text, updateText, placeholder}) => {
    return (
        <li>
            <b>{name}:</b>
            <textarea
                className="multi-form-form"
                onChange={(e) => updateText(e.target.value)}
                value={text}
                rows="2"
                type="text"
                placeholder={placeholder}
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
    isComplete, // completion condition
    entryPlaceholder, // Placeholder array for form for each entry
}) => {
    const entryForms = Object.entries(entryMap).map(([label, value], idx) => <Entry 
        key={"multi-form-entry-"+idx} 
        name={label}
        text={value}
        updateText={(t) => updateEntry(label, t)}
        placeholder={entryPlaceholder[idx]}
    />);
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
            <div className="multi-form-container">
                <ul className="multi-form-list">
                    {entryForms}
                </ul>
            </div>
        </div>
    )
}
export default MultiFormQuestion;
