
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
//ROUTER COMPONENTS
import { HashRouter, Route, Routes } from "react-router-dom";
//VIEWS
import Task from "./Views/Task"

// GameRouter - manages routes of react app
const AppRouter = () => {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Task/>} exact />
      </Routes>
    </HashRouter>
  );
};

export default AppRouter;
