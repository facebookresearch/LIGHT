//REACT
import React, {useState} from "react";
//STYLING
import "./styles.css"

const DropdownSelect = ({options, selectFunction})=>{
    const [selectedOption, setSelectedOption]= useState("Select Location")
    const [firstSelect, setFirstSelect] =useState(false)
    const selectHandler = (selection)=>{
      console.log("DROPDOWN SELECTION:", selection.value,  selection.value !== "Select Location")
      setFirstSelect(true)
      setSelectedOption(selection.value)
      selectFunction(selection)
    }
    console.log("OPTIONS", options)
    return(
    <div className="dropdown-container">
        <select className="dropdown-select" id="locations" onChange={selectHandler} value={selectedOption}>
          <option  className="dropdown-option" disabled={firstSelect} value={"Select Location"} >Select Location</option>
          {
            options.map((option, index) =><option key={index} className="dropdown-option" value={option.val}>{option.name}</option>)
          }
        </select>
    </div>
    )
}
export default DropdownSelect;
