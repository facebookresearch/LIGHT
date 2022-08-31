
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

import "./styles.css"

import Copy from "../../TaskCopy"

const {taskHeader} = Copy;

const Header = () => {
    return (
        <div className="header">
            <h1 className="header__text">{taskHeader}</h1>
        </div>
    );
}

export default Header ;
