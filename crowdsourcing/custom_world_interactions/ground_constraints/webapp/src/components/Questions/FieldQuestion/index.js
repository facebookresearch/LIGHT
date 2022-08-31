
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React from "react";
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import FieldRow from "./FieldRow";

// FieldQuestion - a question who's answer is a form with multiple fields.  these fields can be text input or dropdown.
const FieldQuestion = ({
    question,//question text
    fields,//an array of objects with a string name attribute, a dropdown boolean attribute, and if boolean is true an array of options for the dropdown
    formFunction,// function that connects question answer to payload state.
    formState, // payload state
    disabled
})=>{
    //updates payload state with for inputs
    const ChangeHandler = (formName, formVal)=>{
        let updatedState = {...formState, [formName]:formVal}
        formFunction(updatedState)
    }
    return(
        <div className="fieldquestion-container" >
            <p className="fieldquestion-header">{question}</p>
            <div className="fieldlist-container">
                {
                    fields ?
                    fields.map((field, index)=>(
                    <FieldRow
                        key={index}
                        field={field}
                        dropdown={field.dropdown}
                        options={field.options}
                        defaultValue={field.value}
                        changeFunction={val=>ChangeHandler(field.name, val)}
                        disabled={disabled}
                        />
                        ))
                    :null
                }
            </div>
        </div>
    )
}
export default FieldQuestion;
