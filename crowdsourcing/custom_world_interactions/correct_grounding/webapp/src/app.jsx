/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */
//REACT
import React from "react";
import ReactDOM from "react-dom";
//MEPHISTO
import { useMephistoTask } from "mephisto-task";
//STYLING
import "./styles.css";
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-tippy/dist/tippy.css'
//CUSTOM COMPONENTS
import Task from "./views/Task";
import Preview from "./views/Preview";
import LoadingScreen from "./components/LoadingScreen";

function MainApp() {
  const {
    blockedReason,
    blockedExplanation,
    isPreview,
    isLoading,
    initialTaskData,
    handleSubmit,
  } = useMephistoTask();


  if (blockedReason !== null) {
    return (
      <section className="hero is-medium is-danger">
        <div className="hero-body">
          <h2 className="title is-3">{blockedExplanation}</h2>{" "}
        </div>
      </section>
    );
  }

  if (isPreview) {
    return (
      <div>
        <Preview />
      </div>
    );
  }

  // Check if initial task data returns null
  if (isLoading || initialTaskData === null || !initialTaskData.primary) {
    return <LoadingScreen />;
  }

  return (
    <div>
      <Task
        data={initialTaskData}
        handleSubmit={handleSubmit}
      />
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
