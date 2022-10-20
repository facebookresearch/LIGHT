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
    <div className="w-full h-full flex items-center justify-center flex-col font-mono">
      <h1 className="text-white underline">LOGIN</h1>
      <div className="w-full flex flex-row justify-center items-start w-3/4">
        <label className="cursor-pointer label">
          <input
            type="checkbox"
            checked={legalAgreement}
            onChange={toggleAgreement}
            className="checkbox checkbox-accent checkbox-lg"
            checkbox-lg
          />
          <span className="text-white text-3xl">
            By clicking “sign up” below [OR “log-in”/”continue” - whichever text
            will appear on the call to action button], you are agreeing to the
            <a
              className="text-blue-400 hover:text-green-100 active:text-green-50"
              target="_blank"
              href={
                "https://docs.google.com/document/d/1RR5vo-ith7lBX--Pk7ErgD0gyjaktY-DR_SSsdLWEuc/edit#"
              }
            >
              {" "}
              LIGHT Supplemental Terms of Service and Meta Platform
            </a>
            , Inc.'s
            <a
              className="text-blue-400 hover:text-green-100 active:text-green-50"
              target="_blank"
              href="https://www.facebook.com/about/privacy/update"
            >
              {" "}
              Data Policy{" "}
            </a>
            and you consent for us to use a cookie to track your logged-in
            status across the LIGHT site. Learn more about how we use cookies{" "}
            <a
              className="text-blue-400 hover:text-green-100 active:text-green-50"
              target="_blank"
              href="https://www.facebook.com/policies/cookies/"
            >
              here
            </a>
            . In order to play LIGHT, you are required to login via your valid
            Facebook account. You must be at least 18 years of age or older and
            reside in the United States in order to play.{" "}
          </span>
        </label>
      </div>
      <div className="w-full flex justify-center items-center">
        {legalAgreement ? (
          <button
            disabled={!legalAgreement}
            className="text-3xl text-green-200 border-2 p-1 border-green-200 rounded"
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
