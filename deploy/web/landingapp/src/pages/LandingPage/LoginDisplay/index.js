/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, { useState } from "react";

import "./styles.css";

const LoginDisplay = ({ loginStepIncreaseHandler }) => {
  /*--------------- LOCAL STATE ----------------*/
  const [legalAgreement, setLegalAgreement] = useState(false);
  /*--------------- HANDLERS ----------------*/
  const loginHandler = (e) => {
    e.preventDefault();
    loginStepIncreaseHandler();
  };
  const toggleAgreement = () => {
    let updateAgreement = !legalAgreement;
    setLegalAgreement(updateAgreement);
  };
  return (
    <div className="w-full h-full flex items-center justify-center flex-col">
      <h1 className="text-white underline">LOGIN</h1>
      <div className="w-full flex flex-row justify-center items-start w-3/4">
        <label className="cursor-pointer label">
          <input
            type="checkbox"
            checked={legalAgreement}
            onChange={toggleAgreement}
            className="checkbox checkbox-accent"
            checkbox-lg
          />
          <span className="text-white">
            By clicking “sign up” below [OR “log-in”/”continue” - whichever text
            will appear on the call to action button], you are agreeing to the
            LIGHT Supplemental Terms of Service and Meta Platform, Inc.'s Data
            Policy and you consent for us to use a cookie to track your
            logged-in status across the LIGHT site. Learn more about how we use
            cookies here. In order to play LIGHT, you are required to login via
            your valid Facebook account. You must be at least 18 years of age or
            older and reside in the United States in order to play.{" "}
          </span>
        </label>
      </div>
      <div className="w-full flex justify-center items-center">
        {legalAgreement ? (
          <button
            disabled={!legalAgreement}
            className="login-form__submit"
            onClick={loginHandler}
          >
            Sign In With Facebook
          </button>
        ) : null}
        {/* <form action="/auth/fblogin?next={{next}}" method="get">
             <input
               className="login-form__submit"
               type="submit"
               value="Sign In With Facebook"
             />
           </form> */}
      </div>
    </div>
  );
};

export default LoginDisplay;
