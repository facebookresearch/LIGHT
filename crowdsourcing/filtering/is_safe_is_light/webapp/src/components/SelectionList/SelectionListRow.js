
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
