/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";

//ProgressBar - Renders XP progress towards next level (Hard coded in Landing App)
const ProgressBar = () => {
  return (
    <progress
      className="progress progress-warning w-full h-4 border-solid border-white border-2"
      value={0}
      max="100"
    />
  );
};

export default ProgressBar;
