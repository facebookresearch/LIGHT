/* REACT */
import React from "react";
//ROUTER COMPONENTS
import { HashRouter, Route, Redirect, Switch } from "react-router-dom";
//PAGES
import GamePage from "../pages/GamePage";

// GameRouter - manages routes of react app
const GameRouter = () => {
  return (
    <HashRouter>
      <Switch>
        <Route path="/" component={GamePage} exact />
        <Route path="/_=_" component={GamePage} exact />
      </Switch>
    </HashRouter>
  );
};

export default GameRouter;
