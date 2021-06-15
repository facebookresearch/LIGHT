import React, {useState} from "react";

import Dropdown from 'react-bootstrap/Dropdown'

const DropdownSelect = ({options})=>{
    const [selectedOption, setSelectedOption]= useState("Select Location")
    const selectHandler = (selection)=>{
        setSelectedOption(selection)
    }
    console.log("OPTIONS", options)
    return(
    <div>
        <select name="select location" id="locations">
          {
            options.map(option =><option value={option}>{option}</option>)
          }
        </select>
    </div>
    )
}
export default DropdownSelect;
