//REACT
import React from "react";
//STYLING
import "./styles.css"
//ICONS
import { ImCheckboxChecked } from "react-icons/im";
import { ImCheckboxUnchecked } from "react-icons/im";
//Checkbox - takes completion condition as isComplete prop and displays either checked or unchecked.
const Checkbox = ({isComplete}) => {
    return (
        <div className="checkbox-container">
        {
            isComplete ?
            <ImCheckboxChecked/>
            :
            <ImCheckboxUnchecked/>
        }
        </div>
    );
}

export default Checkbox ;
