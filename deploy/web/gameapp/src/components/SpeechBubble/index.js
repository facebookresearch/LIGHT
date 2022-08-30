/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

import "./styles.css";

const SpeechBubble = (props) => {
  const { text } = props;
  return (
    <div className="speechbubble-container">
      <div className="speechbubble left">
        <div className="speechbubble-tail" />
        <p className="speechbubble-text">{text ? text.toUpperCase() : null}</p>
      </div>
    </div>
  );
};

export default SpeechBubble;
