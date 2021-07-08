//REACT
import React, {useState} from "react";
//STYLING
import "./styles.css"
//DropdownSelect - takes options and function connecting it to payload state as props
const DropdownSelect = ({options, selectFunction})=>{
  // local state for the selected value in the dropdown
    const [selectedOption, setSelectedOption]= useState("Select Location")
  //State to disable default option which has no value upon user interacting with dropdown
    const [firstSelect, setFirstSelect] =useState(false)
  //Upon selection updates both the localstate and the payload state.
    const selectHandler = (selection)=>{
      setFirstSelect(true)
      setSelectedOption(selection.value)
      selectFunction(selection)
    }
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
