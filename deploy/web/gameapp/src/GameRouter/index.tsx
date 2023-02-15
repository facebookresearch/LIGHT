/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
//ROUTER COMPONENTS
import { BrowserRouter, Route, Redirect, Switch } from "react-router-dom";
//PAGES
import GamePage from "../pages/GamePage";

// GameRouter - manages routes of react app
const GameRouter = () => {
  return (
    <>
      <BrowserRouter>
        <Switch>
          <Route path="/play" component={GamePage} exact />
        </Switch>
      </BrowserRouter>
    </>
  );
};

export default GameRouter;
