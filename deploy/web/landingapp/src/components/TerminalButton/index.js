/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React, { useState, useEffect } from "react";

// TerminalButton - renders interactive, "terminal" styled "buttons"
//  Styles them based on the current step in the welcome progression
const TerminalButton = ({
  text,
  textStep,
  welcomeStep,
  welcomeStepAdvancementHandler,
}) => {
  /*--------------- LOCAL STATE ----------------*/
  const [isCurrentStep, setIsCurrentStep] = useState(false);
  /*--------------- LIFECYLCLE ----------------*/
  //Checks the welcome step and sets the styles and interactvity based on that confirmation
  useEffect(() => {
    if (welcomeStep === textStep) {
      setIsCurrentStep(true);
    } else {
      setIsCurrentStep(false);
    }
  }, [welcomeStep]);

  /*--------------- HANDLERS ----------------*/
  const clickHandler = () => {
    welcomeStepAdvancementHandler();
  };
  return (
    <div
      className={` ${
        isCurrentStep ? "text-green-200 hover:text-green-50" : "text-green-800"
      }`}
      onClick={isCurrentStep ? clickHandler : null}
    >
      {"> " + text}
    </div>
  );
};

export default TerminalButton;
