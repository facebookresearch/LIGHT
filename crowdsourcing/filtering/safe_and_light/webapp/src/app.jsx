/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import ReactDOM from "react-dom";
import { BaseFrontend, LoadingScreen, DescInstructions } from "./components/core_components.jsx";
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
    isOnboarding,
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
      <section className="hero is-medium is-link">
        <div class="hero-body">
          <div className="title is-3">
            This is a sentence rating task for a medieval fantasy text adventure setting.
          </div>
          <div className="subtitle is-4">
            Inside you'll be given 10 sentences to rate as to whether or not they're an appropriate or 
            inappropriate thing to say, as well as whether or not they make sense in a medieval fantasy
            setting. Examples below.
          </div>
          {<DescInstructions/>}
        </div>
      </section>
    );
  }

  return (
    <div>
      <BaseFrontend
        taskData={initialTaskData}
        onSubmit={handleSubmit}
        isOnboarding={isOnboarding}
      />
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
