
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React from "react";
//STYLING
import "./styles.css";
// ICONS
import { BsInfoCircle } from "react-icons/bs";


// InfoIcon - renders an info icon
const InfoIcon = ({dark})=><BsInfoCircle className={dark? "info-icon__dark" :"info-icon"} />

export default InfoIcon ;
