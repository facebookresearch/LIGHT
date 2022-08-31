/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

import "./styles.css";

const LoginPage = (props) => {
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
        <div
          className="login-form__field"
          style={{ justifyContent: "center", marginTop: "8px" }}
        >
          <form action="/auth/fblogin?next={{next}}" method="get">
            <input
              className="login-form__submit"
              type="submit"
              value="Sign In With Facebook"
            />
          </form>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
