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
    color, // manually set color
    name,// Button label text
    selectFunction,// Button onClick function
    isSelected// Boolean determines whether button has been selected or not.
}) => {
    let modifyBoxColorStyle = {};
    if (color !== undefined) {
        if (isSelected) {
            modifyBoxColorStyle.backgroundColor = color;
        } else {
            modifyBoxColorStyle.borderColor = color;
        }
    }
    let modifyTextColorStyle = {};
    if (color !== undefined) {
        if (!isSelected) {
            modifyTextColorStyle.color = color;
        }
    }
    // *Note - button does not have to have any selected class it will default to unselected if no isSelectedValue is provided
    return (
        <div className={isSelected ? selectedContainer : unselectedContainer} onClick={selectFunction}
        style={modifyBoxColorStyle}>
            <p className={isSelected ? selectedText : unselectedText} style={modifyTextColorStyle}>
                {name.toUpperCase()}
            </p>
        </div>
    )
}
export default TaskButton;
