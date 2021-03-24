import React from "react";
import { HashRouter, Route, Redirect } from "react-router-dom";

import AboutPage from "./pages/AboutPage";
import AboutPage2 from "./pages/AboutPage2";
import LandingPage from "./pages/LandingPage";
import LandingPage2 from "./pages/LandingPage2";

import "./styles.css";

export function Routes() {
  return (
    <>
      <Route path="/" component={LandingPage} exact />
      <Route path="/about" component={AboutPage} exact />
      <Route path="/about2" component={AboutPage2} exact />
      <Route path="/2" component={LandingPage2} exact />
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
