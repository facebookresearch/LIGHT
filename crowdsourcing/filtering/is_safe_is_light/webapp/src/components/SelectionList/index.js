
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
                selection.map((selectionItem, index) =><SelectionListItem key={index} number={index+1} selectionNode={selectionItem}/>)
                :
                null
            }
        </div>
    )
}
export default SelectionList;
