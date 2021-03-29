import React from "react";
import { HashRouter, Route, Redirect } from "react-router-dom";

import AboutPage from "./pages/AboutPage";
import LandingPage from "./pages/LandingPage";
import TermsPage from "./pages/TermsPage";
import LoginPage from "./pages/LoginPage";
import LogoutPage from "./pages/LogoutPage";

import "./styles.css";

export function Routes() {
  return (
    <>
      <Route path="/" component={LandingPage} exact />
      <Route path="/about" component={AboutPage} exact />
      <Route path="/terms" component={TermsPage} exact />
      <Route path="/login" component={LoginPage} exact />
      <Route path="/logout" component={LogoutPage} exact />
    </>
  );
}

const AppRouter = () => {
  return (
    <div className="app-container">
      <HashRouter>
        <Routes />
      </HashRouter>
    </div>
  );
};

export default AppRouter;
