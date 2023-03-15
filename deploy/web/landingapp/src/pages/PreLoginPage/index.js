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

  //Navigates user to intro page upon completion of login
  useEffect(() => {
    if (loginStep >= 2) {
      history.push("/intro");
    }
  }, [loginStep]);

  //checks to see if player has completed tutorial previously by querying backend then sends player to game if backend would not redirect them back to the tutorial
  useEffect(() => {
    let currentUrl = window.location.href
    let willRedirect;
    fetch("/play").then((response) => {
      console.log(response);
      willRedirect = response.redirected;
      if (!willRedirect) {
        window.location.href = currentUrl+"play";
      }
    });
  }, []);

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
      <div className="__welcome-footer__ w-full h-fit text-white">
        <div className="p-2">
          {" "}
          <Link
            to="tos"
            className="cursor-pointer underline hover:text-green-100 mr-2"
          >
            Terms
          </Link>{" "}
          <Link
            to="faq"
            className="cursor-pointer underline hover:text-green-100"
          >
            {" "}
            FAQ{" "}
          </Link>
        </div>
      </div>
    </div>
  );
};

export default PreLoginPage;
