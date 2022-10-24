/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React, { useState, useEffect } from "react";

import LandingAppCopy from "../../LandingAppCopy";
const { terminalTypingSpeed } = LandingAppCopy;

const TypewriterText = ({
  text,
  textStep,
  welcomeStep,
  welcomeStepAdvancementHandler,
}) => {
  const [isCurrentStep, setIsCurrentStep] = useState(false);
  const [typedText, setTypedText] = useState("");

  /*--------------- LIFECYLCLE ----------------*/
  useEffect(() => {
    if (welcomeStep === textStep || welcomeStep === textStep + 1) {
      setIsCurrentStep(true);
    } else {
      setIsCurrentStep(false);
    }
  }, [welcomeStep]);
  useEffect(() => {
    const timeout = setTimeout(() => {
      setTypedText(text.slice(0, typedText.length + 1));
    }, terminalTypingSpeed);
    if (text.length === typedText.length) {
      welcomeStepAdvancementHandler();
    }
    return () => clearTimeout(timeout);
  }, [typedText]);
  /*--------------- HANDLERS ----------------*/

  return (
    <div className={`${isCurrentStep ? "text-white" : "text-gray-500"}`}>
      <p>{typedText}</p>
    </div>
  );
};

export default TypewriterText;
