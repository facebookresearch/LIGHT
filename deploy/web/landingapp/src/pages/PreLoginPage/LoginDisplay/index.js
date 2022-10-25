/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React, { useState } from "react";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import CheckBox from "../../../components/CheckBox";

//LoginDisplay - renders Login agreement and login button
const LoginDisplay = () => {
  /*--------------- LOCAL STATE ----------------*/
  const [legalAgreement, setLegalAgreement] = useState(false);
  /*--------------- HANDLERS ----------------*/
  //toggleAgreement - toggles boolean value of legal agreement users must agree to in order to login
  const toggleAgreement = () => {
    let updateAgreement = !legalAgreement;
    setLegalAgreement(updateAgreement);
  };

  const nextLoc = new URLSearchParams(window.location.search).get("next");
  const targetStr =
    "/auth/fblogin" + (nextLoc !== null ? "?next=" + nextLoc : "");
  return (
    <div className="w-full h-full flex items-center justify-center flex-col font-mono">
      <h1 className="text-white underline text-4xl mb-1">Login to LIGHT</h1>
      <div className=" flex flex-row justify-center items-start w-3/4">
        <label className="cursor-pointer label flex flex-row">
          <CheckBox
            checkStatus={legalAgreement}
            checkFunction={toggleAgreement}
          />
          <span className="text-white text-2xl">
            By clicking “Sign in with Facebook” below, you are agreeing to the
            LIGHT
            <a
              className="text-blue-400 hover:text-green-100 active:text-green-50"
              target="_blank"
              href={"/tos"}
            >
              {" "}
              Supplemental Terms of Service{" "}
            </a>
            and Meta Platform, Inc.'s
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
        <form action={targetStr} method="get">
          <button
            className={`${
              legalAgreement
                ? "text-green-200 border-green-200 hover:text-blue-400 hover:border-blue-400"
                : "text-gray-200 border-gray-200"
            } border-2 p-1 rounded`}
            type="submit"
            disabled={!legalAgreement}
          >
            Sign In With Facebook
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginDisplay;
