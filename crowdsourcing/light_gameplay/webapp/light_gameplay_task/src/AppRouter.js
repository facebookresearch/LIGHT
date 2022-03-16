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
