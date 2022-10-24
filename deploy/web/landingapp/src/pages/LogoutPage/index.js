/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React from "react";
import { Link } from "react-router-dom";

const LogoutPage = () => {
  return (
    <div className="__logoutpage-container__">
      <div className="__logoutpage-body__">
        <Link className="__logoutpage-link__" to="/">
          Back to Home
        </Link>
      </div>
      <div>
        <h1 className="__logoutpage-text__">
          You are now logged out. Thank you for playing!
        </h1>
      </div>
    </div>
  );
};

export default LogoutPage;
