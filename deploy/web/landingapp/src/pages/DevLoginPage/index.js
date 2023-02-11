/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";


const DevLoginPage = (props) => {
  return (
    <div className="loginpage-container">
      <div className="login-form__container">
        <h1 style={{ color: "white" }}>Login</h1>
        <form action="/login?next={{next}}" method="post">
          <div className="login-form__field ">
            <p className="login-form__label">Name</p>
            <input className="login-form__input" type="text" name="name" />
          </div>
          <div className="login-form__field ">
            <p className="login-form__label">Password</p>
            <input className="login-form__input" type="text" name="password" />
          </div>
          <div
            className="login-form__field"
            style={{ justifyContent: "center" }}
          >
            <input
              className="login-form__submit"
              type="submit"
              value="Sign in"
            />
          </div>
        </form>
      </div>
    </div>
  );
};

export default DevLoginPage;
