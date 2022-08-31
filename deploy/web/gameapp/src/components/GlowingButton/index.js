/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";

//GlowingButton - Renders button that glows with pulse animation on hover or activation.
const GlowingButton = ({ label, buttonFunction }) => {
  return (
    <div className="glowing-button" onClick={buttonFunction}>
      <span className="glowingbutton-text">{label}</span>
    </div>
  );
};

export default GlowingButton;
