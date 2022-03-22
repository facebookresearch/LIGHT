//REACT
import React, {useState} from "react";
//STYLING
import "./styles.css"
//DropdownSelect - component takes options and function connecting it to payload state as props
const DropdownSelect = ({options, selectFunction, selectedValue})=>{
  /*------STATE------*/
  // selected value in the dropdown
    // const [selectedOption, setSelectedOption]= useState("Select Location")
    const [selectedOption, setSelectedOption]= useState(selectedValue)
  //State to disable default option which has no value upon user interacting with dropdown
    const [firstSelect, setFirstSelect] = useState(false)
  /*------HANDLERS------*/
  //Upon selection updates both the localstate and the payload state.
    const selectHandler = (selection)=>{
      setFirstSelect(true)
      // setSelectedOption(selection.value)
      setSelectedOption(selection.target.value)
      selectFunction(selection.target.value)
    }
    console.log('drop down: ')
    console.log(selectedOption)
    return(
    <div className="dropdown-container">
        <select className="dropdown-select" id="locations" onChange={selectHandler} value={selectedOption} disabled={true}>
          <option  className="dropdown-option" disabled={firstSelect} value={selectedOption} >{selectedOption}</option>
          {
            options.map((option, index) =><option key={index} className="dropdown-option" value={option.val}>{option.name}</option>)
          }
        </select>
    </div>
    )
}
export default DropdownSelect;
