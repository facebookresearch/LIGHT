/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */


import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom";


import {LoadingScreen } from "./components/LoadingScreen";
import { useMephistoTask, ErrorBoundary } from "mephisto-task";

/* ================= Container Components ================= */
import Preview from "./Views/Preview";
import Task from "./Views/Task";
/* ================= Styles ================= */
import 'bootstrap/dist/css/bootstrap.min.css';

/* ================= Application Components ================= */

function MainApp() {


  const {
    blockedReason,
    blockedExplanation,
    isPreview,
    isLoading,
    initialTaskData,
    handleSubmit,
    handleFatalError,
    isOnboarding,
    loaded
  } = useMephistoTask();

  if (blockedReason !== null) {
    return (
      <section className="hero is-medium is-danger">
        <div class="hero-body">
          <h2 className="title is-3">{blockedExplanation}</h2>{" "}
        </div>
      </section>
    );
  }
  if (isLoading) {
    return <LoadingScreen />;
  }
  if (isPreview) {
    return (
      <Preview/>
    );
  }
  const DummyData = {
    111:"I used my broadsword to slay a minotaur last week.",
    222:"May I have your credit card info?",
    333:"I had a drink at the Prancing Horse Inn last week.",
    444:"Where do you live?",
  }

  return (
    <>
      <ErrorBoundary handleError={handleFatalError}>
        <Task
          data={DummyData}
        />
      </ErrorBoundary>
    </>
  )
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
