//REACT
import React, { useEffect, useState } from "react";
//STYLES
import "./styles.css"
//CUSTOM COMPONENT
import InfoToolTip from "../../InfoToolTip";
import Checkbox from "../../Checkbox";

const Entry = ({text, updateText, onRemove, placeholder}) => {
    return (
        <li>
            <textarea
                className="list-edit-form"
                onChange={(e) => updateText(e.target.value)}
                value={text}
                rows="1"
                type="text"
                placeholder={placeholder}
            />
            <button onClick={onRemove}>Remove Item</button>
        </li>
    );
}

//ListEditQuestion - a question who's answer is a list that can be extended or cut down
const ListEditQuestion = ({
    question,//Actual text of question
    questionColor, //Text color
    entries,// Initial item list
    updateEntry,// setState function that connects answer to payload state
    toolTipCopy,// Text that will appear in tooltip
    hasToolTip,// boolean that adds tooltip icon and text if true
    isComplete, // completion condition
    entryPlaceholder // placeholder for each entry in the list
}) => {
    const entryForms = entries.map((n, idx) => <Entry 
        key={"remaining-"+idx} 
        text={n}
        updateText={(t) => updateEntry(t, idx, false)}
        onRemove={() => updateEntry(null, idx, true)}
        placeholder={entryPlaceholder}
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
            <div className="list-edit-container">
                <ul className="list-edit-list">
                    {entryForms}
                </ul>
                <button onClick={() => updateEntry(null, null, null)}>Add entry</button>
            </div>
        </div>
    )
}
export default ListEditQuestion;
