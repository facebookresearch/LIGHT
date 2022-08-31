/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { Link } from "react-router-dom";

import "./styles.css";

const ErrorPage = (props) => {
  return (
    <div className="errorpage-container">
      <div className="errorpage-body">
        <div
          style={{
            width: "100%",
            flexDirection: "flexStart",
            paddingLeft: "20px",
          }}
        >
          <Link style={{ textDecoration: "none", color: "yellow" }} to="/">
            Return Home
          </Link>
        </div>
        <h1 style={{ color: "white", textAlign: "center" }}>
          Oops, looks like there's a web issue
        </h1>
      </div>
    </div>
  );
};

export default ErrorPage;
