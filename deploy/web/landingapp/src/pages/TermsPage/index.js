/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { Link, useHistory } from "react-router-dom";

import "./styles.css";

const TermsPage = (props) => {
  let history = useHistory();
  return (
    <div className="termspage-container">
      <div className="termspage-body">
        <div style={{ width: "100%", flexDirection: "flexStart" }}>
          <div className="back-button" onClick={() => history.goBack()}>
            Back
          </div>
        </div>
        <h1 className="termspage-header">Terms</h1>
        <div className="termspage-text__container">
          <p>
            Facebook will process the messages you send in playing the game in
            accordance with our Data Policy (
            <a
              style={{ color: "yellow" }}
              href="http://facebook.com/policy"
              target="_blank"
            >
              facebook.com/policy
            </a>
            ). Messages you send in playing the game may be used by Facebook for
            research purposes and as otherwise specified in our Data Policy, and
            may be used by and/or shared with third parties in connection with
            this research.
          </p>
          <p>
            This may involve public disclosure of the messages as part of a
            research paper or data set. We will take measures to remove any
            information that directly identifies you before doing so, but cannot
            guarantee that messages will be completely anonymous. Do not send
            personal information (for example, name, address, email, or phone
            number) in your messages.
          </p>
          <p>
            Facebook's Community Standards apply and you may not use any racist,
            sexist, or otherwise offensive language, or harass other players. If
            you violate our policies you may be reported and blocked.
          </p>
        </div>
      </div>
    </div>
  );
};

export default TermsPage;
