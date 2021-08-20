//REACT
import React from "react";
//ROUTER COMPONENTS
import { HashRouter, Route, Redirect, Switch } from "react-router-dom";
//PAGES
import GamePage from "./pages/GamePage";
import ProfilePage from "./pages/ProfilePage";
//STYLES
import "./styles.css";

// GameRouter - manages routes of react app
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
