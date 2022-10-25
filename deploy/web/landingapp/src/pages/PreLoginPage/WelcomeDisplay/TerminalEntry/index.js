/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React from "react";
/* CUSTOM COMPONENTS */
import TypewriterText from "../../../../components/TypewriterText";

const TerminalEntry = ({
  text,
  textStep,
  welcomeStep,
  welcomeStepAdvancementHandler,
  isButton,
}) => {
  console.log("TEXT STEP:  ", textStep, "WELCOME STEP:  ", welcomeStep);
  return (
    <>
      {textStep <= welcomeStep ? (
        <TypewriterText
          text={(isButton) ? "> " + text : text}
          textStep={textStep}
          welcomeStep={welcomeStep}
          welcomeStepAdvancementHandler={welcomeStepAdvancementHandler}
          isButton={isButton}
        />
      ) : null}
    </>
  );
};

export default TerminalEntry;
