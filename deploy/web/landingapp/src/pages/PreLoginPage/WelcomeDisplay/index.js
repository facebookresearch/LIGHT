/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React, { useState } from "react";
import { Link, useHistory } from "react-router-dom";
/* CUSTOM COMPONENTS */
import TerminalEntry from "./TerminalEntry";
/* STYLES */
import "./styles.css";

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
    loginStepIncreaseHandler();
    setTerminalInput("");
  };

  const terminalRejectionHandler = () => {
    setRejectedAgreement(true);
    welcomeStepAdvancementHandler();
  };

  const welcomeStepAdvancementHandler = () => {
    let nextStep = welcomeStep + 1;
    setWelcomeStep(nextStep);
  };

  return (
    <div className="ml-16 w-1/2 font-mono text-2xl flex items-start flex-col justify-start">
      <h1 className="text-white font-mono">Landing in LIGHT</h1>
      {terminalDialogue.map((entry, index) => (
        <TerminalEntry
          text={entry.text}
          isButton={entry.highlighted}
          textStep={entry.step}
          welcomeStep={welcomeStep}
          welcomeStepAdvancementHandler={welcomeStepAdvancementHandler}
        />
      ))}
      {welcomeStep >= 5 ? (
        <div>
          {rejectedAgreement ? null : (
            <TerminalEntry
              text={"YES"}
              textStep={5}
              welcomeStep={welcomeStep}
              welcomeStepAdvancementHandler={terminalSubmissionHandler}
              isButton={true}
            />
          )}
          <TerminalEntry
            text={"NO"}
            textStep={5}
            welcomeStep={welcomeStep}
            welcomeStepAdvancementHandler={terminalRejectionHandler}
            isButton={true}
          />
        </div>
      ) : null}

      {rejectedAgreement ? (
        <>
          <p className="text-white">{rejectionTerminalDialogue}</p>
        </>
      ) : null}
    </div>
  );
};

export default WelcomeDisplay;
