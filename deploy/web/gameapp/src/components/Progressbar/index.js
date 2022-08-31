/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

import "./styles.css";

const ProgressBar = (props) => {
  const { bgcolor, percentCompleted, exp, nextLevel } = props;
  return (
    <div className="bar-container">
      <div
        className="bar-filler"
        style={{ width: `${percentCompleted}%`, backgroundColor: bgcolor }}
      ></div>
      <div className="bar-label__container">
        <span className="bar-label">{`${exp}/ ${nextLevel} EXP`}</span>
      </div>
    </div>
  );
};

export default ProgressBar;
