import React, {useState} from "react";
//CUSTOM COMPONENTS

const TaskButton = ({
    unselectedContainer,
    selectedContainer,
    unselectedText,
    selectedText,
    name,
    selectFunction,
    isSelected
})=>{

    return(
        <div className={isSelected ? unselectedContainer : selectedContainer} onClick={selectFunction}>
            <p className={isSelected ? unselectedText : selectedText}>
                {name.toUpperCase()}
            </p>
        </div>
    )
}
export default TaskButton;
