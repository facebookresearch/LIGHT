/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import ReactDOM from "react-dom";
import { ObjectSelector } from "./components/object_selector.jsx";
import { InteractionDescription } from "./components/interaction_description.jsx";
import { LoadingScreen } from "./components/core_components.jsx";
import { useMephistoTask, ErrorBoundary } from "mephisto-task";
import { SubmitButton } from './components/submit_button.jsx'

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
  } = useMephistoTask();

  const [secondary_object, onChangeSecondaryObject] = React.useState("");
  const [action_description, onChangeActionDescription] = React.useState("");

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
            <div className="title is-3">
              Welcome to LIGHT's Custom World Interactions task!
            </div>
            <p>In this task you will receive a main object (Known as the actor object). You will be able to select another object (Target object) from a list of 10 randomly selected objects.</p>
            <p>After that, write a simple interaction between these two objects in the textbox.</p>
            <p>{"\n"}</p>
            <p>For example, let's say we have a fire torch as an actor object and a wooden table as a target object.</p>
            <p>In this case, a good action description would be: "The fire torch burns the wooden table."</p>
          </div>
        </section>
      </div>
    );
  }

  // Check if initial task data returns null
  if (isLoading || initialTaskData == null) {
    return <LoadingScreen />;
  }

  const primary_object = initialTaskData["primary_object"];
  const random_object_list = initialTaskData["secondary_object_list"];

  const state = {
    primary_object: primary_object,
    secondary_object: secondary_object,
    action_description: action_description
  }

  const active = state.action_description.length > 0 && state.secondary_object.length > 0;

  return (
    <div>
      <section className="hero is-medium is-link">
        <div className="hero-body">
          <div className="title is-3">
            Welcome to LIGHT's Custom World Interactions task!
          </div>
          <p>Actor Object: {state.primary_object}</p>
          <ObjectSelector objectList={random_object_list} currentSelectedObject={state.secondary_object} onChangeCurrentSelectedObject={onChangeSecondaryObject} />
          <InteractionDescription description={state.action_description} onChangeDescription={onChangeActionDescription} />
          <SubmitButton active={active} state={state} onSubmit={handleSubmit}/>
        </div>
      </section>
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
