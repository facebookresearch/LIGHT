/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";

/* STYLES */
import "./styles.css";

/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* ICONS */
import { BsInfo } from "react-icons/bs";

//IconButton - Renders button that toggles help mode.
const IconButton = () => {
  return (
    <Tooltip title="HELP MODE" position="top">
      <BsInfo className={`iconbutton-icon`} />
    </Tooltip>
  );
};

export default IconButton;
