/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React, { useState } from "react";
/* CUSTOM COMPONENTS */
import TerminalEntry from "./TerminalEntry";

const WelcomeDisplay = ({
  terminalDialogue,
  loginStepIncreaseHandler,
  rejectionTerminalDialogue,
}) => {
  /*--------------- LOCAL STATE ----------------*/
  const [terminalInput, setTerminalInput] = useState("");
  const [welcomeStep, setWelcomeStep] = useState(0);
  const [rejectedAgreement, setRejectedAgreement] = useState(false);
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

  const welcomeStepAdvancementHandler = () => {
    let nextStep = welcomeStep + 1;
    setWelcomeStep(nextStep);
  };

  return (
    <div className="ml-16">
      <h1 className="text-white">WELCOME TO LIGHT</h1>
      {terminalDialogue.map((entry, index) => (
        <TerminalEntry
          text={entry.text}
          highlighted={entry.highlighted}
          textStep={entry.step}
          welcomeStep={welcomeStep}
          welcomeStepAdvancementHandler={welcomeStepAdvancementHandler}
        />
      ))}
      {welcomeStep === 2 ? (
        <input
          className="focus:outline-none bg-transparent text-green-200 border-transparent border-0"
          onChange={terminalInputChangeHandler}
          disabled={welcomeStep !== 2}
          autoFocus={welcomeStep === 2}
          value={terminalInput}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              let answer = terminalInput[0];
              answer = answer.toLowerCase();
              if (answer === "y") {
                terminalSubmissionHandler();
              }
              if (answer === "n") {
                setRejectedAgreement(true);
                welcomeStepAdvancementHandler();
              }
            }
          }}
        />
      ) : null}
      {rejectedAgreement ? (
        <p className="text-white">{rejectionTerminalDialogue}</p>
      ) : null}
    </div>
  );
};

export default WelcomeDisplay;

// "If  > “Yes”: continue to pre-login flow";
// "If  > “No”: ";
