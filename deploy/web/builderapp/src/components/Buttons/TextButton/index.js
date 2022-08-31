
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";

//TextButton - 
const TextButton = ({ clickFunction, text }) => {
  return (
    <div className="textbutton-container" onClick={clickFunction}>
      <p style={{ margin: 0, padding: 0 }} className="textbutton-text">
        {text}
      </p>
    </div>
  );
};

export default TextButton;