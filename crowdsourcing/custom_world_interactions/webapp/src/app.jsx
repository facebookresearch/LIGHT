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
              Objects Interactions Annotation Task
            </div>
            <p>We're trying to crowdsource possible interactions between a set of items. These interactions are set in a medieval fantasy, and as such should not refer to real people, places, or modern day technologies. In this task you will receive a main object (Known as the primary object). You will be able to select another object (Target object) from a list of 10 randomly selected objects.</p>
            <p>After that, write a simple interaction between these two objects in the textbox.</p>
            <p>{"\n"}</p>
            <p>For example, let's say we have a fire torch as the primary object and a wooden table as the target object.</p>
            <p>In this case, a good action description would be: "You light the table on fire with the torch. It ignites and burns to the ground, leaving a pile of ash." In general, good descriptions are as follows:</p>
            <div>
            Primary: Rusty key. Target: Bucket. Interaction: You scrape the key on the edge of the bucket. It sounds terrible, and leaves a mark.
            Primary: Towel. Target: Rock. Interaction: You rub the rock with the towel. The rock is now shiny, but the towel could use a cleaning.
            Primary: Rock. Target: Tree. Interaction: You throw the rock at the tree. It hits a branch, and a bird flies away.
            </div>

            <p>Avoid submitting interactions which are physically impossible or nonsense in the current scenario. Interactions must also be written in second person.</p>
            <div>
            Primary: shirt. Target: bucket. Interaction: You put the shirt in the bucket and it transforms into a pair of pants. 
            <b>Bad Reason:</b> This interaction isn't very plausible. Interactions don't need to be expected or mundane, but they should be a realistic occurrence.

            Primary: Ball. Target: Table. Interaction: The ball rolls off of the table and falls on the floor. 
            <b>Bad Reason:</b> This interaction isn't written in second person. The correct format would be "You roll the ball on the table. It falls off of the other side onto the floor"
            </div>
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
            Objects Interactions Annotation Task
          </div>
          <p>Primary Object: {state.primary_object}</p>
          <ObjectSelector objectList={random_object_list} currentSelectedObject={state.secondary_object} onChangeCurrentSelectedObject={onChangeSecondaryObject} />
          <InteractionDescription description={state.action_description} onChangeDescription={onChangeActionDescription} />
          <SubmitButton active={active} state={state} onSubmit={handleSubmit}/>
        </div>
      </section>
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
