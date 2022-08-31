/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React, { useState } from "react";
//CUSTOM COMPONENTS
import DropdownSelect from "../../DropdownSelect";

// fieldrow - row with styled form label and input to the right of it.  Input is "fed" into field question.  This is for question with multiple short inputs.
const FieldRow = ({
    field, //Object with name and value attributes
    dropdown, // boolean value signalling whether field is a dropdown or not
    options, //  Options in the dropdown an array of objects which have name and val attributes
    changeFunction, //function that updates the field question state
    defaultValue,
    disabled
}) => {
    //field local state
    const [fieldVal, setFieldVal] = useState(defaultValue ? defaultValue : "");
    //updates state in field question component
    const changeHandler = e => {
        e.preventDefault()
        setFieldVal(e.target.value)
        changeFunction(e.target.value)
    }
    // if dropdown is true renders field with dropdown input
    if (dropdown) {
        return (
            <div className="fieldrow-container" >
                <div className="fieldrow-container__section--half" style={{ justifyContent: "flex-end" }} >
                    <div className="field-container">
                        <p className="field-text">
                            {field.name.toUpperCase()}
                        </p>
                    </div>
                </div>
                <div className="fieldrow-container__section--half" style={{ justifyContent: "flex-start" }}>
                {disabled ?
                        <p className="fieldanswer-text" style={{ borderStyle: "none", paddingLeft: "5px" }}>{fieldVal}</p>
                        :
                        <DropdownSelect
                            options={options}
                            selectFunction={changeHandler}
                        />}
                </div>
            </div>
        )
    } else {
        //if dropdown if false renders field with text input
        return (
            <div className="fieldrow-container" >
                <div className="fieldrow-container__section--half" style={{ justifyContent: "flex-end" }}>
                    <div className="field-container">
                        <p className="field-text">
                            {field.name.toUpperCase()}
                        </p>
                    </div>
                </div>
                <div className="fieldrow-container__section--half" style={{ justifyContent: "flex-start" }} >
                    <div className="fieldanswer-container">
                        {disabled ?
                            <p className="fieldanswer-text" style={{borderStyle:"none", paddingLeft:"5px" }}>{fieldVal}</p>
                            :
                            <input
                                className="fieldanswer-text"
                                onChange={changeHandler}
                                value={fieldVal}
                            />}

                    </div>
                </div>
            </div>
        )
    }
}
export default FieldRow;
