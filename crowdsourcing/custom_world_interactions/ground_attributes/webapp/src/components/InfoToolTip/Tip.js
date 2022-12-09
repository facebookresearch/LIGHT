/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React from "react";

// Tip - html rendered by tool tip
const Tip = ({
    tutorialCopy//Text that will be displayed in the tool tip
})=>{
    return (
        <div className="tip-container">
            <p className="tip-text">
                {tutorialCopy}
            </p>
        </div>
    )
}

export default Tip ;
