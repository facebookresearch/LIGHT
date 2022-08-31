/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";

//IconButton - 
const IconButton = ({ clickFunction, text }) => {
  return (
    <div className="iconbutton-container" onClick={clickFunction}>
      
    </div>
  );
};

export default IconButton;