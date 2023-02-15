/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* REACT ROUTER */
import { Link } from "react-router-dom";
/* STYLES */
import "./styles.css";

//ErrorPage - Renders error page with link back to prelogin screen
const ErrorPage = () => {
  return (
    <div className="__errorpage-container__ w-screen h-screen">
      <div className="__errorpage-header__ w-full flex flex-start pl-5">
        <Link
          className=" text-white cursor-pointer hover:text-green-100 p-4 text-2xl"
          to="/"
        >
          Return Home
        </Link>
      </div>
      <div className="__errorpage-body__ flex w-full h-full justify-center items-center">
        <h1 className="__errorpage-text__ text-white">
          There has been an error, head back toward the{" "}
          <span className="__errorpage-link__">
            {" "}
            <Link className=" text-white cursor-pointer" to="/">
              {" "}
              LIGHT{" "}
            </Link>
          </span>
          .
        </h1>
      </div>
    </div>
  );
};

export default ErrorPage;
