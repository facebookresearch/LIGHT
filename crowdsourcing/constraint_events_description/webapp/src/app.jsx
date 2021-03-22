/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import ReactDOM from "react-dom";
import { TaskDescription } from "./components/task_description.jsx";
import { ActionDescription } from "./components/action_description.jsx";
import { ConstraintBlock } from "./components/constraint_element.jsx";
import { EventsBlock } from "./components/event_elements.jsx";
import { LoadingScreen } from "./components/core_components.jsx";
import { useMephistoTask } from "mephisto-task";

/* ================= Application Components ================= */

function MainApp() {
  const {
    blockedReason,
    blockedExplanation,
    isPreview,
    isLoading,
    initialTaskData,
    handleSubmit,
  } = useMephistoTask();

  // const state = initialTaskData;
  const state = {
    'primaryObject': 'big stick',
    'secondaryObject': 'pumpkins',
    'actionDescription': 'You poke at the pumpkins with the big stick. Your stick goes through the pumpkins, indicating that they are rotten.'
  };

  if (blockedReason !== null) {
    return (
      <section className="hero is-medium is-danger">
        <div class="hero-body">
          <h2 className="title is-3">{blockedExplanation}</h2>{" "}
        </div>
      </section>
    );
  }

  if (isPreview) {
    return (
      <div>
        <section className="hero is-medium is-link">
          <div className="hero-body">
            <TaskDescription />
          </div>
        </section>
      </div>
    );
  }

  // Check if initial task data returns null
  if (isLoading || initialTaskData == null) {
    return <LoadingScreen />;
  }

  return (
    <div>
      <section className="hero is-medium is-link">
        <div className="hero-body">
          <TaskDescription />
          <br />
          <br />
          <ActionDescription state={state} />
          <br />
          <ConstraintBlock state={state} />
          <br />
          <EventsBlock state={state} />
        </div>
      </section>
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
