import React, {useState} from "react";

import "./styles.css"
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
        <div className={isSelected ?  selectedContainer : unselectedContainer} onClick={selectFunction}>
            <p className={isSelected ? selectedText : unselectedText}>
                {name.toUpperCase()}
            </p>
        </div>
    )
}
export default TaskButton;
