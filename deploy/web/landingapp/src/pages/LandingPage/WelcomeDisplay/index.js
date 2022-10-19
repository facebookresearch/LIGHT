/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React, { useState } from "react";
/* CUSTOM COMPONENTS */
import TerminalEntry from "./TerminalEntry";

const WelcomeDisplay = ({ terminalDialogue, loginStepIncreaseHandler }) => {
  const [terminalInput, setTerminalInput] = useState("");
  /*--------------- HANDLERS ----------------*/
  const terminalInputChangeHandler = (e) => {
    let updatedValue = e.target.value;
    setTerminalInput(updatedValue);
  };

  const terminalSubmissionHandler = () => {
    if (terminalInput === "y") {
      loginStepIncreaseHandler();
    } else {
      setTerminalInput("");
    }
  };

  return (
    <div className="">
      {terminalDialogue.map((entry, index) => (
        <TerminalEntry text={entry.text} highlighted={entry.highlighted} />
      ))}
      <input
        onChange={terminalInputChangeHandler}
        value={terminalInput}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            terminalSubmissionHandler();
          }
        }}
      />
    </div>
  );
};

export default WelcomeDisplay;

// "If  > “Yes”: continue to pre-login flow";
// "If  > “No”: ";
