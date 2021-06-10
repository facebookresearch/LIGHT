import React, {useState} from "react";

import Dropdown from 'react-bootstrap/Dropdown'

const DropdownSelect = ({options})=>{
    const [selectedOption, setSelectedOption]= useState("Select Location")
    const selectHandler = (selection)=>{
        setSelectedOption(selection)
    }
    return(
    <Dropdown>
        <Dropdown.Toggle variant="success" id="dropdown-basic">
            Dropdown Button
        </Dropdown.Toggle>

        <Dropdown.Menu>
            {
            options.length ?
            options.map((optionName, index)=><Dropdown.Item key={index} onClick={()=>}>{optionName}</Dropdown.Item>)
            :
            null
            }
        </Dropdown.Menu>
    </Dropdown>
    )
}
