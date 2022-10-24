/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React, { useState, useEffect } from "react";
import { Link, useHistory } from "react-router-dom";
/* CUSTOM COMPONENTS */
import WelcomeDisplay from "./WelcomeDisplay";
import LoginDisplay from "./LoginDisplay";
/* COPY */
import LANDINGAPPCOPY from "../../LandingAppCopy";

const PreLoginPage = () => {
  const { terminalDialogue, rejectionTerminalDialogue } = LANDINGAPPCOPY;
  let history = useHistory();
  /*---------------LOCAL STATE----------------*/
  //UI INTRO STEP
  const [loginStep, setLoginStep] = useState(0);
  //CHAT DISPLAY REF
  const chatContainerRef = React.useRef(null);
  /*--------------- HANDLERS ----------------*/
  const loginStepIncreaseHandler = () => {
    let nextStep = loginStep + 1;
    setLoginStep(nextStep);
  };
  /*-------------- LIFECYCLE ----------------*/

  useEffect(() => {
    if (loginStep >= 2) {
      history.push("/intro");
    }
  }, [loginStep]);

  return (
    <div className="flex w-full h-full justify-center items-center flex-col">
      {loginStep === 0 ? (
        <div className="flex w-full h-full justify-center items-center">
          <WelcomeDisplay
            terminalDialogue={terminalDialogue}
            loginStepIncreaseHandler={loginStepIncreaseHandler}
            rejectionTerminalDialogue={rejectionTerminalDialogue}
          />
        </div>
      ) : null}
      {loginStep === 1 ? (
        <LoginDisplay loginStepIncreaseHandler={loginStepIncreaseHandler} />
      ) : null}
      <div className="__welcome-footer__ w-full h-fit"></div>
    </div>
  );
};

export default PreLoginPage;
