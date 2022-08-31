
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* ICONS */
import { BsFillPlusCircleFill } from 'react-icons/bs';
//IconButton - 
const CreateWorldButton = ({ clickFunction }) => {
  return (
    <div className="createworldbutton-container" onClick={clickFunction}>
        <BsFillPlusCircleFill className="createworld-icon" />
        <p style={{ margin: 0, padding: "0 0 0 3px" }} className="createworldbutton-text">
           CREATE NEW 
        </p>
    </div>
  );
};

export default CreateWorldButton;