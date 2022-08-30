
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */


import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom";


import {LoadingScreen } from "./components/core_components.jsx";
import { useMephistoTask, ErrorBoundary } from "mephisto-task";

/* ================= Container Components ================= */
import Preview from "./Views/Preview";
import Task1 from "./Views/Task1";

/* ================= Application Components ================= */

function MainApp() {

  const [primaryObject, setPrimaryObject] = React.useState("");
  const [secondaryObject, setSecondaryObject] = React.useState("");
  const [actionDescription, setActionDescription] = React.useState("");
  const [rawAction, setRawAction] = React.useState("");
  const [otherActive, setOtherActive] = React.useState(false);

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
        <div className="hero-body">
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

  const payload = {
    primaryObject,
    secondaryObject,
    actionDescription,
    rawAction,
  };

  const active =
    payload.rawAction.length > 0 &&
    payload.actionDescription.length > 0 &&
    payload.secondaryObject.length > 0 &&
    payload.primaryObject.length > 0;

  return (
    <>
      <ErrorBoundary handleError={handleFatalError}>
        <Task1
          actionDescription={actionDescription}
          taskData={initialTaskData}
          setPrimaryObject={setPrimaryObject}
          setSecondaryObject={setSecondaryObject}
          setActionDescription={setActionDescription}
          setRawAction={setRawAction}
          setOtherActive={setOtherActive}
          onSubmit={handleSubmit}
          isOnboarding={isOnboarding}
          onError={handleFatalError}
          payload={payload}
          active={active}
        />
      </ErrorBoundary>
    </>
  )
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
