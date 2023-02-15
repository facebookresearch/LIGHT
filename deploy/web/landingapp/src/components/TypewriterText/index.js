/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React, { useState, useEffect } from "react";
/* COPY */
import LandingAppCopy from "../../LandingAppCopy";
const { terminalTypingSpeed } = LandingAppCopy;

// TypewriterText - Renders text as thought being typed out at the speed of the terminalTypingSpeed set in the copy file
const TypewriterText = ({
  text,
  textStep,
  welcomeStep,
  welcomeStepAdvancementHandler,
  isButton,
}) => {
  /*--------------- LOCAL STATE ----------------*/
  const [isCurrentStep, setIsCurrentStep] = useState(false);
  const [typedText, setTypedText] = useState("");

  let textClass = "text-white";
  if (isCurrentStep === true && isButton === true) {
    textClass = "text-green-200 hover:text-green-50";
  } else if (isCurrentStep === true) {
    // but not button
    textClass = "text-white";
  } else if (isButton === true) {
    // but not current step
    textClass = "text-green-800";
  } else {
    // not button and not current step
    textClass = "text-gray-500";
  }

  /*--------------- LIFECYLCLE ----------------*/
  //Checks the welcome step and sets the styles and interactvity based on that confirmation
  useEffect(() => {
    if (welcomeStep === textStep || welcomeStep === textStep + 1) {
      setIsCurrentStep(true);
    } else {
      setIsCurrentStep(false);
    }
  }, [welcomeStep]);

  //renders text and moves on to next welcome step after all text in copy has been "typed"
  useEffect(() => {
    const timeout = setTimeout(() => {
      setTypedText(text.slice(0, typedText.length + 1));
    }, terminalTypingSpeed);
    if (text.length === typedText.length && !isButton) {
      welcomeStepAdvancementHandler();
    }
    return () => clearTimeout(timeout);
  }, [typedText]);
  /*--------------- HANDLERS ----------------*/
  //Upon click of specific text continues to next step of welcomeSteps state
  const clickHandler = () => {
    welcomeStepAdvancementHandler();
  };

  return (
    <div
      className={textClass}
      onClick={isButton && isCurrentStep ? clickHandler : null}
    >
      <p className="text-s md:text-base lg:text-2xl xl:text-3xl 2xl:text-4xl">
        {typedText}
      </p>
    </div>
  );
};

export default TypewriterText;
