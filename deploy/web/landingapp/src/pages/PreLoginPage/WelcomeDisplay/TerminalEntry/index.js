/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React from "react";
/* CUSTOM COMPONENTS */
import TypewriterText from "../../../../components/TypewriterText";

//TerminalEntry - Renders container component for terminal style entries both copy and interactive "buttons"
const TerminalEntry = ({
  text,
  textStep,
  welcomeStep,
  welcomeStepAdvancementHandler,
  isButton,
}) => {
  return (
    <>
      {textStep <= welcomeStep ? (
        <TypewriterText
          text={isButton ? "> " + text : text}
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
