
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React from "react";
//STYLING
import "./styles.css"
//ICONS
import { ImCheckboxChecked } from "react-icons/im";
import { ImCheckboxUnchecked } from "react-icons/im";
//Checkbox - takes completion condition as isComplete prop and displays either checked or unchecked.
const Checkbox = ({isComplete}) => {
    return (
        <div className="checkbox-container">
        {
            isComplete ?
            <ImCheckboxChecked/>
            :
            <ImCheckboxUnchecked/>
        }
        </div>
    );
}

export default Checkbox ;
