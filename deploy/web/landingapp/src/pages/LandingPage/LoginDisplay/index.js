/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

import "./styles.css";

const LoginDisplay = ({ loginStepIncreaseHandler }) => {
  /*--------------- HANDLERS ----------------*/
  const loginHandler = (e) => {
    e.preventDefault();
    loginStepIncreaseHandler();
  };
  return (
    <div>
      <div style={{ justifyContent: "center", marginTop: "8px" }}>
        <button className="login-form__submit" onClick={loginHandler}>
          Sign In With Facebook
        </button>
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
