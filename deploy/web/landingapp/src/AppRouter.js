/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { HashRouter, Route, Redirect, Switch } from "react-router-dom";
/* CONFIG */
import CONFIG from "../config.js";

import AboutPage from "./pages/AboutPage";
import LandingPage from "./pages/LandingPage";
import TermsPage from "./pages/TermsPage";
import TutorialPage from "./pages/TutorialPage";
import DevLoginPage from "./pages/DevLoginPage";
import ProdLoginPage from "./pages/ProdLoginPage";
import LogoutPage from "./pages/LogoutPage";
import ErrorPage from "./pages/ErrorPage";

import "./styles.css";

const AppRouter = () => {
  const use_page = CONFIG.login == "fb" ? ProdLoginPage : DevLoginPage;
  return (
    <div className="app-container">
      <HashRouter>
        <Switch>
          <Route path="/" component={LandingPage} exact />
          <Route path="/tutorial" component={TutorialPage} exact />
          <Route path="/about" component={AboutPage} exact />
          <Route path="/terms" component={TermsPage} exact />
          <Route path="/login" component={use_page} exact />
          <Route path="/bye" component={LogoutPage} exact />
          <Route path="/error" component={ErrorPage} exact />
          <Route component={ErrorPage} />
        </Switch>
      </HashRouter>
    </div>
  );
};

export default AppRouter;
