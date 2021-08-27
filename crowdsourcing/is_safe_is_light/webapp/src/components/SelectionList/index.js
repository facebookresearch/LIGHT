//REACT
import React, {useState} from "react";
//STYLE
import "./styles.css";
//CUSTOM COMPONENTS
import SelectionListItem from "./SelectionListRow";

// SelectionList - A container for each selection
const SelectionList = ({
    selection
})=>{

    return(
        <div className="selectionlist-container">
            {
                selection.length ?
                selection.map(selectionItem =><SelectionListItem item={selectionItem}/>)
                :
                null
            }
        </div>
    )
}
export default SelectionList;
