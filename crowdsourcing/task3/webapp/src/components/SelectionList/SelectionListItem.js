//REACT
import React, {useState} from "react";
//STYLE
import "./styles.css"

// SelectionListItem - Row in selection list.
const SelectionListItem = ({
    item
})=>{
    const {name, description} = item;
    return(
        <div className="selection-row">
           <div className="selection-name__container">
                <p className="selection-name__text">
                    {name}
                </p>
           </div>
           <div className="selection-description__container" >
                <p className="selection-description__text">
                    {description}
                </p>
           </div>
        </div>
    )
}
export default SelectionListItem;
