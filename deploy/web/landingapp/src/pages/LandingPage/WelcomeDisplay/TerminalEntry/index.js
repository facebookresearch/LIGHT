/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React from "react";
/* CUSTOM COMPONENTS */
import TypewriterText from "../../../../components/TypewriterText";
import TerminalButton from "../../../../components/TerminalButton";

const TerminalEntry = ({
  text,
  highlighted,
  textStep,
  welcomeStep,
  welcomeStepAdvancementHandler,
}) => {
  console.log("TEXT STEP:  ", textStep, "WELCOME STEP:  ", welcomeStep);
  return (
    <>
      {textStep <= welcomeStep ? (
        !highlighted ? (
          <TypewriterText
            text={text}
            welcomeStepAdvancementHandler={welcomeStepAdvancementHandler}
          />
        ) : (
          <TerminalButton
            text={text}
            textStep={textStep}
            welcomeStep={welcomeStep}
            welcomeStepAdvancementHandler={welcomeStepAdvancementHandler}
          />
        )
      ) : null}
    </>
  );
};

export default TerminalEntry;
