import React, {useState} from "react";
import Dropdown from 'react-bootstrap/Dropdown'

import "./styles.css"

const DropdownSelect = ({options})=>{
    const [selectedOption, setSelectedOption]= useState("Select Location")
    const selectHandler = (selection)=>{
        setSelectedOption(selection)
    }
    console.log("OPTIONS", options)
    return(
    <div className="dropdown-container">
        <select className="dropdown-select" id="locations">
          <option  className="dropdown-option" value="Select Location" selected>Select Location</option>
          {
            options.map((option, index) =><option key={index} className="dropdown-option" value={option}>{option}</option>)
          }
        </select>
    </div>
    )
}
export default DropdownSelect;
