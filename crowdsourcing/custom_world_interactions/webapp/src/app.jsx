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
import { TaskDescription } from "./components/task_description.jsx"
import { LoadingScreen } from "./components/core_components.jsx";
import { useMephistoTask } from "mephisto-task";
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
  } = useMephistoTask();

  const [primaryObject, onChangePrimaryObject] = React.useState("");
  const [secondaryObject, onChangeSecondaryObject] = React.useState("");
  const [actionDescription, onChangeActionDescription] = React.useState("");
  const [otherActive, onChangeOtherActive] = React.useState(false);

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

  const primaryObjectList = initialTaskData["primary_object_list"];
  const secondaryObjectList = initialTaskData["secondary_object_list"];

  const state = {
    primaryObject: primaryObject,
    secondaryObject: secondaryObject,
    actionDescription: actionDescription
  }

  const active = state.actionDescription.length > 0 && state.secondaryObject.length > 0 && state.primaryObject.length > 0;

  return (
    <div>
      <section className="hero is-medium is-link">
        <div className="hero-body">
          <TaskDescription />
          <br />
          <br />
          <ObjectSelector 
            primaryObjectList={primaryObjectList} secondaryObjectList={secondaryObjectList}
            onChangeCurrentPrimaryObject={onChangePrimaryObject} onChangeCurrentSecondaryObject={onChangeSecondaryObject}
            otherActive={otherActive} onChangeOtherActive={onChangeOtherActive}
          />
          <br />
          <br />
          <p><b>Your current selected action is:</b><i>"Use {state.primaryObject} with {state.secondaryObject}"</i></p>
          <InteractionDescription description={state.actionDescription} onChangeDescription={onChangeActionDescription} />
          <br />
          <SubmitButton active={active} state={state} onSubmit={handleSubmit}/>
        </div>
      </section>
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
