//REACT
import React, {useState} from "react";
//STYLE
import "./styles.css";
//CUSTOM COMPONENTS
import SelectionListItem from "./SelectionListItem";

// SelectionList - A container for each selection item and their description
const SelectionList = ({
    selection
})=>{

    return(
        <div className="selectionlist-container">
            {
                selection.length ?
                selection.map(selectionItem =><SelectionListItem item={selectionItem} key={'item-'+selectionItem.id}/>)
                :
                null
            }
        </div>
    )
}
export default SelectionList;
