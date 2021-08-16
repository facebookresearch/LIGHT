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
    isSelected// Boolean determines whether button has been selected or not.
})=>{
// *Note - button does not have to have any selected class it will default to unselected if no isSelectedValue is provided
    return(
        <div className={isSelected ?  selectedContainer : unselectedContainer} onClick={selectFunction}>
            <p className={isSelected ? selectedText : unselectedText}>
                {name.toUpperCase()}
            </p>
        </div>
    )
}
export default TaskButton;
