/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
import { BrowserRouter, Route, Switch } from "react-router-dom";
/* CONFIG */
import CONFIG from "./config.js";

/* CUSTOM COMPONENTS */
import LandingPage from "./pages/LandingPage";
import TermsPage from "./pages/TermsPage";
import FAQSPage from "./pages/FAQSPage";
import DevLoginPage from "./pages/DevLoginPage";
import LogoutPage from "./pages/LogoutPage";
import ErrorPage from "./pages/ErrorPage";
import PreLoginPage from "./pages/PreLoginPage";
/* IMAGES */
//APP BACKGROUND IMAGE
import StarryNight from "./assets/images/light_starry_bg.jpg";
/* STYLES */
import "./styles.css";

//AppRouter - Renders react-router for app.  Each virtual path renders component page based on URL
const AppRouter = () => {
  const local_login =
    CONFIG.login == "fb" ? null : (
      <Route path="/login" component={DevLoginPage} exact />
    );
  return (
    <div
      style={{
        backgroundImage: `linear-gradient(to bottom, #0f0c2999, #302b63aa, #24243ecc), url(${StarryNight})`,
      }}
      className="__landing-page__ flex h-screen w-screen bg-cover bg-top bg-no-repeat overflow-x-scroll min-w-[75%]"
    >
      <BrowserRouter>
        <Switch>
          <Route path="/" component={PreLoginPage} exact />
          <Route path="/intro" component={LandingPage} exact />
          <Route path="/faq" component={FAQSPage} exact />
          <Route path="/tos" component={TermsPage} exact />
          <Route path="/bye" component={LogoutPage} exact />
          <Route path="/error" component={ErrorPage} exact />
          {local_login}
          <Route component={ErrorPage} />
        </Switch>
      </BrowserRouter>
    </div>
  );
};

export default AppRouter;
