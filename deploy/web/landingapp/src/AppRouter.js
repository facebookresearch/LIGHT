/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
import { HashRouter, Route, Redirect, Switch } from "react-router-dom";
/* CUSTOM COMPONENTS */
import AboutPage from "./pages/AboutPage";
import LandingPage from "./pages/LandingPage";
import TermsPage from "./pages/TermsPage";
import FAQSPage from "./pages/FAQSPage";
import LogoutPage from "./pages/LogoutPage";
import ErrorPage from "./pages/ErrorPage";
import PreLoginPage from "./pages/PreLoginPage";
/* IMAGES */
import StarryNight from "./assets/images/light_starry_bg.jpg";
/* STYLES */
import "./styles.css";

const AppRouter = () => {
  return (
    <div
      style={{
        backgroundImage: `linear-gradient(to bottom, #0f0c2999, #302b63aa, #24243ecc), url(${StarryNight})`,
      }}
      className="__landing-page__ flex h-screen w-screen bg-cover bg-top bg-no-repeat"
    >
      <HashRouter>
        <Switch>
          <Route path="/" component={PreLoginPage} exact />
          <Route path="/intro" component={LandingPage} exact />
          <Route path="/faqs" component={FAQSPage} exact />
          <Route path="/about" component={AboutPage} exact />
          <Route path="/terms" component={TermsPage} exact />
          <Route path="/bye" component={LogoutPage} exact />
          <Route path="/error" component={ErrorPage} exact />
          <Route component={ErrorPage} />
        </Switch>
      </HashRouter>
    </div>
  );
};

export default AppRouter;
