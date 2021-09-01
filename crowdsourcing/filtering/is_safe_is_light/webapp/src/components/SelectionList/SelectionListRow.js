//REACT
import React from "react";
//STYLE
import "./styles.css"

// SelectionListRow - Row in selection list.
const SelectionListRow = ({
    selectionNode,
    number
})=>{
    const {sentence} = selectionNode;
    return(
        <div className="selection-row">
           <div className="selection-name__container">
                <p className="selection-name__text">
                    {`${number}.  ${sentence}`}
                </p>
           </div>
        </div>
    )
}
export default SelectionListRow;
