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
  isButton,
}) => {
  const [isCurrentStep, setIsCurrentStep] = useState(false);
  const [typedText, setTypedText] = useState("");
  let textClass = "text-white";
  if (isCurrentStep === true && isButton === true) {
    textClass = "text-green-200 hover:text-green-50"
  } else if (isCurrentStep === true) { // but not button
    textClass = "text-white"
  } else if (isButton === true) { // but not current step
    textClass = "text-green-800"
  } else { // not button and not current step
    textClass = "text-gray-500"
  }

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
    if (text.length === typedText.length && !isButton) {
      welcomeStepAdvancementHandler();
    }
    return () => clearTimeout(timeout);
  }, [typedText]);

  const clickHandler = () => {
    welcomeStepAdvancementHandler();
  };

  /*--------------- HANDLERS ----------------*/

  return (
    <div className={textClass} onClick={isButton && isCurrentStep ? clickHandler : null} >
      <p>{typedText}</p>
    </div>
  );
};

export default TypewriterText;
