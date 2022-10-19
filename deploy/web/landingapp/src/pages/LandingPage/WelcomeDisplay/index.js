/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React from "react";
/* CUSTOM COMPONENTS */
import TerminalEntry from "./TerminalEntry";

const WelcomeDisplay = ({ terminalDialogue, loginStepIncreaseHandler }) => {
  return (
    <div className="">
      {terminalDialogue.map((entry, index) => (
        <TerminalEntry text={entry.text} highlighted={entry.highlighted} />
      ))}
      <input />
    </div>
  );
};

export default WelcomeDisplay;

// "If  > “Yes”: continue to pre-login flow";
// "If  > “No”: ";
