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
import { BaseFrontend, LoadingScreen } from "./components/core_components.jsx";
import { useMephistoTask, ErrorBoundary } from "mephisto-task";
import { ObjectRandomizer } from "./object_randomizer.js";

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

  const objectRandomizer = new ObjectRandomizer();
  const primary_object = objectRandomizer.get_primary_object();
  const random_object_list = objectRandomizer.get_object_list();

  const [secondary_object, onChangeSecondaryObject] = React.useState("");
  const [action_description, onChangeActionDescription] = React.useState("");

  const state = {
    primary_object: primary_object,
    secondary_object: secondary_object,
    action_description: action_description
  }

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
      <div>
        <section className="hero is-medium is-link">
          <div className="hero-body">
            <div className="title is-3">
              Welcome to LIGHT's Custom World Interactions task!
            </div>
            <p>Actor Object: {state.primary_object}</p>
            <ObjectSelector objectList={random_object_list} currentSelectedObject={state.secondary_object} onChangeCurrentSelectedObject={onChangeSecondaryObject} />
            <InteractionDescription description={state.action_description} onChangeDescription={onChangeActionDescription} />
          </div>
        </section>
      </div>
    );
  }

  return (
    <div>
      <ErrorBoundary handleError={handleFatalError}>
        <BaseFrontend
          taskData={initialTaskData}
          onSubmit={handleSubmit}
          isOnboarding={isOnboarding}
          onError={handleFatalError}
        />
      </ErrorBoundary>
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
