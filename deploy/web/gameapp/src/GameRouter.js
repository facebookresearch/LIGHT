import React from "react";
import { HashRouter, Route, Redirect, Switch } from "react-router-dom";

import GamePage from "./pages/GamePage";
import ProfilePage from "./pages/ProfilePage";

import "./styles.css";

const GameRouter = () => {
  return (
    <div className="app-container">
      <HashRouter>
        <Switch>
          <Route path="/" component={GamePage} exact />
          <Route path="/_=_" component={GamePage} exact />
          <Route path="/profile" component={ProfilePage} exact />
        </Switch>
      </HashRouter>
    </div>
  );
};

export default GameRouter;
