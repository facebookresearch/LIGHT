
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React from "react";
//Styling
import "./styles.css"

//TaskButton - All purpose button for task
const TaskButton = ({
    unselectedContainer,// css class for button when not selected
    selectedContainer,// css class for button when selected
    unselectedText,// css class for button text when not selected
    selectedText,// css class for button text when selected
    name,// Button label text
    selectFunction,// Button onClick function
    isSelected,// Boolean determines whether button has been selected or not.
    disabled // Boolean determines whether this button is actually clickable (in which case change css)
})=>{
// *Note - button does not have to have any selected class it will default to unselected if no isSelectedValue is provided
    const radiusStyle = disabled ? {borderRadius: "10px 10px 10px 10px", boxShadow:"none"} : {};
    return(
        <div style={radiusStyle} className={isSelected ?  selectedContainer : unselectedContainer} onClick={selectFunction}>
            <p className={isSelected ? selectedText : unselectedText}>
                {name.toUpperCase()}
            </p>
        </div>
    )
}
export default TaskButton;
