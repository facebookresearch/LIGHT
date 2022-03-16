/* REACT */
import React from "react";
//ROUTER COMPONENTS
import { HashRouter, Route, Redirect, Routes } from "react-router-dom";
//VIEWS
import Task from "./Views/Task"
import Onboarding from "./Views/OnboardingView"

// GameRouter - manages routes of react app
const AppRouter = () => {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Onboarding/>} exact />
        <Route path="/task" element={<Task/>} exact />
      </Routes>
    </HashRouter>
  );
};

export default AppRouter;
