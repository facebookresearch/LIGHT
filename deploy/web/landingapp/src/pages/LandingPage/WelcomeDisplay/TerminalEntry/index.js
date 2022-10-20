/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React from "react";

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
          <p
            className={`pb-4 ${highlighted ? "text-green-200" : "text-white"}`}
          >
            {text}
          </p>
        ) : (
          <div className="flex flex-row">
            <span className="text-green-200"> {">"}</span>
            <input
              className="focus:outline-none bg-transparent text-green-200 border-transparent border-0"
              autoFocus={welcomeStep === textStep}
              disabled={welcomeStep !== textStep}
              value={text}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  welcomeStepAdvancementHandler();
                }
              }}
            />
          </div>
        )
      ) : null}
    </>
  );
};

export default TerminalEntry;
