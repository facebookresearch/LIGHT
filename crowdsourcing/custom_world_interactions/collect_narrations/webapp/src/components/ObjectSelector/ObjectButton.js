
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, {useState} from "react";
//CUSTOM COMPONENTS

const ObjectButton = ({name, selectFunction, isSelected})=>{

    return(
        <div className={isSelected ? "selectedbutton-container": "button-container"} onClick={selectFunction}>
            <p className={isSelected ? "selectedbutton-text": "button-text"}>
                {name.toUpperCase()}
            </p>
        </div>
    )
}
export default ObjectButton;
