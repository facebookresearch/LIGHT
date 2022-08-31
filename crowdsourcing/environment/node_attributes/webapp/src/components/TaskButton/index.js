/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React from "react";
//STYLE
import "./styles.css"

// TaskButton - an all purpose, customizable button.
const TaskButton = ({
    unselectedContainer, //default style for the button container
    selectedContainer,// style of button container if there is a "selected" state the button can be
    unselectedText,// default style for button label
    selectedText,// style of label if button is selected.
    name, // text in label
    selectFunction, // function that is invoked when button is clicked
    isSelected // boolean that dictates selected styles being applied
})=>{

    return(
        <div className={isSelected ?  selectedContainer : unselectedContainer} onClick={selectFunction}>
            <p className={isSelected ? selectedText : unselectedText} style={{marginBottom:"0px"}}>
                {name.toUpperCase()}
            </p>
        </div>
    )
}
export default TaskButton;
