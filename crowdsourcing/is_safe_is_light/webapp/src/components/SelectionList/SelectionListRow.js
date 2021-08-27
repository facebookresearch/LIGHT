//REACT
import React, {useState} from "react";
//STYLE
import "./styles.css"

// SelectionListRow - Row in selection list.
const SelectionListRow = ({
    selectionNode
})=>{
    const {sentence} = selectionNode;
    return(
        <div className="selection-row">
           <div className="selection-name__container">
                <p className="selection-name__text">
                    {sentence}
                </p>
           </div>
        </div>
    )
}
export default SelectionListRow;
