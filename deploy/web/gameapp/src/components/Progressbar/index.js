/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React from "react";
/* STYLE */
import "./styles.css";

// ProgressBar component renders bar that fills as players gain xp based on percentage of current earned xp is of xp to level
const ProgressBar = ({ progressPercent }) => {
  return (
    <progress
      className="_progress-bar_ progress progress-warning w-full h-4 border-solid border-white border-2"
      value={progressPercent}
      max="100"
    />
  );
};

export default ProgressBar;
