import React, { useEffect, useRef } from "react";

import TipsCopy from "./TipsCopy"

const DescriptionForm = ({ formVal, formFunction, primaryObject, secondaryObject, name, placeholder, taskTemplate, tips, bigForm }) => {
    const changeHandler = e => {
        e.preventDefault()
        formFunction(e.target.value)
    }
    let primaryText = primaryObject ? primaryObject : "(primary)";
    let secondaryText = secondaryObject ? secondaryObject : "(secondary)";
    let taskText = taskTemplate.replace("{primaryText}", primaryText).replace("{secondaryText}", secondaryText);
    return (
        <div className="form-container" >
            <h1 className="form-header">
                {name}
            </h1>
            {tips && <div className="tip-container">
                {
                    TipsCopy ?
                        TipsCopy.map((tip, index) => (
                            <p className="form-tip" key={index}>
                                <span style={{ fontWeight: "bold" }} >* </span>{tip}
                            </p>
                        ))
                        :
                        null
                }
            </div>}
            <div>
                <b>{taskText}</b>
            </div>
            <textarea
                className="description-form"
                onChange={changeHandler}
                value={formVal}
                rows={bigForm ? "7" : "2"}
                type="text"
                placeholder={placeholder}
            />
        </div>
    )
}
export default DescriptionForm;
