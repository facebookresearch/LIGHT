import React from "react";
import { HashRouter, Route, Redirect, Switch } from "react-router-dom";

import AboutPage from "./pages/AboutPage";
import LandingPage from "./pages/LandingPage";
import TermsPage from "./pages/TermsPage";
import LoginPage from "./pages/LoginPage";
import LogoutPage from "./pages/LogoutPage";
import ErrorPage from "./pages/ErrorPage";

import "./styles.css";

const AppRouter = () => {
  return (
    <div className="app-container">
      <HashRouter>
        <Switch>
          <Route path="/" component={LandingPage} exact />
          <Route path="/about" component={AboutPage} exact />
          <Route path="/terms" component={TermsPage} exact />
          <Route path="/login" component={LoginPage} exact />
          <Route path="/bye" component={LogoutPage} exact />
          <Route path="/error" component={ErrorPage} exact />
          <Route component={ErrorPage} />
        </Switch>
      </HashRouter>
    </div>
  );
};

export default AppRouter;
