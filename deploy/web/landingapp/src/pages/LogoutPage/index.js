/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* REACT ROUTER */
import { Link } from "react-router-dom";

//LogoutPage - Renders logout page with link back to prelogin screen
const LogoutPage = () => {
  return (
    <div className="__logoutpage-container__ w-screen h-screen">
      <div className="__logoutpage-header__ w-full flex flex-start pl-5">
        <Link
          className="__logoutpage-link__ text-white cursor-pointer hover:text-green-100 p-4 text-2xl"
          to="/"
        >
          Return Home
        </Link>
      </div>
      <div className="__logoutpage-body__ flex w-full h-full justify-center items-center">
        <h1 className="__logoutpage-text__ text-white">
          You are now logged out. Thank you for playing!
        </h1>
      </div>
    </div>
  );
};

export default LogoutPage;
