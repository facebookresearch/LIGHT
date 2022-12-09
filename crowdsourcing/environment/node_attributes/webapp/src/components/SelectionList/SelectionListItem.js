/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
