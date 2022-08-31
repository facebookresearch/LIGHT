/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React from "react";

const Header = ({headerText})=>{
    return(
        <div className="header">
            <h1 className="header__text">{headerText}</h1>
        </div>
    )
}

export default Header;
