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
/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* CONFIG */
import CONFIG from "../../../config";



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
  //LOGIN PATHS
  // const nextLoc = new URLSearchParams(window.location.search).get("next");
  // var targetStr = null;
  // if (CONFIG.login == "fb") {
  //   targetStr = "/auth/fblogin" + (nextLoc !== null ? "?next=" + nextLoc : "");
  // } else {
  //   targetStr = "/login";
  // }
  //HANDLERS
  const loginSubmissionHandler = (event)=>{
    event.preventDefault();
    let targetStr = null
    if (CONFIG.login == "fb") {
      targetStr = "/auth/fblogin"
    } else {
      targetStr = "/login";
    }
    console.log("TARGET STRING:  ", targetStr)
    window.location.href = targetStr;
    };

  return (
    <div className=" flex-col font-mono w-full overflow-y-scroll justify-center items-center h-full flex ">
      <h1 className="text-white underline font-bold text-2xl md:text-3xl lg:text-4xl xl:text-6xl mb-1">
        Login to LIGHT
      </h1>
      <div className=" flex flex-row justify-center items-center w-5/6 text-s md:text-base lg:text-lg xl:text-xl">
        <label className="cursor-pointer label flex flex-row">
          <CheckBox
            checkStatus={legalAgreement}
            checkFunction={toggleAgreement}
          />
          <span className="text-white">
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
        <Tooltip
          className="text-white bg-gray-50"
          html={
            <div className="w-30 h-30 p-3 border-solid border-black rounded bg-white text-black">
              <p> Please check the box to agree to the terms </p>
            </div>
          }
          position="top"
          trigger="mouseenter"
          size="big"
          disabled={!!legalAgreement}
          style={{ color: "white", backgroundColor: "black" }}
        >
          <div>
            <button
              className={`${
                legalAgreement
                  ? "text-green-200 border-green-200 hover:text-blue-400 hover:border-blue-400"
                  : "text-gray-200 border-gray-200"
              } border-2 p-1 rounded`}
              onClick={loginSubmissionHandler}
              disabled={!legalAgreement}
            >
              Sign In With Facebook
            </button>
          </div>
        </Tooltip>
      </div>
    </div>
  );
};

export default LoginDisplay;
