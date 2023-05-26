/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

import "./styles.css";

const ProdLoginPage = (props) => {
  return (
    <div className="loginpage-container">
      <div className="login-form__container">
        <h1 style={{ color: "white" }}>Login</h1>
        <p>
          We use Facebook Login as an identity provider, however we do not store
          any information about you or your Facebook account. By logging in you
          agree to our <a href="/#/terms">terms</a> and you accept our use of
          cookies to mark you as logged in as you navigate the site.
        </p>
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

export default ProdLoginPage;
