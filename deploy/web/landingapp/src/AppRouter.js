/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { HashRouter, Route, Redirect, Switch } from "react-router-dom";

import AboutPage from "./pages/AboutPage";
import LandingPage from "./pages/LandingPage";
import TermsPage from "./pages/TermsPage";
import TutorialPage from "./pages/TutorialPage";
import LoginPage from "./pages/LoginPage";
import LogoutPage from "./pages/LogoutPage";
import ErrorPage from "./pages/ErrorPage";

import StarryNight from "./assets/images/light_starry_bg.jpg";

const AppRouter = () => {
  return (
    <div
      style={{
        backgroundImage: `linear-gradient(to bottom, #0f0c2999, #302b63aa, #24243ecc), url(${StarryNight})`,
      }}
      className=" flex h-screen w-screen bg-cover bg-top bg-no-repeat"
    >
      hi.,dfmnaslkfdnaslkdfnasl;kfnjasl;kdnfaslkdnfaks
    </div>
  );
};

export default AppRouter;
