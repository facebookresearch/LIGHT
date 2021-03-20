import React from "react";
import { HashRouter, Route, Redirect } from "react-router-dom";


import AboutPage from "./pages/AboutPage";
import LandingPage from "./pages/LandingPage";
import GamePage from "./pages/GamePage";

import "./styles.css"


export function Routes() {
  return (
    <>
    
        <Route path="/" component={LandingPage} exact />
        <Route path="/play" component={GamePage} exact />
        <Route path="/about" component={AboutPage} exact />
      
    </>
  );
}

const AppRouter = ()=>{
    return (
      <div className="app-container">
        <HashRouter>
          <Routes />
        </HashRouter>
      </div>
    );
  }

export default AppRouter;